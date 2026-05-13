/**
 * TypeScript types for the Jobs feature.
 */

/** Single job entity from the API. */
export interface Job {
    id: number;
    job_hash: string;
    title: string;
    company: string;
    location: string | null;
    url: string;
    source: string;
    posted_at: string | null;
    is_sent: number;
    created_at: string | null;
    salary: string | null;
    job_type: string | null;
    work_model: string | null;
    experience_level: string | null;
    description: string | null;
}

/** API response for job listing. */
export interface JobListResponse {
    jobs: Job[];
    total: number;
}

/** Filter parameters for job queries. */
export interface JobFilters {
    limit?: number;
    source?: string;
    search?: string;
    job_type?: string;
    work_model?: string;
    experience_level?: string;
}
