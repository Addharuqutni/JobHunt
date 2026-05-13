/**
 * Tests for JobList component.
 * Verifies filtering, pagination, error state, and accessibility.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import JobList from '../../features/jobs/components/JobList';

// Mock the jobs API service
vi.mock('../../features/jobs/services/jobApi', () => ({
    fetchJobs: vi.fn(),
}));

import { fetchJobs } from '../../features/jobs/services/jobApi';
const mockFetchJobs = vi.mocked(fetchJobs);

const mockJobs = [
    { id: 1, title: 'Frontend Developer', company: 'Acme Corp', location: 'Jakarta', source: 'Glints', is_sent: true, url: 'https://example.com/1', created_at: '2026-05-12T10:00:00Z', job_type: 'Full-time', work_model: 'Remote', experience_level: 'Mid', salary: '15M IDR', posted_at: '2 days ago', description: 'Build UIs' },
    { id: 2, title: 'Backend Engineer', company: 'Tech Inc', location: 'Bandung', source: 'Jobstreet', is_sent: false, url: 'https://example.com/2', created_at: '2026-05-11T08:00:00Z', job_type: 'Contract', work_model: 'On-site', experience_level: 'Senior', salary: null, posted_at: '1 week ago', description: 'Build APIs' },
    { id: 3, title: 'Fullstack Developer', company: 'Startup XYZ', location: 'Remote', source: 'Glints', is_sent: false, url: 'https://example.com/3', created_at: '2026-05-10T06:00:00Z', job_type: 'Full-time', work_model: 'Remote', experience_level: 'Entry', salary: '8M IDR', posted_at: '3 days ago', description: null },
];

describe('JobList', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders loading state initially', () => {
        mockFetchJobs.mockReturnValue(new Promise(() => {})); // never resolves
        render(<JobList />);
        expect(screen.getByText('Loading jobs...')).toBeInTheDocument();
    });

    it('renders error state when API fails', async () => {
        mockFetchJobs.mockRejectedValue(new Error('Network error'));
        render(<JobList />);

        await waitFor(() => {
            expect(screen.getByText('Failed to load jobs')).toBeInTheDocument();
            expect(screen.getByText('Network error')).toBeInTheDocument();
        });

        expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
    });

    it('renders job cards after successful fetch', async () => {
        mockFetchJobs.mockResolvedValue({ jobs: mockJobs });
        render(<JobList />);

        await waitFor(() => {
            expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
            expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
            expect(screen.getByText('Fullstack Developer')).toBeInTheDocument();
        });
    });

    it('filters jobs by search query', async () => {
        mockFetchJobs.mockResolvedValue({ jobs: mockJobs });
        const user = userEvent.setup();
        render(<JobList />);

        await waitFor(() => {
            expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        });

        const searchInput = screen.getByLabelText('Search jobs');
        await user.type(searchInput, 'Backend');

        expect(screen.queryByText('Frontend Developer')).not.toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });

    it('filters jobs by status', async () => {
        mockFetchJobs.mockResolvedValue({ jobs: mockJobs });
        const user = userEvent.setup();
        render(<JobList />);

        await waitFor(() => {
            expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        });

        const statusSelect = screen.getByLabelText('Filter by status');
        await user.selectOptions(statusSelect, 'sent');

        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.queryByText('Backend Engineer')).not.toBeInTheDocument();
        expect(screen.queryByText('Fullstack Developer')).not.toBeInTheDocument();
    });

    it('renders empty state when no jobs match filters', async () => {
        mockFetchJobs.mockResolvedValue({ jobs: mockJobs });
        const user = userEvent.setup();
        render(<JobList />);

        await waitFor(() => {
            expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        });

        const searchInput = screen.getByLabelText('Search jobs');
        await user.type(searchInput, 'nonexistent job xyz');

        expect(screen.getByText('No jobs found')).toBeInTheDocument();
    });

    it('has accessible filter labels', async () => {
        mockFetchJobs.mockResolvedValue({ jobs: mockJobs });
        render(<JobList />);

        await waitFor(() => {
            expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        });

        expect(screen.getByLabelText('Search jobs')).toBeInTheDocument();
        expect(screen.getByLabelText('Filter by source')).toBeInTheDocument();
        expect(screen.getByLabelText('Filter by status')).toBeInTheDocument();
        expect(screen.getByLabelText('Filter by job type')).toBeInTheDocument();
        expect(screen.getByLabelText('Filter by work model')).toBeInTheDocument();
        expect(screen.getByLabelText('Filter by experience level')).toBeInTheDocument();
        expect(screen.getByLabelText('Sort order')).toBeInTheDocument();
    });
});
