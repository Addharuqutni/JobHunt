/**
 * Tests for the shared API client.
 * Verifies consistent error handling, JSON parsing, and header injection.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get, post, ApiError } from '../../shared/services/apiClient';

// Mock the config module to provide a test API key
vi.mock('../../config/api', () => ({
    API_KEY: 'test-api-key',
}));

describe('apiClient', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe('get()', () => {
        it('returns parsed JSON on successful response', async () => {
            const mockData = { jobs: [{ id: 1, title: 'Dev' }] };
            global.fetch = vi.fn().mockResolvedValue({
                ok: true,
                status: 200,
                json: () => Promise.resolve(mockData),
            });

            const result = await get<typeof mockData>('http://localhost/api/jobs');

            expect(result).toEqual(mockData);
            expect(global.fetch).toHaveBeenCalledWith('http://localhost/api/jobs', expect.objectContaining({
                method: 'GET',
                headers: expect.objectContaining({
                    'X-API-Key': 'test-api-key',
                    'Content-Type': 'application/json',
                }),
            }));
        });

        it('throws ApiError on non-OK response with detail', async () => {
            global.fetch = vi.fn().mockResolvedValue({
                ok: false,
                status: 401,
                statusText: 'Unauthorized',
                json: () => Promise.resolve({ detail: 'Invalid API key' }),
            });

            await expect(get('http://localhost/api/jobs')).rejects.toThrow(ApiError);
            await expect(get('http://localhost/api/jobs')).rejects.toThrow('Invalid API key');
        });

        it('throws ApiError with fallback message when body is not JSON', async () => {
            global.fetch = vi.fn().mockResolvedValue({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error',
                json: () => Promise.reject(new Error('not json')),
            });

            await expect(get('http://localhost/api/jobs')).rejects.toThrow(ApiError);
            await expect(get('http://localhost/api/jobs')).rejects.toThrow('Request failed with HTTP 500 Internal Server Error');
        });
    });

    describe('post()', () => {
        it('sends JSON body and returns parsed response', async () => {
            const payload = { keywords: 'react' };
            const mockResponse = { success: true };
            global.fetch = vi.fn().mockResolvedValue({
                ok: true,
                status: 200,
                json: () => Promise.resolve(mockResponse),
            });

            const result = await post<typeof mockResponse>('http://localhost/api/settings', payload);

            expect(result).toEqual(mockResponse);
            expect(global.fetch).toHaveBeenCalledWith('http://localhost/api/settings', expect.objectContaining({
                method: 'POST',
                body: JSON.stringify(payload),
            }));
        });

        it('handles 204 No Content gracefully', async () => {
            global.fetch = vi.fn().mockResolvedValue({
                ok: true,
                status: 204,
                json: () => Promise.reject(new Error('no body')),
            });

            const result = await post('http://localhost/api/scrape');
            expect(result).toBeUndefined();
        });
    });
});
