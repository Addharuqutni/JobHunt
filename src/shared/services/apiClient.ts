/**
 * Shared API client — provides consistent request handling, JSON parsing,
 * and error management across all feature services.
 */
import { API_KEY } from '../../config/api';

export class ApiError extends Error {
    public status: number;
    public statusText: string;

    constructor(status: number, statusText: string, message?: string) {
        super(message || `Request failed with HTTP ${status} ${statusText}`);
        this.name = 'ApiError';
        this.status = status;
        this.statusText = statusText;
    }
}

/**
 * Returns standard headers for authenticated API requests.
 */
function getDefaultHeaders(): Record<string, string> {
    return {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
    };
}

interface RequestOptions extends Omit<RequestInit, 'headers'> {
    headers?: Record<string, string>;
}

/**
 * Core request function. Validates response status and parses JSON safely.
 * Throws ApiError for non-2xx responses so callers can handle uniformly.
 */
async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
    const { headers, ...rest } = options;

    // Abort request after 10 seconds to prevent infinite hang when backend is down
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    let response: Response;
    try {
        response = await fetch(url, {
            headers: { ...getDefaultHeaders(), ...headers },
            signal: controller.signal,
            ...rest,
        });
    } catch (err) {
        clearTimeout(timeoutId);
        if (err instanceof DOMException && err.name === 'AbortError') {
            throw new Error('Request timed out — backend may be unavailable.');
        }
        throw err;
    }
    clearTimeout(timeoutId);

    if (!response.ok) {
        let detail = '';
        try {
            const body = await response.json();
            detail = body.detail || body.message || '';
        } catch {
            // Response body is not JSON — use status text
        }
        throw new ApiError(response.status, response.statusText, detail || undefined);
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return undefined as unknown as T;
    }

    return response.json() as Promise<T>;
}

/**
 * GET request helper.
 */
export function get<T>(url: string, options?: RequestOptions): Promise<T> {
    return request<T>(url, { ...options, method: 'GET' });
}

/**
 * POST request helper.
 */
export function post<T>(url: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(url, {
        ...options,
        method: 'POST',
        body: body !== undefined ? JSON.stringify(body) : undefined,
    });
}

export default { get, post, ApiError };
