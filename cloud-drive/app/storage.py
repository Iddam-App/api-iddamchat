import os
from app.config import R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, STORAGE_MODE, LOCAL_STORAGE_PATH


# ── Local filesystem storage ──────────────────────────────
def _local_path(key: str) -> str:
    path = os.path.join(LOCAL_STORAGE_PATH, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _local_upload(key: str, data: bytes, content_type: str = None):
    path = _local_path(key)
    with open(path, "wb") as f:
        f.write(data)


def _local_download(key: str) -> bytes:
    path = _local_path(key)
    with open(path, "rb") as f:
        return f.read()


def _local_delete(key: str):
    path = _local_path(key)
    if os.path.exists(path):
        os.remove(path)


def _local_delete_many(keys: list[str]):
    for key in keys:
        _local_delete(key)


# ── R2/S3 storage ─────────────────────────────────────────
def get_s3_client():
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def _r2_upload(key: str, data: bytes, content_type: str = None):
    client = get_s3_client()
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    client.put_object(Bucket=R2_BUCKET_NAME, Key=key, Body=data, **extra)


def _r2_download(key: str) -> bytes:
    client = get_s3_client()
    response = client.get_object(Bucket=R2_BUCKET_NAME, Key=key)
    return response["Body"].read()


def _r2_delete(key: str):
    client = get_s3_client()
    client.delete_object(Bucket=R2_BUCKET_NAME, Key=key)


def _r2_delete_many(keys: list[str]):
    if not keys:
        return
    client = get_s3_client()
    objects = [{"Key": k} for k in keys]
    client.delete_objects(Bucket=R2_BUCKET_NAME, Delete={"Objects": objects})


def _r2_presigned(key: str, expires: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": R2_BUCKET_NAME, "Key": key},
        ExpiresIn=expires,
    )


# ── Public API (auto-selects storage backend) ─────────────
def upload_file(key: str, data: bytes, content_type: str = None):
    if STORAGE_MODE == "local":
        _local_upload(key, data, content_type)
    else:
        _r2_upload(key, data, content_type)


def download_file(key: str) -> bytes:
    if STORAGE_MODE == "local":
        return _local_download(key)
    else:
        return _r2_download(key)


def delete_file(key: str):
    if STORAGE_MODE == "local":
        _local_delete(key)
    else:
        _r2_delete(key)


def delete_files(keys: list[str]):
    if STORAGE_MODE == "local":
        _local_delete_many(keys)
    else:
        _r2_delete_many(keys)


def get_presigned_url(key: str, expires: int = 3600) -> str:
    if STORAGE_MODE == "local":
        return f"/uploads/{key}"
    else:
        return _r2_presigned(key, expires)
