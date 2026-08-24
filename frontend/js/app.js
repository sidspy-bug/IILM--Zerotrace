/* ================================================================
   ForensicRecover — Application Core
   API Client • Auth • Router • UI Helpers • Chart.js Integration
   ================================================================ */

// ── API Client ──
const API = {
  baseUrl: '',
  token: localStorage.getItem('fr_token'),

  headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  },

  async request(method, url, body = null) {
    const opts = { method, headers: this.headers() };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${this.baseUrl}${url}`, opts);
    if (res.status === 401) {
      Auth.logout();
      return null;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || 'Request failed');
    }
    if (res.headers.get('content-type')?.includes('application/json')) {
      return res.json();
    }
    return res;
  },

  get(url) { return this.request('GET', url); },
  post(url, body) { return this.request('POST', url, body); },
  put(url, body) { return this.request('PUT', url, body); },
  patch(url, body) { return this.request('PATCH', url, body); },

  async downloadPdf(url, filename) {
    try {
      const res = await fetch(`${this.baseUrl}${url}`, {
        method: 'GET',
        headers: this.headers(),
      });
      if (res.status === 401) { Auth.logout(); return; }
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Download failed' }));
        throw new Error(err.detail || 'Download failed');
      }
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = filename || 'report.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      Toast.error('Download failed: ' + err.message);
    }
  },

  async login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },
};

// ── Auth Manager ──
const Auth = {
  user: JSON.parse(localStorage.getItem('fr_user') || 'null'),

  setSession(token, user) {
    API.token = token;
    this.user = user;
    localStorage.setItem('fr_token', token);
    localStorage.setItem('fr_user', JSON.stringify(user));
  },

  logout() {
    API.token = null;
    this.user = null;
    localStorage.removeItem('fr_token');
    localStorage.removeItem('fr_user');
    window.location.href = '/';
  },

  isLoggedIn() {
    return !!API.token && !!this.user;
  },

  getInitials() {
    if (!this.user?.name) return '?';
    return this.user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  },
};

// ── Toast Notifications ──
const Toast = {
  container: null,

  init() {
    if (!document.querySelector('.toast-container')) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    } else {
      this.container = document.querySelector('.toast-container');
    }
  },

  show(message, type = 'info') {
    if (!this.container) this.init();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-message">${message}</span>`;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg) { this.show(msg, 'error'); },
  warning(msg) { this.show(msg, 'warning'); },
  info(msg) { this.show(msg, 'info'); },
};

// ── UI Helpers ──
const UI = {
  // Sidebar active state
  setActivePage(page) {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.page === page);
    });
  },

  // Update user info in sidebar
  updateUserInfo() {
    const nameEl = document.querySelector('.user-name');
    const roleEl = document.querySelector('.user-role');
    const avatarEl = document.querySelector('.user-avatar');
    if (nameEl) nameEl.textContent = Auth.user?.name || 'User';
    if (roleEl) roleEl.textContent = Auth.user?.role || 'VIEWER';
    if (avatarEl) avatarEl.textContent = Auth.getInitials();
  },

  // Format date
  formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  },

  // Format file size
  formatSize(bytes) {
    if (!bytes) return '—';
    if (bytes > 1048576) return `${(bytes / 1048576).toFixed(1)} MB`;
    if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${bytes} B`;
  },

  // Status badge HTML
  badge(status) {
    const map = {
      'ACTIVE': 'active', 'CLOSED': 'closed', 'PENDING': 'pending',
      'REGISTERED': 'indigo', 'ACQUIRED': 'active', 'ANALYZING': 'pending',
      'RECOVERED': 'recovered', 'IN_PROGRESS': 'in-progress',
      'COMPLETED': 'completed', 'VERIFIED': 'verified',
      'INTEGRITY_MISMATCH': 'mismatch', 'FULLY_RECOVERED': 'recovered',
      'PARTIALLY_RECOVERED': 'partial', 'NOT_RECOVERABLE': 'failed',
      'CORRUPTED': 'alert', 'UNKNOWN': 'unknown', 'GENERATED': 'completed',
      'HIGH': 'recovered', 'MEDIUM': 'pending', 'LOW': 'alert', 'UNCERTAIN': 'unknown',
    };
    const cls = map[status] || 'unknown';
    return `<span class="badge badge-${cls}">${status}</span>`;
  },

  // Show/hide modal
  openModal(id) {
    document.getElementById(id)?.classList.add('active');
  },

  closeModal(id) {
    document.getElementById(id)?.classList.remove('active');
  },

  // Loading skeleton
  showSkeleton(container, count = 3) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += '<div class="skeleton skeleton-card mb-4"></div>';
    }
    container.innerHTML = html;
  },

  // Empty state
  emptyState(message, sub = '') {
    return `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
        </svg>
        <h3>${message}</h3>
        ${sub ? `<p>${sub}</p>` : ''}
      </div>
    `;
  },
};

// ── SVG Icons ──
const Icons = {
  shield: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12.99H5V8.26l7-3.89v8.62z"/></svg>`,
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  cases: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`,
  evidence: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
  recovery: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>`,
  integrity: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  custody: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  reports: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>`,
  logout: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
  plus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
  check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`,
  alert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
  download: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
  search: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
};

