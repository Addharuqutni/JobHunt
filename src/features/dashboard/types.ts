/**
 * TypeScript types for the Dashboard feature.
 */

/** Dashboard statistics from the API. */
export interface DashboardStats {
    totalJobs: number;
    newToday: number;
    sentToTelegram: number;
    activeSources: number;
}
