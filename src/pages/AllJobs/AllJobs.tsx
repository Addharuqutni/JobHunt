import React, { useState, useEffect } from 'react';
import { ExternalLink, Building2, MapPin, Calendar, Clock, CheckCircle, Search, Filter, RefreshCw, Download } from 'lucide-react';
import * as XLSX from 'xlsx';
import { API, getHeaders } from '../../config';
import './AllJobs.css';

interface Job {
    id: number;
    job_hash: string;
    title: string;
    company: string;
    location: string;
    url: string;
    source: string;
    is_sent: number;
    created_at: string;
}

const AllJobs: React.FC = () => {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [sourceFilter, setSourceFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');
    const [sortOrder, setSortOrder] = useState('newest'); // 'newest' | 'oldest'
    const [currentPage, setCurrentPage] = useState(1);
    const jobsPerPage = 20;

    useEffect(() => {
        fetchJobs();
    }, []);

    useEffect(() => {
        applyFilters();
    }, [jobs, searchQuery, sourceFilter, statusFilter, sortOrder]);

    const fetchJobs = async () => {
        setLoading(true);
        try {
            const response = await fetch(API.jobs({ limit: 500 }), { headers: getHeaders() });
            const data = await response.json();
            if (data.jobs) {
                setJobs(data.jobs);
            }
        } catch (error) {
            console.error("Error fetching jobs:", error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        let result = [...jobs];

        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter(job =>
                job.title.toLowerCase().includes(q) ||
                job.company.toLowerCase().includes(q) ||
                job.location.toLowerCase().includes(q)
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

        // Apply Sorting by Date
        if (sortOrder === 'newest') {
            result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        } else if (sortOrder === 'oldest') {
            result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        }

        setFilteredJobs(result);
        setCurrentPage(1);
    };

    const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);
    const paginatedJobs = filteredJobs.slice(
        (currentPage - 1) * jobsPerPage,
        currentPage * jobsPerPage
    );

    const uniqueSources = [...new Set(jobs.map(j => j.source))];

    const formatDate = (dateStr: string) => {
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

    const exportToExcel = () => {
        if (filteredJobs.length === 0) {
            alert("No data to export");
            return;
        }

        const dataToExport = filteredJobs.map(job => ({
            Title: job.title,
            Company: job.company,
            Location: job.location,
            Source: job.source,
            Status: job.is_sent ? 'Sent' : 'Pending',
            Date: formatDate(job.created_at),
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
                        <Download size={16} />
                        Export Excel
                    </button>
                    <button className="btn btn-primary" onClick={fetchJobs}>
                        <RefreshCw size={16} className={loading ? 'spin' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="filters-bar glass-panel">
                <div className="search-filter">
                    <Search size={18} className="filter-icon" />
                    <input
                        type="text"
                        placeholder="Search by title, company, or location..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="filter-input"
                    />
                </div>

                <div className="filter-group">
                    <div className="filter-select-wrapper">
                        <Filter size={16} className="filter-icon-small" />
                        <select
                            value={sourceFilter}
                            onChange={(e) => setSourceFilter(e.target.value)}
                            className="filter-select"
                        >
                            <option value="all">All Sources</option>
                            {uniqueSources.map(src => (
                                <option key={src} value={src.toLowerCase()}>{src}</option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="filter-select"
                        >
                            <option value="all">All Status</option>
                            <option value="sent">Sent</option>
                            <option value="pending">Pending</option>
                        </select>
                    </div>

                    <div className="filter-select-wrapper">
                        <select
                            value={sortOrder}
                            onChange={(e) => setSortOrder(e.target.value)}
                            className="filter-select"
                        >
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
                <div className="loading-state">
                    <RefreshCw size={32} className="spin" />
                    <p>Loading jobs...</p>
                </div>
            ) : paginatedJobs.length === 0 ? (
                <div className="empty-state glass-panel">
                    <Search size={48} />
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
                                    <Building2 size={15} />
                                    <span>{job.company || 'Unknown Company'}</span>
                                </div>
                                <div className="detail-row">
                                    <MapPin size={15} />
                                    <span>{job.location || 'Unknown Location'}</span>
                                </div>
                                <div className="detail-row">
                                    <Calendar size={15} />
                                    <span>{formatDate(job.created_at)}</span>
                                </div>
                            </div>

                            <div className="job-card-footer">
                                {job.is_sent ? (
                                    <span className="status-chip status-sent">
                                        <CheckCircle size={13} /> Sent
                                    </span>
                                ) : (
                                    <span className="status-chip status-pending">
                                        <Clock size={13} /> Pending
                                    </span>
                                )}
                                <a
                                    href={job.url}
                                    className="apply-btn"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Apply <ExternalLink size={14} />
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="pagination-bar">
                    <button
                        className="page-btn"
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(p => p - 1)}
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
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default AllJobs;
