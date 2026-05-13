/**
 * Dashboard API service — encapsulates stats-related API calls.
 * Uses the shared API client for consistent error handling.
 */
import { get } from '../../../shared/services/apiClient';
import { API } from '../../../config/api';
import type { DashboardStats } from '../types';

/**
 * Fetch dashboard statistics from the API.
 */
export async function fetchDashboardStats(): Promise<DashboardStats> {
    return get<DashboardStats>(API.stats());
}
