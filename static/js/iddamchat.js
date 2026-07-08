/* ═══════════════════════════════════════════════════════════════════
   IddamChat — Shared JavaScript
   ═══════════════════════════════════════════════════════════════════ */

const API = '';
const REACTIONS = {like:'👍', love:'❤️', pray:'🙏', amen:'🙌', fire:'🔥'};

// ─── Auth Helpers ─────────────────────────────────────────
function getToken() { return localStorage.getItem('access_token'); }
function isLoggedIn() { return !!getToken(); }

async function authFetch(url, opts = {}) {
    // Build headers, preserving any already-set headers
    if (!opts.headers) opts.headers = {};
    opts.headers['Authorization'] = 'Bearer ' + getToken();
    // Only set Content-Type for non-FormData bodies
    if (!(opts.body instanceof FormData)) {
        if (!opts.headers['Content-Type']) {
            opts.headers['Content-Type'] = 'application/json';
        }
    } else {
        // Ensure Content-Type is NOT set for FormData (browser sets boundary)
        delete opts.headers['Content-Type'];
    }

    let res;
    try {
        res = await fetch(API + url, opts);
    } catch (e) {
        console.error('authFetch network error:', e);
        throw e;
    }

    if (res.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            logout();
            return res;
        }
        try {
            const refreshRes = await fetch(API + '/api/auth/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });
            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('access_token', data.access);
                if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                opts.headers['Authorization'] = 'Bearer ' + data.access;
                res = await fetch(API + url, opts);
            } else {
                logout();
                return res;
            }
        } catch (e) {
            console.error('Token refresh failed:', e);
            logout();
            return res;
        }
    }
    return res;
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    window.location.href = '/login/';
}

// ─── Upload with Progress (uses XHR for upload.onprogress) ───
function uploadWithProgress(url, formData, onProgress, method) {
    method = method || 'POST';
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method, API + url);
        xhr.setRequestHeader('Authorization', 'Bearer ' + getToken());

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable && onProgress) {
                onProgress(Math.round((e.loaded / e.total) * 100));
            }
        };

        xhr.onload = () => {
            if (xhr.status === 401) {
                // Token expired — refresh and retry once
                fetch(API + '/api/auth/token/refresh/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
                }).then(r => {
                    if (!r.ok) throw new Error('Refresh failed');
                    return r.json();
                }).then(data => {
                    localStorage.setItem('access_token', data.access);
                    if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                    const xhr2 = new XMLHttpRequest();
                    xhr2.open(method, API + url);
                    xhr2.setRequestHeader('Authorization', 'Bearer ' + data.access);
                    xhr2.upload.onprogress = xhr.upload.onprogress;
                    xhr2.onload = () => resolve({
                        status: xhr2.status,
                        ok: xhr2.status >= 200 && xhr2.status < 300,
                        json: () => JSON.parse(xhr2.responseText),
                    });
                    xhr2.onerror = () => reject(new Error('Network error'));
                    xhr2.send(formData);
                }).catch(() => { logout(); reject(new Error('Auth failed')); });
            } else {
                resolve({
                    status: xhr.status,
                    ok: xhr.status >= 200 && xhr.status < 300,
                    json: () => JSON.parse(xhr.responseText),
                });
            }
        };

        xhr.onerror = () => reject(new Error('Network error'));
        xhr.send(formData);
    });
}

// ─── Upload Progress Bar Helper ──────────────────────────
function showUploadProgress(containerId) {
    const bar = document.getElementById(containerId);
    if (!bar) return;
    bar.style.display = 'block';
    const fill = bar.querySelector('.upload-progress-fill');
    const text = bar.querySelector('.upload-progress-text');
    if (fill) fill.style.width = '0%';
    if (text) text.textContent = '0%';
}

function updateUploadProgress(containerId, percent) {
    const bar = document.getElementById(containerId);
    if (!bar) return;
    const fill = bar.querySelector('.upload-progress-fill');
    const text = bar.querySelector('.upload-progress-text');
    if (fill) fill.style.width = percent + '%';
    if (text) text.textContent = percent + '%';
}

function hideUploadProgress(containerId) {
    const bar = document.getElementById(containerId);
    if (!bar) return;
    bar.style.display = 'none';
}

// ─── Utilities ────────────────────────────────────────────
function formatTimeAgo(dateStr) {
    if (!dateStr) return '';
    const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
    if (isNaN(diff)) return '';
    if (diff < 60) return 'Ahora';
    if (diff < 3600) return Math.floor(diff / 60) + ' min';
    if (diff < 86400) return Math.floor(diff / 3600) + ' h';
    if (diff < 604800) return Math.floor(diff / 86400) + ' d';
    return new Date(dateStr).toLocaleDateString('es');
}

