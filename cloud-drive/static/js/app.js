/* ══════════════════════════════════════════════════════════
   CloudDrive — Frontend Application
   ══════════════════════════════════════════════════════════ */

const API = '';
let token = localStorage.getItem('token');
let currentFolder = null;
let contextTarget = null;
let isListView = localStorage.getItem('viewMode') === 'list';
const isMobile = () => window.matchMedia('(max-width:768px)').matches;
const isTouch = () => 'ontouchstart' in window;

const $ = id => document.getElementById(id);

// DOM cache
const dom = {
    authScreen:   $('auth-screen'),
    appScreen:    $('app-screen'),
    authForm:     $('auth-form'),
    authBtn:      $('auth-btn'),
    authToggle:   $('auth-toggle'),
    authError:    $('auth-error'),
    authUser:     $('auth-username'),
    authPass:     $('auth-password'),
    grid:         $('file-grid'),
    empty:        $('empty-state'),
    loading:      $('loading'),
    ctx:          $('context-menu'),
    sheetBackdrop:$('bottom-sheet-backdrop'),
    sheet:        $('bottom-sheet'),
    renameModal:  $('rename-modal'),
    renameInput:  $('rename-input'),
    folderModal:  $('folder-modal'),
    folderInput:  $('folder-name-input'),
    deleteModal:  $('delete-modal'),
    previewModal: $('preview-modal'),
    fabMain:      $('fab-main'),
    fabMenu:      $('fab-menu'),
    fabGroup:     $('fab-group'),
    fileInput:    $('file-input'),
    toasts:       $('toast-container'),
};

let isLogin = true;
let renameTarget = null;
let deleteTarget = null;

/* ══════════════════════════════════════════════════════════
   TOAST NOTIFICATIONS
   ══════════════════════════════════════════════════════════ */
const ICONS = { success:'fa-check-circle', error:'fa-exclamation-circle', info:'fa-info-circle' };
function toast(msg, type='info') {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `<i class="fas ${ICONS[type]||ICONS.info}"></i><span>${esc(msg)}</span>`;
    dom.toasts.appendChild(el);
    const timer = setTimeout(() => {
        el.classList.add('out');
        setTimeout(() => el.remove(), 300);
    }, 3500);
    el.addEventListener('click', () => { clearTimeout(timer); el.remove(); });
}

