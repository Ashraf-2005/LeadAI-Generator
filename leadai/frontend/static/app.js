/**
 * LeadAI Frontend JavaScript
 * Shared utilities and API client
 */

// API Configuration
const API_BASE = window.location.port === '8000' || window.location.port === '' || window.location.port === '80'
    ? '/api'
    : 'http://localhost:8000/api';

// Auth: Login
async function loginUser(username, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Login failed' }));
        throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
}

// Auth: Register
async function registerUser(username, password) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
        throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
}

// API Client with automatic token attachment
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/';
    }

    return response;
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Utility: Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy:', err);
        return false;
    }
}

// Utility: Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-4 py-3 rounded-lg text-white z-50 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        'bg-blue-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Alert helper used by login.html (showAlert)
function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    if (!container) {
        showToast(message, type);
        return;
    }
    container.innerHTML = `
        <div class="alert alert-${type === 'error' ? 'error' : 'success'}" style="
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            border-radius: 6px;
            background: ${type === 'error' ? '#fee2e2' : '#dcfce7'};
            color: ${type === 'error' ? '#991b1b' : '#166534'};
        ">
            ${message}
        </div>
    `;
}

// Theme toggle (light/dark)
function initTheme() {
    const isDark = localStorage.getItem('theme') === 'dark';
    if (isDark) {
        document.documentElement.classList.add('dark');
    }
}

function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
});