function escapeHtml(text) {
    if (!text) return '';
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function showToast(message) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast-iddam';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(8px)';
        setTimeout(() => toast.remove(), 300);
    }, 2700);
}

// ─── Post Card Rendering ─────────────────────────────────
function renderPostCard(post, opts = {}) {
    const author = post.author || {};
    const initial = (author.first_name || author.username || '?')[0].toUpperCase();
    const avatarHtml = author.avatar
        ? `<img src="${author.avatar}" alt="">`
        : initial;
    const displayName = author.display_name || author.first_name || author.username;
    const timeAgo = formatTimeAgo(post.created_at);
    const me = JSON.parse(localStorage.getItem('user_data') || '{}');
    const isMe = me.id === author.id;

    let imagesHtml = '';
    if (post.images && post.images.length > 0) {
        if (post.images.length === 1) {
            imagesHtml = `<div class="post-card-images"><img src="${post.images[0].image}" alt="" loading="lazy"></div>`;
        } else {
            const gridClass = post.images.length >= 3 ? 'grid-3' : 'grid-2';
            const imgs = post.images.slice(0, 4).map(i => `<img src="${i.image}" alt="" loading="lazy">`).join('');
            imagesHtml = `<div class="post-card-images"><div class="image-grid ${gridClass}">${imgs}</div></div>`;
        }
    }

    const reactionEmoji = post.my_reaction ? REACTIONS[post.my_reaction] || '👍' : '';
    const likedClass = post.my_reaction ? 'liked' : '';

    let menuHtml = '';
    if (isMe) {
        const hiddenLabel = post.is_hidden ? 'Mostrar' : 'Ocultar';
        menuHtml = `
        <div class="post-dropdown">
            <div class="post-menu" onclick="toggleMenu(this)"><i class="bi bi-three-dots"></i></div>
            <div class="post-dropdown-menu">
                <button onclick="toggleHidePost(${post.id})"><i class="bi bi-eye-slash"></i> ${hiddenLabel}</button>
                <button class="text-danger" onclick="deletePost(${post.id})"><i class="bi bi-trash"></i> Eliminar</button>
            </div>
        </div>`;
    }

    const hiddenBadge = post.is_hidden ? '<span class="meta-badge ms-2" style="font-size:0.68rem; opacity:0.7;">Oculto</span>' : '';
    const typeLabel = opts.showType && post.post_type === 'hobby' ? '<span class="meta-badge ms-2" style="font-size:0.68rem;">Hobby</span>' : '';
    const timeExtra = opts.showTypeInline && post.post_type === 'hobby' ? ' · Hobby' : '';

    // Comment button: link vs focus
    let commentBtn;
    if (opts.commentFocus) {
        commentBtn = `<button class="action-btn" onclick="document.getElementById('comment-input').focus()" style="flex:1;">
            <i class="bi bi-chat"></i><span>Comentar</span>
        </button>`;
    } else {
        commentBtn = `<a href="/post/${post.id}/" class="action-btn" style="flex:1; text-decoration:none;">
            <i class="bi bi-chat"></i><span>Comentar</span>
        </a>`;
    }

    return `
    <div class="post-card" id="post-${post.id}" style="${post.is_hidden ? 'opacity:0.5;' : ''}">
        <div class="post-card-header">
            <a href="/profile/${author.id}/" class="avatar-sm">${avatarHtml}</a>
            <div class="author-info">
                <a href="/profile/${author.id}/" class="author-name">${escapeHtml(displayName)}</a>${hiddenBadge}${typeLabel}
                <div class="post-time">${timeAgo}${timeExtra}</div>
            </div>
            ${menuHtml}
        </div>
        <div class="post-card-body">
            ${post.title ? `<div class="post-title">${escapeHtml(post.title)}</div>` : ''}
            <div class="post-text">${escapeHtml(post.content)}</div>
        </div>
        ${imagesHtml}
        <div class="post-card-stats">
            <div class="reactions-count">
                ${post.reaction_count > 0 ? '👍 ' + post.reaction_count : ''}
            </div>
            <div>
                ${post.comment_count > 0 ? post.comment_count + ' comentario' + (post.comment_count > 1 ? 's' : '') : ''}
            </div>
        </div>
        <div class="post-card-actions">
            <div style="position:relative; flex:1; display:flex;">
                <div class="reaction-picker" id="picker-${post.id}">
                    ${Object.entries(REACTIONS).map(([k,v]) => `<button onclick="react(${post.id},'${k}')" title="${k}">${v}</button>`).join('')}
                </div>
                <button class="action-btn ${likedClass}" style="flex:1;" onclick="react(${post.id},'like')" onmouseenter="showPicker(${post.id})" onmouseleave="hidePicker(${post.id})" data-reaction="${post.my_reaction || ''}">
                    <i class="bi ${post.my_reaction ? 'bi-hand-thumbs-up-fill' : 'bi-hand-thumbs-up'}"></i>
                    <span>${reactionEmoji || 'Me gusta'}</span>
                </button>
            </div>
            ${commentBtn}
            <button class="action-btn" onclick="savePost(${post.id})" style="flex:1;" data-action="save">
                <i class="bi ${post.is_saved ? 'bi-bookmark-fill' : 'bi-bookmark'}"></i>
                <span>${post.is_saved ? 'Guardado' : 'Guardar'}</span>
            </button>
        </div>
    </div>`;
}