function esc(s) { const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

/* ══════════════════════════════════════════════════════════
   API HELPER
   ══════════════════════════════════════════════════════════ */
async function api(url, opts={}) {
    if (token) opts.headers = { ...opts.headers, Authorization: `Bearer ${token}` };
    const res = await fetch(API + url, opts);
    if (res.status === 401) {
        token = null; localStorage.removeItem('token');
        dom.authScreen.classList.remove('hidden');
        dom.appScreen.classList.add('hidden');
        throw new Error('Sesión expirada');
    }
    if (!res.ok) {
        const b = await res.json().catch(()=>({}));
        throw new Error(b.detail || `Error ${res.status}`);
    }
    return res;
}

/* ══════════════════════════════════════════════════════════
   AUTH
   ══════════════════════════════════════════════════════════ */
dom.authToggle.addEventListener('click', () => {
    isLogin = !isLogin;
    dom.authBtn.querySelector('span').textContent = isLogin ? 'Iniciar sesión' : 'Registrarse';
    dom.authToggle.textContent = isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión';
    dom.authError.classList.add('hidden');
});

dom.authForm.addEventListener('submit', async e => {
    e.preventDefault();
    dom.authError.classList.add('hidden');
    const username = dom.authUser.value.trim();
    const password = dom.authPass.value;
    if (!username || !password) return;

    dom.authBtn.disabled = true;
    dom.authBtn.querySelector('span').textContent = isLogin ? 'Entrando...' : 'Creando cuenta...';

    try {
        if (!isLogin) {
            await api('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            toast('Cuenta creada', 'success');
        }
        const form = new URLSearchParams();
        form.append('username', username);
        form.append('password', password);
        const res = await api('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: form,
        });
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        enterApp();
    } catch (err) {
        dom.authError.textContent = err.message;
        dom.authError.classList.remove('hidden');
    } finally {
        dom.authBtn.disabled = false;
        dom.authBtn.querySelector('span').textContent = isLogin ? 'Iniciar sesión' : 'Registrarse';
    }
});

$('logout-btn').addEventListener('click', () => {
    token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    dom.authScreen.classList.remove('hidden');
    dom.appScreen.classList.add('hidden');
    dom.authUser.value = '';
    dom.authPass.value = '';
    toast('Sesión cerrada', 'info');
});

/* ══════════════════════════════════════════════════════════
   APP INIT
   ══════════════════════════════════════════════════════════ */
function enterApp() {
    dom.authScreen.classList.add('hidden');
    dom.appScreen.classList.remove('hidden');
    $('user-name').textContent = localStorage.getItem('username') || '';
    updateFabVisibility();
    applyViewMode();
    loadFolder(null);
}

if (token) enterApp();

function updateFabVisibility() {
    if (isMobile()) dom.fabGroup.style.display = 'flex';
    else dom.fabGroup.style.display = 'none';
}
window.addEventListener('resize', () => { if (token) updateFabVisibility(); });

/* ══════════════════════════════════════════════════════════
   VIEW TOGGLE
   ══════════════════════════════════════════════════════════ */
function applyViewMode() {
    const icon = $('btn-view-toggle').querySelector('i');
    if (isListView) {
        dom.grid.classList.add('list-view');
        icon.className = 'fas fa-th-large';
    } else {
        dom.grid.classList.remove('list-view');
        icon.className = 'fas fa-list';
    }
}

$('btn-view-toggle').addEventListener('click', () => {
    isListView = !isListView;
    localStorage.setItem('viewMode', isListView ? 'list' : 'grid');
    applyViewMode();
});

/* ══════════════════════════════════════════════════════════
   FOLDER NAVIGATION
   ══════════════════════════════════════════════════════════ */
async function loadFolder(folderId) {
    currentFolder = folderId;
    dom.grid.innerHTML = '';
    dom.empty.classList.add('hidden');
    dom.loading.classList.remove('hidden');

    try {
        const url = folderId ? `/api/files/browse?folder_id=${folderId}` : '/api/files/browse';
        const res = await api(url);
        const data = await res.json();

        renderBreadcrumb(data.breadcrumb);
        renderStorage(data.storage_used, data.storage_limit);

        dom.loading.classList.add('hidden');

        if (!data.folders.length && !data.files.length) {
            dom.empty.classList.remove('hidden');
            return;
        }

        const frag = document.createDocumentFragment();
        data.folders.forEach(f => frag.appendChild(makeFolder(f)));
        data.files.forEach(f => frag.appendChild(makeFile(f)));
        dom.grid.appendChild(frag);
    } catch (err) {
        dom.loading.classList.add('hidden');
        if (!err.message.includes('expirada')) toast('Error: ' + err.message, 'error');
    }
}

function renderBreadcrumb(crumbs) {
    const bc = $('breadcrumb');
    bc.innerHTML = '';

    const home = mkBtn('crumb-btn' + (!crumbs.length ? ' active' : ''), '<i class="fas fa-home"></i><span>Inicio</span>');
    home.addEventListener('click', () => loadFolder(null));
    bc.appendChild(home);

    crumbs.forEach((c, i) => {
        const sep = document.createElement('span');
        sep.className = 'crumb-sep';
        sep.textContent = '/';
        bc.appendChild(sep);

        const btn = mkBtn('crumb-btn' + (i === crumbs.length - 1 ? ' active' : ''), `<span>${esc(c.name)}</span>`);
        btn.addEventListener('click', () => loadFolder(c.id));
        bc.appendChild(btn);
    });

    requestAnimationFrame(() => { bc.scrollLeft = bc.scrollWidth; });
}

function mkBtn(cls, html) {
    const b = document.createElement('button');
    b.className = cls;
    b.innerHTML = html;
    return b;
}

function renderStorage(used, limit) {
    const pct = limit > 0 ? (used / limit) * 100 : 0;
    const fill = $('storage-fill');
    fill.style.width = Math.min(pct, 100) + '%';
    if (pct > 90) fill.style.background = 'var(--danger)';
    else if (pct > 70) fill.style.background = 'var(--warning)';
    else fill.style.background = 'var(--primary)';
    $('storage-text').textContent = `${fmtSize(used)} / ${fmtSize(limit)}`;
}

function fmtSize(b) {
    if (!b) return '0 B';
    const u = ['B','KB','MB','GB','TB'];
    const i = Math.floor(Math.log(b) / Math.log(1024));
    return parseFloat((b / Math.pow(1024, i)).toFixed(1)) + ' ' + u[i];
}

/* ══════════════════════════════════════════════════════════
   FILE / FOLDER ITEMS
   ══════════════════════════════════════════════════════════ */
function fileIcon(mime) {
    if (!mime) return { i:'fa-file', c:'default' };
    if (mime.startsWith('image/'))  return { i:'fa-file-image',  c:'image' };
    if (mime.startsWith('video/'))  return { i:'fa-file-video',  c:'video' };
    if (mime.startsWith('audio/'))  return { i:'fa-file-audio',  c:'audio' };
    if (mime === 'application/pdf') return { i:'fa-file-pdf',    c:'pdf' };
    if (/zip|rar|tar|7z/.test(mime))return { i:'fa-file-archive',c:'archive' };
    if (/word|document/.test(mime)) return { i:'fa-file-word',   c:'doc' };
    if (/sheet|excel/.test(mime))   return { i:'fa-file-excel',  c:'doc' };
    if (/present|power/.test(mime)) return { i:'fa-file-powerpoint', c:'doc' };
    if (/json|javascript|python|html|css|xml/.test(mime)) return { i:'fa-file-code', c:'code' };
    return { i:'fa-file', c:'default' };
}

function makeFolder(f) {
    const el = document.createElement('div');
    el.className = 'file-item';
    el.innerHTML = `<i class="fas fa-folder icon folder"></i><span class="name" title="${esc(f.name)}">${esc(f.name)}</span>`;

    // Use a click-delay approach: single tap = open, long press = menu
    let clickTimer = null;
    el.addEventListener('click', e => {
        // On desktop, single click opens; on mobile too (long press is for menu)
        if (clickTimer) return;
        clickTimer = setTimeout(() => { clickTimer = null; loadFolder(f.id); }, 0);
    });

    el.addEventListener('contextmenu', e => {
        e.preventDefault();
        openMenu(e, 'folder', f);
    });

    addLongPress(el, 'folder', f);
    return el;
}

function makeFile(f) {
    const {i: icon, c: cls} = fileIcon(f.mime_type);
    const isImg = f.mime_type && f.mime_type.startsWith('image/');
    const el = document.createElement('div');
    el.className = 'file-item';
    el.innerHTML = `
        <i class="fas ${icon} icon ${cls}"></i>
        <span class="name" title="${esc(f.original_name)}">${esc(f.original_name)}</span>
        <span class="meta">${fmtSize(f.size)}</span>`;

    let clickTimer = null;
    el.addEventListener('click', () => {
        if (clickTimer) return;
        clickTimer = setTimeout(() => {
            clickTimer = null;
            if (isImg) showPreview(f); else downloadFile(f.id, f.original_name);
        }, 0);
    });

    el.addEventListener('dblclick', e => e.preventDefault());

    el.addEventListener('contextmenu', e => {
        e.preventDefault();
        openMenu(e, 'file', f);
    });

    addLongPress(el, 'file', f);
    return el;
}

/* ══════════════════════════════════════════════════════════
   LONG PRESS (Mobile)
   ══════════════════════════════════════════════════════════ */
function addLongPress(el, type, item) {
    let timer = null, moved = false;

    el.addEventListener('touchstart', e => {
        moved = false;
        timer = setTimeout(() => {
            if (!moved) {
                e.preventDefault();
                // Prevent the click from firing
                el.style.pointerEvents = 'none';
                setTimeout(() => { el.style.pointerEvents = ''; }, 300);
                if (navigator.vibrate) navigator.vibrate(25);
                openSheet(type, item);
            }
        }, 450);
    }, { passive: false });

    el.addEventListener('touchmove', () => { moved = true; clearTimeout(timer); });
    el.addEventListener('touchend', () => clearTimeout(timer));
    el.addEventListener('touchcancel', () => clearTimeout(timer));
}

/* ══════════════════════════════════════════════════════════
   MENUS
   ══════════════════════════════════════════════════════════ */
function openMenu(e, type, item) {
    if (isMobile() || isTouch()) {
        openSheet(type, item);
        return;
    }
    contextTarget = { type, item };

    // Show/hide relevant buttons
    const openBtn = dom.ctx.querySelector('[data-action="open"]');
    const previewBtn = dom.ctx.querySelector('[data-action="preview"]');
    const dlBtn = dom.ctx.querySelector('[data-action="download"]');
    const isImg = type === 'file' && item.mime_type && item.mime_type.startsWith('image/');

    openBtn.style.display = type === 'folder' ? '' : 'none';
    previewBtn.style.display = isImg ? '' : 'none';
    dlBtn.style.display = type === 'folder' ? 'none' : '';

    dom.ctx.classList.remove('hidden');
    dom.ctx.style.left = Math.min(e.clientX, window.innerWidth - 220) + 'px';
    dom.ctx.style.top = Math.min(e.clientY, window.innerHeight - 220) + 'px';
}

document.addEventListener('click', e => {
    if (!dom.ctx.contains(e.target)) dom.ctx.classList.add('hidden');
});

dom.ctx.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
        dom.ctx.classList.add('hidden');
        if (contextTarget) doAction(btn.dataset.action, contextTarget.type, contextTarget.item);
    });
});

