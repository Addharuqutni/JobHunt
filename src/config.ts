// Centralized API configuration
// Uses Vite environment variable VITE_API_URL, falls back to localhost for development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = API_BASE_URL.replace(/^http/, 'ws');
export const API_KEY = import.meta.env.VITE_API_KEY || 'dev-secret-key-123';

export const getHeaders = () => ({
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
});

// API endpoint helpers
export const API = {
    jobs: (params?: { limit?: number; source?: string; search?: string }) => {
        const url = new URL(`${API_BASE_URL}/api/jobs`);
        if (params?.limit) url.searchParams.set('limit', String(params.limit));
        if (params?.source) url.searchParams.set('source', params.source);
        if (params?.search) url.searchParams.set('search', params.search);
        return url.toString();
    },
    stats: () => `${API_BASE_URL}/api/stats`,
    scrape: () => `${API_BASE_URL}/api/scrape`,
    settings: () => `${API_BASE_URL}/api/settings`,
    wsScrapeStatus: () => `${WS_URL}/api/ws/scrape-status?api_key=${API_KEY}`,
};
