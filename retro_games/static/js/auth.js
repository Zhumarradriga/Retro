async function fetchWithAuth(url, options) {
    options.headers = {
        ...options.headers,
        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
        'X-CSRFToken': getCookie('csrftoken')
    };
    let response = await fetch(url, options);
    if (response.status === 401) {
        const newToken = await refreshToken();
        if (newToken) {
            options.headers['Authorization'] = 'Bearer ' + newToken;
            response = await fetch(url, options);
        }
    }
    return response;
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        alert('Session expired. Please log in again.');
        window.location.href = '/login/';
        return null;
    }
    try {
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        if (!response.ok) throw new Error('Refresh failed');
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        return data.access;
    } catch (error) {
        alert('Session expired. Please log in again.');
        window.location.href = '/login/';
        return null;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}