/* ── Bottom Sheet ──────────────────────────── */
function openSheet(type, item) {
    contextTarget = { type, item };
    const {i: icon} = type === 'folder' ? {i:'fa-folder'} : fileIcon(item.mime_type);
    const name = type === 'folder' ? item.name : item.original_name;

    $('bs-icon').className = `fas ${icon}`;
    $('bs-icon').style.color = type === 'folder' ? '#fbbf24' : 'var(--text-2)';
    $('bs-name').textContent = name;
    $('bs-meta').textContent = type === 'file' ? fmtSize(item.size) : 'Carpeta';

    // Show/hide relevant buttons
    const openBtn = dom.sheet.querySelector('[data-action="open"]');
    const previewBtn = dom.sheet.querySelector('[data-action="preview"]');
    const dlBtn = dom.sheet.querySelector('[data-action="download"]');
    const isImg = type === 'file' && item.mime_type && item.mime_type.startsWith('image/');

    openBtn.style.display = type === 'folder' ? '' : 'none';
    previewBtn.style.display = isImg ? '' : 'none';
    dlBtn.style.display = type === 'folder' ? 'none' : '';

    dom.sheetBackdrop.classList.remove('hidden');
    dom.sheet.classList.remove('hidden');
}

function closeSheet() {
    dom.sheetBackdrop.classList.add('hidden');
    dom.sheet.classList.add('hidden');
}

