import uuid
import mimetypes
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import User, File as FileModel, Folder
from app.schemas import FolderCreate, FolderResponse, FileResponse, FolderContents
from app.auth import get_current_user
from app.storage import upload_file, download_file, delete_file, delete_files, get_presigned_url
from app.config import MAX_FILE_SIZE
import io

router = APIRouter(prefix="/api/files", tags=["files"])

STORAGE_LIMIT = 10 * 1024 * 1024 * 1024  # 10GB


def get_storage_used(db: Session, user_id) -> int:
    result = db.query(func.coalesce(func.sum(FileModel.size), 0)).filter(
        FileModel.user_id == user_id
    ).scalar()
    return int(result)


def build_breadcrumb(db: Session, folder_id, user_id) -> list:
    crumbs = []
    current = folder_id
    while current:
        folder = db.query(Folder).filter(Folder.id == current, Folder.user_id == user_id).first()
        if not folder:
            break
        crumbs.insert(0, folder)
        current = folder.parent_id
    return crumbs


@router.get("/browse", response_model=FolderContents)
def browse(
    folder_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    fid = uuid.UUID(folder_id) if folder_id else None
    current_folder = None
    if fid:
        current_folder = db.query(Folder).filter(Folder.id == fid, Folder.user_id == user.id).first()
        if not current_folder:
            raise HTTPException(404, "Carpeta no encontrada")

    folders = db.query(Folder).filter(
        Folder.user_id == user.id, Folder.parent_id == fid
    ).order_by(Folder.name).all()

    files = db.query(FileModel).filter(
        FileModel.user_id == user.id, FileModel.folder_id == fid
    ).order_by(FileModel.original_name).all()

    breadcrumb = build_breadcrumb(db, fid, user.id) if fid else []

    return FolderContents(
        current_folder=current_folder,
        breadcrumb=breadcrumb,
        folders=folders,
        files=files,
        storage_used=get_storage_used(db, user.id),
        storage_limit=STORAGE_LIMIT,
    )


@router.post("/folder", response_model=FolderResponse, status_code=201)
def create_folder(
    data: FolderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.parent_id:
        parent = db.query(Folder).filter(Folder.id == data.parent_id, Folder.user_id == user.id).first()
        if not parent:
            raise HTTPException(404, "Carpeta padre no encontrada")

    existing = db.query(Folder).filter(
        Folder.user_id == user.id,
        Folder.parent_id == data.parent_id,
        Folder.name == data.name,
    ).first()
    if existing:
        raise HTTPException(409, "Ya existe una carpeta con ese nombre aquí")

    folder = Folder(name=data.name, parent_id=data.parent_id, user_id=user.id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.post("/upload", response_model=list[FileResponse], status_code=201)
async def upload_files(
    files: list[UploadFile] = File(...),
    folder_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    fid = uuid.UUID(folder_id) if folder_id else None
    if fid:
        folder = db.query(Folder).filter(Folder.id == fid, Folder.user_id == user.id).first()
        if not folder:
            raise HTTPException(404, "Carpeta no encontrada")

    storage_used = get_storage_used(db, user.id)
    uploaded = []

    for f in files:
        content = await f.read()
        size = len(content)

        if size > MAX_FILE_SIZE:
            raise HTTPException(413, f"'{f.filename}' excede el límite de 100MB por archivo")
        if storage_used + size > STORAGE_LIMIT:
            raise HTTPException(507, "Sin espacio. Has alcanzado el límite de 10GB")

        mime = f.content_type or mimetypes.guess_type(f.filename)[0] or "application/octet-stream"
        r2_key = f"{user.id}/{uuid.uuid4()}/{f.filename}"

        upload_file(r2_key, content, mime)

        file_record = FileModel(
            original_name=f.filename,
            r2_key=r2_key,
            size=size,
            mime_type=mime,
            folder_id=fid,
            user_id=user.id,
        )
        db.add(file_record)
        storage_used += size
        uploaded.append(file_record)

    db.commit()
    for file_record in uploaded:
        db.refresh(file_record)
    return uploaded


@router.get("/download/{file_id}")
def download(file_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(FileModel).filter(FileModel.id == file_id, FileModel.user_id == user.id).first()
    if not f:
        raise HTTPException(404, "Archivo no encontrado")

    data = download_file(f.r2_key)
    return StreamingResponse(
        io.BytesIO(data),
        media_type=f.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{f.original_name}"'},
    )


@router.delete("/file/{file_id}", status_code=204)
def delete_file_endpoint(file_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(FileModel).filter(FileModel.id == file_id, FileModel.user_id == user.id).first()
    if not f:
        raise HTTPException(404, "Archivo no encontrado")

    delete_file(f.r2_key)
    db.delete(f)
    db.commit()


def collect_folder_keys(db: Session, folder_id, user_id) -> list[str]:
    keys = []
    files = db.query(FileModel).filter(FileModel.folder_id == folder_id, FileModel.user_id == user_id).all()
    keys.extend([f.r2_key for f in files])
    subfolders = db.query(Folder).filter(Folder.parent_id == folder_id, Folder.user_id == user_id).all()
    for sf in subfolders:
        keys.extend(collect_folder_keys(db, sf.id, user_id))
    return keys


@router.delete("/folder/{folder_id}", status_code=204)
def delete_folder(folder_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.user_id == user.id).first()
    if not folder:
        raise HTTPException(404, "Carpeta no encontrada")

    keys = collect_folder_keys(db, folder.id, user.id)
    if keys:
        for i in range(0, len(keys), 1000):
            delete_files(keys[i:i + 1000])

    db.delete(folder)
    db.commit()


@router.put("/rename/{item_type}/{item_id}")
def rename_item(
    item_type: str,
    item_id: str,
    name: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if item_type == "folder":
        item = db.query(Folder).filter(Folder.id == item_id, Folder.user_id == user.id).first()
    elif item_type == "file":
        item = db.query(FileModel).filter(FileModel.id == item_id, FileModel.user_id == user.id).first()
    else:
        raise HTTPException(400, "Tipo inválido")

    if not item:
        raise HTTPException(404, "No encontrado")

    if item_type == "folder":
        item.name = name
    else:
        item.original_name = name

    db.commit()
    return {"ok": True}
