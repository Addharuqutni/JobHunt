/**
 * useDashboardStats hook — manages dashboard statistics state.
 */
import { useState, useEffect, useCallback } from 'react';
import { fetchDashboardStats } from '../services/dashboardApi';
import type { DashboardStats } from '../types';
import type { LoadingState } from '../../../shared/types/api';

interface UseDashboardStatsReturn {
    stats: DashboardStats | null;
    status: LoadingState;
    error: string | null;
    refetch: () => void;
    isLoading: boolean;
}

/**
 * Hook for fetching and managing dashboard statistics.
 * Auto-fetches on mount.
 */
export function useDashboardStats(): UseDashboardStatsReturn {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [status, setStatus] = useState<LoadingState>('idle');
    const [error, setError] = useState<string | null>(null);

    const loadStats = useCallback(async () => {
        setStatus('loading');
        setError(null);

        try {
            const data = await fetchDashboardStats();
            setStats(data);
            setStatus('success');
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load stats';
            setError(message);
            setStatus('error');
        }
    }, []);

    useEffect(() => {
        loadStats();
    }, [loadStats]);

    return {
        stats,
        status,
        error,
        refetch: loadStats,
        isLoading: status === 'loading',
    };
}