dom.sheetBackdrop.addEventListener('click', closeSheet);

dom.sheet.querySelectorAll('.sheet-actions button').forEach(btn => {
    btn.addEventListener('click', () => {
        closeSheet();
        if (contextTarget) doAction(btn.dataset.action, contextTarget.type, contextTarget.item);
    });
});

/* ══════════════════════════════════════════════════════════
   ACTIONS
   ══════════════════════════════════════════════════════════ */
function doAction(action, type, item) {
    switch (action) {
        case 'open':     loadFolder(item.id); break;
        case 'preview':  showPreview(item); break;
        case 'download': downloadFile(item.id, item.original_name); break;
        case 'rename':   openRenameModal(type, item); break;
        case 'delete':   openDeleteModal(type, item); break;
    }
}

// ── Download ──
async function downloadFile(id, name) {
    toast('Descargando...', 'info');
    try {
        const res = await api(`/api/files/download/${id}`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = name;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast('Descarga completada', 'success');
    } catch (err) {
        toast('Error: ' + err.message, 'error');
    }
}

// ── Preview ──
async function showPreview(item) {
    if (!item.mime_type?.startsWith('image/')) return;
    dom.previewModal.classList.remove('hidden');
    const img = $('preview-img');
    img.src = '';
    $('preview-name').textContent = item.original_name;
    $('preview-size').textContent = fmtSize(item.size);

    try {
        const res = await api(`/api/files/download/${item.id}`);
        const blob = await res.blob();
        img.src = URL.createObjectURL(blob);
    } catch (err) {
        toast('Error al cargar preview', 'error');
        dom.previewModal.classList.add('hidden');
    }
}

function closePreview() {
    dom.previewModal.classList.add('hidden');
    const img = $('preview-img');
    if (img.src.startsWith('blob:')) URL.revokeObjectURL(img.src);
    img.src = '';
}

$('preview-close').addEventListener('click', e => { e.stopPropagation(); closePreview(); });
dom.previewModal.addEventListener('click', e => {
    if (e.target === dom.previewModal || !e.target.closest('.preview-body')) closePreview();
});

// ── Rename ──
function openRenameModal(type, item) {
    renameTarget = { type, item };
    dom.renameInput.value = type === 'folder' ? item.name : item.original_name;
    dom.renameModal.classList.remove('hidden');
    setTimeout(() => { dom.renameInput.focus(); dom.renameInput.select(); }, 100);
}

$('rename-cancel').addEventListener('click', () => dom.renameModal.classList.add('hidden'));
$('rename-confirm').addEventListener('click', async () => {
    if (!renameTarget) return;
    const name = dom.renameInput.value.trim();
    if (!name) return;
    try {
        await api(`/api/files/rename/${renameTarget.type}/${renameTarget.item.id}?name=${encodeURIComponent(name)}`, { method:'PUT' });
        dom.renameModal.classList.add('hidden');
        toast('Renombrado', 'success');
        loadFolder(currentFolder);
    } catch (err) { toast(err.message, 'error'); }
});
dom.renameInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') $('rename-confirm').click();
    if (e.key === 'Escape') dom.renameModal.classList.add('hidden');
});
dom.renameModal.addEventListener('click', e => { if (e.target === dom.renameModal) dom.renameModal.classList.add('hidden'); });

