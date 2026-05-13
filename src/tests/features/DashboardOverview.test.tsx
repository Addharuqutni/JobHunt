/**
 * Tests for DashboardOverview component.
 * Verifies scrape button behavior, progress bar ARIA, and WebSocket cleanup.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DashboardOverview from '../../features/dashboard/components/DashboardOverview';

// Mock the shared API client
vi.mock('../../shared/services/apiClient', () => ({
    post: vi.fn(),
    get: vi.fn(),
}));

// Mock the dashboard stats hook
vi.mock('../../features/dashboard/hooks/useDashboardStats', () => ({
    useDashboardStats: () => ({
        stats: { totalJobs: 42, newToday: 5, sentToTelegram: 10, activeSources: 3 },
        isLoading: false,
        error: null,
        refetch: vi.fn(),
    }),
}));

// Mock StatsGrid to keep tests focused on DashboardOverview logic
vi.mock('../../features/dashboard/components/StatsCard', () => ({
    StatsGrid: ({ stats }: { stats: Record<string, number> }) => (
        <div data-testid="stats-grid">{JSON.stringify(stats)}</div>
    ),
}));

// Mock WebSocket
class MockWebSocket {
    onmessage: ((event: MessageEvent) => void) | null = null;
    onclose: (() => void) | null = null;
    close = vi.fn();
    static instances: MockWebSocket[] = [];

    constructor() {
        MockWebSocket.instances.push(this);
    }

    simulateMessage(data: unknown) {
        if (this.onmessage) {
            this.onmessage({ data: JSON.stringify(data) } as MessageEvent);
        }
    }
}

// Mock config
vi.mock('../../config/api', () => ({
    API: {
        wsScrapeStatus: () => 'ws://localhost/api/ws/scrape-status',
        scrape: () => 'http://localhost/api/scrape',
    },
    API_KEY: 'test-key',
}));

describe('DashboardOverview', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        MockWebSocket.instances = [];
        (global as unknown as { WebSocket: typeof MockWebSocket }).WebSocket = MockWebSocket as unknown as typeof WebSocket;
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('renders the force scrape button', () => {
        render(<DashboardOverview />);
        expect(screen.getByRole('button', { name: /force scrape now/i })).toBeInTheDocument();
    });

    it('disables scrape button and shows progress text when scraping', async () => {
        const { post } = await import('../../shared/services/apiClient');
        (post as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);

        const user = userEvent.setup();
        render(<DashboardOverview />);

        const button = screen.getByRole('button', { name: /force scrape now/i });
        await user.click(button);

        expect(button).toBeDisabled();
        expect(button).toHaveAttribute('aria-busy', 'true');
        expect(screen.getByText(/scraping in progress/i)).toBeInTheDocument();
    });

    it('shows progress bar with ARIA attributes on WebSocket message', async () => {
        render(<DashboardOverview />);

        const ws = MockWebSocket.instances[0];
        act(() => {
            ws.simulateMessage({ progress: 45, message: 'Scraping Glints...' });
        });

        await waitFor(() => {
            const progressBar = screen.getByRole('progressbar');
            expect(progressBar).toHaveAttribute('aria-valuenow', '45');
            expect(progressBar).toHaveAttribute('aria-valuemin', '0');
            expect(progressBar).toHaveAttribute('aria-valuemax', '100');
        });

        expect(screen.getByText('Scraping Glints...')).toBeInTheDocument();
        expect(screen.getByText('45%')).toBeInTheDocument();
    });

    it('closes WebSocket on unmount', () => {
        const { unmount } = render(<DashboardOverview />);
        const ws = MockWebSocket.instances[0];

        unmount();

        expect(ws.close).toHaveBeenCalled();
    });

    it('shows error alert when scrape API fails', async () => {
        const { post } = await import('../../shared/services/apiClient');
        (post as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Server unavailable'));

        const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});
        const user = userEvent.setup();
        render(<DashboardOverview />);

        const button = screen.getByRole('button', { name: /force scrape now/i });
        await user.click(button);

        await waitFor(() => {
            expect(alertMock).toHaveBeenCalledWith('Server unavailable');
        });

        alertMock.mockRestore();
    });
});