// ─── Reactions ────────────────────────────────────────────
let pickerTimeout;
function showPicker(postId) {
    clearTimeout(pickerTimeout);
    const el = document.getElementById('picker-' + postId);
    if (el) el.classList.add('show');
}
function hidePicker(postId) {
    pickerTimeout = setTimeout(() => {
        const el = document.getElementById('picker-' + postId);
        if (el) el.classList.remove('show');
    }, 300);
}

async function react(postId, type) {
    hidePicker(postId);
    const card = document.getElementById('post-' + postId);
    if (!card) return;
    const btn = card.querySelector('.action-btn[data-reaction]');
    if (!btn) return;
    const current = btn.dataset.reaction;

    try {
        if (current === type) {
            const res = await authFetch(`/api/posts/${postId}/react/`, { method: 'DELETE' });
            if (res.ok || res.status === 204) {
                btn.dataset.reaction = '';
                btn.classList.remove('liked');
                btn.querySelector('i').className = 'bi bi-hand-thumbs-up';
                btn.querySelector('span').textContent = 'Me gusta';
            }
        } else {
            const res = await authFetch(`/api/posts/${postId}/react/`, {
                method: 'POST',
                body: JSON.stringify({ reaction_type: type })
            });
            if (res.ok) {
                btn.dataset.reaction = type;
                btn.classList.add('liked');
                btn.querySelector('i').className = 'bi bi-hand-thumbs-up-fill';
                btn.querySelector('span').textContent = REACTIONS[type];
            }
        }
    } catch(e) {
        showToast('Error de conexion');
    }
}

// ─── Save Post ────────────────────────────────────────────
async function savePost(postId) {
    try {
        const res = await authFetch(`/api/posts/${postId}/save/`, { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            const card = document.getElementById('post-' + postId);
            if (!card) return;
            const saveBtn = card.querySelector('.action-btn[data-action="save"]');
            if (saveBtn) {
                saveBtn.querySelector('i').className = data.saved ? 'bi bi-bookmark-fill' : 'bi bi-bookmark';
                saveBtn.querySelector('span').textContent = data.saved ? 'Guardado' : 'Guardar';
            }
            showToast(data.saved ? 'Publicacion guardada' : 'Removida de guardados');
        }
    } catch(e) {
        showToast('Error de conexion');
    }
}

// ─── Post Menu ────────────────────────────────────────────
function toggleMenu(el) {
    const menu = el.nextElementSibling;
    document.querySelectorAll('.post-dropdown-menu.show').forEach(m => {
        if (m !== menu) m.classList.remove('show');
    });
    menu.classList.toggle('show');
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.post-dropdown')) {
        document.querySelectorAll('.post-dropdown-menu.show').forEach(m => m.classList.remove('show'));
    }
});

async function toggleHidePost(postId) {
    try {
        const res = await authFetch(`/api/posts/${postId}/hide/`, { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            const card = document.getElementById('post-' + postId);
            if (card) card.style.opacity = data.is_hidden ? '0.5' : '1';
            showToast(data.is_hidden ? 'Publicacion oculta' : 'Publicacion visible');
        }
    } catch(e) {
        showToast('Error de conexion');
    }
}

async function deletePost(postId) {
    if (!window.confirm('Seguro que deseas eliminar esta publicacion?')) return;
    try {
        const res = await authFetch(`/api/posts/${postId}/`, { method: 'DELETE' });
        if (res.ok || res.status === 204) {
            const card = document.getElementById('post-' + postId);
            if (card) {
                card.style.transition = 'opacity 0.3s, transform 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'translateY(-8px)';
                setTimeout(() => card.remove(), 300);
            }
            showToast('Publicacion eliminada');
        }
    } catch(e) {
        showToast('Error de conexion');
    }
}