// ── Sidebar Template ──
function renderSidebar(activePage) {
  return `
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">${Icons.shield}</div>
        <div>
          <h2>ForensicRecover</h2>
          <span>Investigation Platform</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-label">Main</div>
          <a href="/dashboard" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}" data-page="dashboard">
            ${Icons.dashboard} <span>Dashboard</span>
          </a>
        </div>

        <div class="nav-section">
          <div class="nav-section-label">Investigation</div>
          <a href="/cases" class="nav-item ${activePage === 'cases' ? 'active' : ''}" data-page="cases">
            ${Icons.cases} <span>Cases</span>
          </a>
          <a href="/evidence" class="nav-item ${activePage === 'evidence' ? 'active' : ''}" data-page="evidence">
            ${Icons.evidence} <span>Evidence</span>
          </a>
          <a href="/recovery" class="nav-item ${activePage === 'recovery' ? 'active' : ''}" data-page="recovery">
            ${Icons.recovery} <span>Recovery</span>
          </a>
        </div>

        <div class="nav-section">
          <div class="nav-section-label">Verification</div>
          <a href="/custody" class="nav-item ${activePage === 'custody' ? 'active' : ''}" data-page="custody">
            ${Icons.custody} <span>Chain of Custody</span>
          </a>
          <a href="/reports" class="nav-item ${activePage === 'reports' ? 'active' : ''}" data-page="reports">
            ${Icons.reports} <span>Reports</span>
          </a>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">${Auth.getInitials()}</div>
          <div class="user-details">
            <div class="user-name">${Auth.user?.name || 'User'}</div>
            <div class="user-role">${Auth.user?.role || 'VIEWER'}</div>
          </div>
          <button class="btn-icon" onclick="Auth.logout()" title="Logout">
            ${Icons.logout}
          </button>
        </div>
      </div>
    </aside>
  `;
}

// ── Chart Colors ──
const ChartColors = {
  indigo: 'rgba(79, 70, 229, 0.8)',
  emerald: 'rgba(16, 185, 129, 0.8)',
  amber: 'rgba(245, 158, 11, 0.8)',
  red: 'rgba(239, 68, 68, 0.8)',
  slate: 'rgba(100, 116, 139, 0.8)',
  sky: 'rgba(14, 165, 233, 0.8)',
  indigo_light: 'rgba(79, 70, 229, 0.1)',
  emerald_light: 'rgba(16, 185, 129, 0.1)',
  amber_light: 'rgba(245, 158, 11, 0.1)',
  red_light: 'rgba(239, 68, 68, 0.1)',
};

// ── Guard: redirect to login if not authenticated ──
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = '/';
    return false;
  }
  return true;
}

// ── Initialize Toast ──
document.addEventListener('DOMContentLoaded', () => {
  Toast.init();
});