// ── Delete ──
function openDeleteModal(type, item) {
    deleteTarget = { type, item };
    const name = type === 'folder' ? item.name : item.original_name;
    $('delete-msg').textContent = `¿Eliminar "${name}"?` + (type === 'folder' ? ' Todos los archivos dentro serán eliminados.' : '');
    dom.deleteModal.classList.remove('hidden');
}

$('delete-cancel').addEventListener('click', () => dom.deleteModal.classList.add('hidden'));
$('delete-confirm').addEventListener('click', async () => {
    if (!deleteTarget) return;
    const { type, item } = deleteTarget;
    const endpoint = type === 'folder' ? `/api/files/folder/${item.id}` : `/api/files/file/${item.id}`;
    try {
        await api(endpoint, { method:'DELETE' });
        dom.deleteModal.classList.add('hidden');
        toast('Eliminado', 'success');
        loadFolder(currentFolder);
    } catch (err) { toast(err.message, 'error'); }
});
dom.deleteModal.addEventListener('click', e => { if (e.target === dom.deleteModal) dom.deleteModal.classList.add('hidden'); });

// ── New Folder ──
$('btn-new-folder').addEventListener('click', () => openFolderModal());
$('fab-folder').addEventListener('click', () => { closeFab(); openFolderModal(); });

function openFolderModal() {
    dom.folderInput.value = '';
    dom.folderModal.classList.remove('hidden');
    setTimeout(() => dom.folderInput.focus(), 100);
}

$('folder-cancel').addEventListener('click', () => dom.folderModal.classList.add('hidden'));
$('folder-confirm').addEventListener('click', async () => {
    const name = dom.folderInput.value.trim();
    if (!name) return;
    try {
        await api('/api/files/folder', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ name, parent_id: currentFolder }),
        });
        dom.folderModal.classList.add('hidden');
        toast('Carpeta creada', 'success');
        loadFolder(currentFolder);
    } catch (err) { toast(err.message, 'error'); }
});
dom.folderInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') $('folder-confirm').click();
    if (e.key === 'Escape') dom.folderModal.classList.add('hidden');
});
dom.folderModal.addEventListener('click', e => { if (e.target === dom.folderModal) dom.folderModal.classList.add('hidden'); });

/* ══════════════════════════════════════════════════════════
   FAB MENU
   ══════════════════════════════════════════════════════════ */
let fabOpen = false;

