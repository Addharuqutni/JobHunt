/**
 * Jobs API service — encapsulates job-related API calls.
 * Uses the shared API client for consistent error handling.
 */
import { get } from '../../../shared/services/apiClient';
import { API } from '../../../config/api';
import type { Job } from '../types';

interface JobsResponse {
    jobs: Job[];
    total?: number;
}

/**
 * Fetch jobs from the API with optional filters.
 */
export async function fetchJobs(params?: {
    limit?: number;
    source?: string;
    search?: string;
    job_type?: string;
    work_model?: string;
    experience_level?: string;
}): Promise<JobsResponse> {
    return get<JobsResponse>(API.jobs(params));
}
