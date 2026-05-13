import React, { useState, useEffect, useMemo } from 'react';
import { ExternalLink, Building2, MapPin, Clock, CheckCircle, Search, Filter, RefreshCw, Download, DollarSign } from 'lucide-react';
import { fetchJobs } from '../services/jobApi';
import type { Job } from '../types';
import '../styles/JobList.css';

/**
 * JobList — full job listing page with advanced filtering, sorting, pagination, and Excel export.
 */
const JobList: React.FC = () => {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [sourceFilter, setSourceFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');
    const [jobTypeFilter, setJobTypeFilter] = useState('all');
    const [workModelFilter, setWorkModelFilter] = useState('all');
    const [experienceFilter, setExperienceFilter] = useState('all');
    const [sortOrder, setSortOrder] = useState('newest');
    const [currentPage, setCurrentPage] = useState(1);
    const jobsPerPage = 20;

    useEffect(() => {
        loadJobs();
    }, []);

    const loadJobs = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await fetchJobs({ limit: 500 });
            setJobs(data.jobs || []);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load jobs';
            setError(message);
            console.error("Error fetching jobs:", err);
        } finally {
            setLoading(false);
        }
    };

    /** Derived filtered and sorted jobs — computed from state, not stored separately. */
    const filteredJobs = useMemo(() => {
        let result = [...jobs];

        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter(job =>
                job.title.toLowerCase().includes(q) ||
                job.company.toLowerCase().includes(q) ||
                (job.location || '').toLowerCase().includes(q)
            );
        }

        if (sourceFilter !== 'all') {
            result = result.filter(job => job.source.toLowerCase() === sourceFilter);
        }

        if (statusFilter === 'sent') {
            result = result.filter(job => job.is_sent);
        } else if (statusFilter === 'pending') {
            result = result.filter(job => !job.is_sent);
        }

        if (jobTypeFilter !== 'all') {
            result = result.filter(job => job.job_type?.toLowerCase() === jobTypeFilter.toLowerCase());
        }

        if (workModelFilter !== 'all') {
            result = result.filter(job => job.work_model?.toLowerCase() === workModelFilter.toLowerCase());
        }

        if (experienceFilter !== 'all') {
            result = result.filter(job => job.experience_level?.toLowerCase() === experienceFilter.toLowerCase());
        }

        if (sortOrder === 'newest') {
            result.sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime());
        } else if (sortOrder === 'oldest') {
            result.sort((a, b) => new Date(a.created_at || '').getTime() - new Date(b.created_at || '').getTime());
        }

        return result;
    }, [jobs, searchQuery, sourceFilter, statusFilter, jobTypeFilter, workModelFilter, experienceFilter, sortOrder]);

    // Reset page when filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [searchQuery, sourceFilter, statusFilter, jobTypeFilter, workModelFilter, experienceFilter, sortOrder]);

    const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);
    const paginatedJobs = filteredJobs.slice(
        (currentPage - 1) * jobsPerPage,
        currentPage * jobsPerPage
    );

    const uniqueSources = [...new Set(jobs.map(j => j.source))];

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return 'Unknown';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('id-ID', {
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        } catch {
            return dateStr.split(' ')[0];
        }
    };

    /** Export filtered jobs to Excel file. Lazy-loads xlsx to reduce bundle size. */
    const exportToExcel = async () => {
        if (filteredJobs.length === 0) {
            alert("No data to export");
            return;
        }

        const XLSX = await import('xlsx');

        const dataToExport = filteredJobs.map(job => ({
            Title: job.title,
            Company: job.company,
            Location: job.location || 'N/A',
            Source: job.source,
            Salary: job.salary || 'N/A',
            'Job Type': job.job_type || 'N/A',
            'Work Model': job.work_model || 'N/A',
            'Experience': job.experience_level || 'N/A',
            Status: job.is_sent ? 'Sent' : 'Pending',
            Posted: job.posted_at || 'N/A',
            'Scraped Date': formatDate(job.created_at),
            Link: job.url
        }));

        const worksheet = XLSX.utils.json_to_sheet(dataToExport);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Jobs");

        XLSX.writeFile(workbook, `JobSentinel_Export_${new Date().toISOString().slice(0, 10)}.xlsx`);
    };

    return (
        <div className="all-jobs-page animate-fade-in">
            <div className="all-jobs-header">
                <div>
                    <h2 className="page-title">All Jobs</h2>
                    <p className="page-subtitle">
                        Browse and filter all {jobs.length} scraped job postings.
                    </p>
                </div>
                <div className="header-actions" style={{ display: 'flex', gap: '10px' }}>
                    <button className="btn btn-secondary" onClick={exportToExcel} disabled={filteredJobs.length === 0}>
                        <Download size={16} aria-hidden="true" />
                        Export Excel
                    </button>
                    <button className="btn btn-primary" onClick={loadJobs} aria-busy={loading}>
                        <RefreshCw size={16} className={loading ? 'spin' : ''} aria-hidden="true" />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="filters-bar glass-panel" role="search" aria-label="Job filters">
                <div className="search-filter">
                    <Search size={18} className="filter-icon" aria-hidden="true" />
                    <label htmlFor="job-search-input" className="sr-only">Search jobs</label>
                    <input
                        id="job-search-input"
                        type="search"
                        placeholder="Search by title, company, or location..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="filter-input"
                    />
                </div>

                <div className="filter-group">
                    <div className="filter-select-wrapper">
                        <Filter size={16} className="filter-icon-small" aria-hidden="true" />
                        <label htmlFor="source-filter" className="sr-only">Filter by source</label>
                        <select id="source-filter" value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)} className="filter-select">
                            <option value="all">All Sources</option>
                            {uniqueSources.map(src => (
                                <option key={src} value={src.toLowerCase()}>{src}</option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <label htmlFor="status-filter" className="sr-only">Filter by status</label>
                        <select id="status-filter" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="filter-select">
                            <option value="all">All Status</option>
                            <option value="sent">Sent</option>
                            <option value="pending">Pending</option>
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <label htmlFor="type-filter" className="sr-only">Filter by job type</label>
                        <select id="type-filter" value={jobTypeFilter} onChange={(e) => setJobTypeFilter(e.target.value)} className="filter-select">
                            <option value="all">All Types</option>
                            <option value="full-time">Full-time</option>
                            <option value="part-time">Part-time</option>
                            <option value="contract">Contract</option>
                            <option value="internship">Internship</option>
                            <option value="freelance">Freelance</option>
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <label htmlFor="model-filter" className="sr-only">Filter by work model</label>
                        <select id="model-filter" value={workModelFilter} onChange={(e) => setWorkModelFilter(e.target.value)} className="filter-select">
                            <option value="all">All Models</option>
                            <option value="remote">Remote</option>
                            <option value="hybrid">Hybrid</option>
                            <option value="on-site">On-site</option>
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <label htmlFor="experience-filter" className="sr-only">Filter by experience level</label>
                        <select id="experience-filter" value={experienceFilter} onChange={(e) => setExperienceFilter(e.target.value)} className="filter-select">
                            <option value="all">All Levels</option>
                            <option value="entry">Entry</option>
                            <option value="mid">Mid</option>
                            <option value="senior">Senior</option>
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <label htmlFor="sort-order" className="sr-only">Sort order</label>
                        <select id="sort-order" value={sortOrder} onChange={(e) => setSortOrder(e.target.value)} className="filter-select">
                            <option value="newest">Newest First</option>
                            <option value="oldest">Oldest First</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Results Count */}
            <div className="results-info">
                <span className="results-count">
                    Showing <strong>{paginatedJobs.length}</strong> of <strong>{filteredJobs.length}</strong> jobs
                </span>
            </div>

            {/* Job Cards Grid */}
            {loading ? (
                <div className="loading-state" aria-live="polite">
                    <RefreshCw size={32} className="spin" aria-hidden="true" />
                    <p>Loading jobs...</p>
                </div>
            ) : error ? (
                <div className="empty-state glass-panel" role="alert">
                    <Search size={48} aria-hidden="true" />
                    <h3>Failed to load jobs</h3>
                    <p>{error}</p>
                    <button className="btn btn-primary" onClick={loadJobs}>Retry</button>
                </div>
            ) : paginatedJobs.length === 0 ? (
                <div className="empty-state glass-panel">
                    <Search size={48} aria-hidden="true" />
                    <h3>No jobs found</h3>
                    <p>Try adjusting your filters or run a new scraping session.</p>
                </div>
            ) : (
                <div className="jobs-grid">
                    {paginatedJobs.map((job) => (
                        <div key={job.id} className="job-card glass-panel">
                            <div className="job-card-header">
                                <h4 className="job-card-title">{job.title}</h4>
                                <span className={`source-tag source-${job.source.toLowerCase()}`}>
                                    {job.source}
                                </span>
                            </div>

                            <div className="job-card-details">
                                <div className="detail-row">
                                    <Building2 size={15} aria-hidden="true" />
                                    <span>{job.company || 'Unknown Company'}</span>
                                </div>
                                <div className="detail-row">
                                    <MapPin size={15} aria-hidden="true" />
                                    <span>{job.location || 'Unknown Location'}</span>
                                </div>
                                {job.salary && (
                                    <div className="detail-row detail-salary">
                                        <DollarSign size={15} aria-hidden="true" />
                                        <span>{job.salary}</span>
                                    </div>
                                )}
                                <div className="detail-row">
                                    <Clock size={15} aria-hidden="true" />
                                    <span>{job.posted_at || 'Unknown Date'}</span>
                                </div>
                            </div>

                            <div className="job-card-tags">
                                {job.job_type && (
                                    <span className="job-tag tag-type">{job.job_type}</span>
                                )}
                                {job.work_model && (
                                    <span className={`job-tag tag-model tag-model-${job.work_model.toLowerCase().replace(/[^a-z]/g, '')}`}>
                                        {job.work_model}
                                    </span>
                                )}
                                {job.experience_level && (
                                    <span className="job-tag tag-experience">{job.experience_level}</span>
                                )}
                            </div>

                            {job.description && (
                                <p className="job-card-description">
                                    {job.description.length > 120 ? job.description.substring(0, 120) + '...' : job.description}
                                </p>
                            )}

                            <div className="job-card-footer">
                                {job.is_sent ? (
                                    <span className="status-chip status-sent">
                                        <CheckCircle size={13} aria-hidden="true" /> Sent
                                    </span>
                                ) : (
                                    <span className="status-chip status-pending">
                                        <Clock size={13} aria-hidden="true" /> Pending
                                    </span>
                                )}
                                <a
                                    href={job.url}
                                    className="apply-btn"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Apply <ExternalLink size={14} aria-hidden="true" />
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <nav className="pagination-bar" aria-label="Job list pagination">
                    <button
                        className="page-btn"
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(p => p - 1)}
                        aria-label="Previous page"
                    >
                        Previous
                    </button>

                    <div className="page-numbers">
                        {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                            let pageNum: number;
                            if (totalPages <= 7) {
                                pageNum = i + 1;
                            } else if (currentPage <= 4) {
                                pageNum = i + 1;
                            } else if (currentPage >= totalPages - 3) {
                                pageNum = totalPages - 6 + i;
                            } else {
                                pageNum = currentPage - 3 + i;
                            }
                            return (
                                <button
                                    key={pageNum}
                                    className={`page-num ${currentPage === pageNum ? 'active' : ''}`}
                                    onClick={() => setCurrentPage(pageNum)}
                                    aria-label={`Page ${pageNum}`}
                                    aria-current={currentPage === pageNum ? 'page' : undefined}
                                >
                                    {pageNum}
                                </button>
                            );
                        })}
                    </div>

                    <button
                        className="page-btn"
                        disabled={currentPage === totalPages}
                        onClick={() => setCurrentPage(p => p + 1)}
                        aria-label="Next page"
                    >
                        Next
                    </button>
                </nav>
            )}
        </div>
    );
};

export default JobList;
