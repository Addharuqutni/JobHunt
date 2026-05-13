/**
 * Centralized API configuration.
 * Single source of truth for base URLs, headers, and endpoint builders.
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = API_BASE_URL.replace(/^http/, 'ws');

const apiKey = import.meta.env.VITE_API_KEY;

if (!apiKey && import.meta.env.PROD) {
    throw new Error('[JobSentinel] VITE_API_KEY environment variable is required in production.');
}

export const API_KEY = apiKey ?? '';



/**
 * API endpoint builders — constructs full URLs with query parameters.
 */
export const API = {
    jobs: (params?: {
        limit?: number;
        source?: string;
        search?: string;
        job_type?: string;
        work_model?: string;
        experience_level?: string;
    }) => {
        const url = new URL(`${API_BASE_URL}/api/jobs`);
        if (params?.limit) url.searchParams.set('limit', String(params.limit));
        if (params?.source) url.searchParams.set('source', params.source);
        if (params?.search) url.searchParams.set('search', params.search);
        if (params?.job_type) url.searchParams.set('job_type', params.job_type);
        if (params?.work_model) url.searchParams.set('work_model', params.work_model);
        if (params?.experience_level) url.searchParams.set('experience_level', params.experience_level);
        return url.toString();
    },
    stats: () => `${API_BASE_URL}/api/stats`,
    scrape: () => `${API_BASE_URL}/api/scrape`,
    settings: () => `${API_BASE_URL}/api/settings`,
    wsScrapeStatus: () => `${WS_URL}/api/ws/scrape-status?api_key=${API_KEY}`,
} as const;
