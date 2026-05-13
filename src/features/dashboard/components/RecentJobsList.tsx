import React, { useState, useEffect } from 'react';
import { ExternalLink, Building2, MapPin, Clock, CheckCircle, DollarSign, RefreshCw } from 'lucide-react';
import { fetchJobs } from '../../jobs/services/jobApi';
import type { Job } from '../../jobs/types';
import '../../dashboard/styles/RecentJobsList.css';

/**
 * RecentJobsList — displays recent jobs in a table format on the dashboard.
 * Supports tab filtering: All / Pending Telegram / Sent.
 */
const RecentJobsList: React.FC = () => {
    const [activeTab, setActiveTab] = useState('All');
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadJobs = async () => {
            try {
                const data = await fetchJobs();
                setJobs(data.jobs || []);
            } catch (err) {
                const message = err instanceof Error ? err.message : 'Failed to load recent jobs';
                setError(message);
                console.error("Error fetching jobs:", err);
            } finally {
                setLoading(false);
            }
        };
        loadJobs();
    }, []);

    const filteredJobs = jobs.filter(job => {
        if (activeTab === 'Pending Telegram') return !job.is_sent;
        if (activeTab === 'Sent') return job.is_sent;
        return true;
    });

    if (loading) {
        return (
            <div className="job-list-container glass-panel animate-fade-in" aria-live="polite">
                <div className="loading-state">
                    <RefreshCw size={24} className="spin" aria-hidden="true" />
                    <p>Loading recent jobs...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="job-list-container glass-panel animate-fade-in" role="alert">
                <div className="empty-state">
                    <h3>Failed to load jobs</h3>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="job-list-container glass-panel animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="job-list-header">
                <h3 className="section-title">Recent Job Postings</h3>
                <div className="filter-tabs" role="tablist" aria-label="Filter jobs by status">
                    <button
                        className={`filter-tab ${activeTab === 'All' ? 'active' : ''}`}
                        onClick={() => setActiveTab('All')}
                        role="tab"
                        aria-selected={activeTab === 'All'}
                    >
                        All Jobs
                    </button>
                    <button
                        className={`filter-tab ${activeTab === 'Pending Telegram' ? 'active' : ''}`}
                        onClick={() => setActiveTab('Pending Telegram')}
                        role="tab"
                        aria-selected={activeTab === 'Pending Telegram'}
                    >
                        Pending Telegram
                    </button>
                    <button
                        className={`filter-tab ${activeTab === 'Sent' ? 'active' : ''}`}
                        onClick={() => setActiveTab('Sent')}
                        role="tab"
                        aria-selected={activeTab === 'Sent'}
                    >
                        Sent
                    </button>
                </div>
            </div>

            <div className="job-table-wrapper">
                <table className="job-table">
                    <thead>
                        <tr>
                            <th>Job Role</th>
                            <th>Company & Location</th>
                            <th>Details</th>
                            <th>Source</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredJobs.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="empty-table-cell">
                                    No jobs match the current filter.
                                </td>
                            </tr>
                        ) : (
                            filteredJobs.map((job) => (
                                <tr key={job.id} className="job-row">
                                    <td>
                                        <div className="job-title-cell">
                                            <span className="job-title">{job.title}</span>
                                            {job.salary && (
                                                <span className="job-salary-inline">
                                                    <DollarSign size={12} aria-hidden="true" /> {job.salary}
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                    <td>
                                        <div className="company-cell">
                                            <div className="company-info">
                                                <Building2 size={14} className="cell-icon" aria-hidden="true" />
                                                <span>{job.company}</span>
                                            </div>
                                            <div className="location-info">
                                                <MapPin size={14} className="cell-icon" aria-hidden="true" />
                                                <span>{job.location}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <div className="details-cell">
                                            {job.job_type && <span className="mini-tag">{job.job_type}</span>}
                                            {job.work_model && <span className="mini-tag">{job.work_model}</span>}
                                            {job.experience_level && <span className="mini-tag">{job.experience_level}</span>}
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`source-badge source-${job.source.toLowerCase()}`}>
                                            {job.source}
                                        </span>
                                    </td>
                                    <td>
                                        {job.is_sent ? (
                                            <span className="status-badge status-sent">
                                                <CheckCircle size={14} aria-hidden="true" /> Sent
                                            </span>
                                        ) : (
                                            <span className="status-badge status-pending">
                                                <Clock size={14} aria-hidden="true" /> Pending
                                            </span>
                                        )}
                                    </td>
                                    <td>
                                        <a href={job.url} className="action-link" target="_blank" rel="noopener noreferrer">
                                            Apply <ExternalLink size={14} aria-hidden="true" />
                                        </a>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <div className="pagination">
                <span className="pagination-text">Showing {filteredJobs.length} entries</span>
            </div>
        </div>
    );
};

export default RecentJobsList;
