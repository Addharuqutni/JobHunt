import React, { useState, useEffect } from 'react';
import { ExternalLink, Building2, MapPin, Calendar, Clock, CheckCircle } from 'lucide-react';
import { API, getHeaders } from '../../config';
import './JobList.css';

const JobList: React.FC = () => {
    const [activeTab, setActiveTab] = useState('All');
    const [jobs, setJobs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const response = await fetch(API.jobs(), { headers: getHeaders() });
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
        fetchJobs();
    }, []);

    // Simple filter logic for demonstration
    const filteredJobs = jobs.filter(job => {
        if (activeTab === 'Pending Telegram') return !job.is_sent;
        if (activeTab === 'Sent') return job.is_sent;
        return true; // All Jobs
    });

    return (
        <div className="job-list-container glass-panel animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="job-list-header">
                <h3 className="section-title">Recent Job Postings</h3>
                <div className="filter-tabs">
                    <button
                        className={`filter-tab ${activeTab === 'All' ? 'active' : ''}`}
                        onClick={() => setActiveTab('All')}
                    >
                        All Jobs
                    </button>
                    <button
                        className={`filter-tab ${activeTab === 'Pending Telegram' ? 'active' : ''}`}
                        onClick={() => setActiveTab('Pending Telegram')}
                    >
                        Pending Telegram
                    </button>
                    <button
                        className={`filter-tab ${activeTab === 'Sent' ? 'active' : ''}`}
                        onClick={() => setActiveTab('Sent')}
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
                            <th>Source</th>
                            <th>Status</th>
                            <th>Time Found</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredJobs.map((job) => (
                            <tr key={job.id} className="job-row">
                                <td>
                                    <div className="job-title-cell">
                                        <span className="job-title">{job.title}</span>
                                    </div>
                                </td>
                                <td>
                                    <div className="company-cell">
                                        <div className="company-info">
                                            <Building2 size={14} className="cell-icon" />
                                            <span>{job.company}</span>
                                        </div>
                                        <div className="location-info">
                                            <MapPin size={14} className="cell-icon" />
                                            <span>{job.location}</span>
                                        </div>
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
                                            <CheckCircle size={14} /> Sent
                                        </span>
                                    ) : (
                                        <span className="status-badge status-pending">
                                            <Clock size={14} /> Pending
                                        </span>
                                    )}
                                </td>
                                <td>
                                    <div className="time-cell">
                                        <Calendar size={14} className="cell-icon" />
                                        <span title={job.created_at}>
                                            {job.created_at ? job.created_at.split(' ')[0] : 'Unknown'}
                                        </span>
                                    </div>
                                </td>
                                <td>
                                    <a href={job.url} className="action-link" target="_blank" rel="noopener noreferrer">
                                        Apply <ExternalLink size={14} />
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="pagination">
                <span className="pagination-text">Showing {filteredJobs.length} entries</span>
                <div className="pagination-controls">
                    <button className="page-btn disabled">Previous</button>
                    <button className="page-btn active">1</button>
                    <button className="page-btn">2</button>
                    <button className="page-btn">3</button>
                    <span className="page-ellipsis">...</span>
                    <button className="page-btn">Next</button>
                </div>
            </div>
        </div>
    );
};

export default JobList;