dom.fabMain.addEventListener('click', () => {
    fabOpen = !fabOpen;
    dom.fabMain.classList.toggle('open', fabOpen);
    dom.fabMenu.classList.toggle('hidden', !fabOpen);
});

function closeFab() {
    fabOpen = false;
    dom.fabMain.classList.remove('open');
    dom.fabMenu.classList.add('hidden');
}

// Close fab on outside click
document.addEventListener('click', e => {
    if (fabOpen && !dom.fabGroup.contains(e.target)) closeFab();
});

/* ══════════════════════════════════════════════════════════
   UPLOAD
   ══════════════════════════════════════════════════════════ */
$('btn-upload').addEventListener('click', () => dom.fileInput.click());
$('fab-upload').addEventListener('click', () => { closeFab(); dom.fileInput.click(); });

dom.fileInput.addEventListener('change', () => {
    if (dom.fileInput.files.length) uploadFiles(dom.fileInput.files);
    dom.fileInput.value = '';
});

async function uploadFiles(fileList) {
    const progress = $('upload-progress');
    const status = $('upload-status');
    const fill = $('progress-fill');
    const n = fileList.length;
    const total = Array.from(fileList).reduce((a, f) => a + f.size, 0);

    progress.classList.remove('hidden');
    status.textContent = `Subiendo ${n} archivo${n > 1 ? 's' : ''} (${fmtSize(total)})...`;
    fill.style.width = '3%';
    fill.style.background = 'var(--primary)';

    const fd = new FormData();
    for (const f of fileList) fd.append('files', f);

    let url = '/api/files/upload';
    if (currentFolder) url += `?folder_id=${currentFolder}`;

    try {
        await new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.upload.addEventListener('progress', e => {
                if (e.lengthComputable) {
                    const pct = Math.round((e.loaded / e.total) * 100);
                    fill.style.width = pct + '%';
                    status.textContent = `Subiendo... ${pct}%`;
                }
            });
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) resolve();
                else {
                    try { reject(new Error(JSON.parse(xhr.responseText).detail)); }
                    catch { reject(new Error(`Error ${xhr.status}`)); }
                }
            });
            xhr.addEventListener('error', () => reject(new Error('Error de red')));
            xhr.open('POST', API + url);
            if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);
            xhr.send(fd);
        });

        fill.style.width = '100%';
        status.textContent = 'Completado';
        toast(`${n} archivo${n > 1 ? 's' : ''} subido${n > 1 ? 's' : ''}`, 'success');
        setTimeout(() => progress.classList.add('hidden'), 2000);
        loadFolder(currentFolder);
    } catch (err) {
        status.textContent = 'Error';
        fill.style.background = 'var(--danger)';
        toast('Error: ' + err.message, 'error');
        setTimeout(() => { progress.classList.add('hidden'); fill.style.background = ''; }, 3000);
    }
}

/* ══════════════════════════════════════════════════════════
   DRAG & DROP
   ══════════════════════════════════════════════════════════ */
const dropOverlay = $('drop-overlay');
let dragCount = 0;

document.addEventListener('dragenter', e => { e.preventDefault(); dragCount++; if (token) dropOverlay.classList.remove('hidden'); });
document.addEventListener('dragleave', e => { e.preventDefault(); dragCount--; if (dragCount <= 0) { dropOverlay.classList.add('hidden'); dragCount = 0; } });
document.addEventListener('dragover', e => e.preventDefault());
document.addEventListener('drop', e => {
    e.preventDefault(); dragCount = 0; dropOverlay.classList.add('hidden');
    if (e.dataTransfer.files.length && token) uploadFiles(e.dataTransfer.files);
});

/* ══════════════════════════════════════════════════════════
   KEYBOARD
   ══════════════════════════════════════════════════════════ */
document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (!dom.previewModal.classList.contains('hidden')) return closePreview();
    if (!dom.deleteModal.classList.contains('hidden')) return dom.deleteModal.classList.add('hidden');
    if (!dom.renameModal.classList.contains('hidden')) return dom.renameModal.classList.add('hidden');
    if (!dom.folderModal.classList.contains('hidden')) return dom.folderModal.classList.add('hidden');
    if (!dom.sheet.classList.contains('hidden')) return closeSheet();
    dom.ctx.classList.add('hidden');
    closeFab();
});
