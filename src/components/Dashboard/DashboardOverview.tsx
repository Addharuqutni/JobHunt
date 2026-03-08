import React, { useState, useEffect } from 'react';
import { Briefcase, TrendingUp, CheckCircle, Globe } from 'lucide-react';
import { API, getHeaders } from '../../config';
import './DashboardOverview.css';

const StatCard = ({ title, value, icon: Icon, trend, colorClass }: any) => (
    <div className="stat-card glass-panel">
        <div className="stat-card-header">
            <h3 className="stat-title">{title}</h3>
            <div className={`stat-icon-wrapper ${colorClass}`}>
                <Icon size={20} />
            </div>
        </div>
        <div className="stat-card-body">
            <div className="stat-value">{value}</div>
            <div className="stat-trend">
                <TrendingUp size={14} className="trend-icon" />
                <span>{trend}</span>
            </div>
        </div>
    </div>
);

const DashboardOverview: React.FC = () => {
    const [stats, setStats] = useState({
        totalJobs: 0,
        newToday: 0,
        sentToTelegram: 0,
        activeSources: 0
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch(API.stats(), { headers: getHeaders() });
                const data = await response.json();
                setStats(data);
            } catch (error) {
                console.error("Error fetching stats:", error);
            }
        };
        fetchStats();
    }, []);

    return (
        <div className="dashboard-overview">
            <div className="overview-header">
                <div>
                    <h2 className="page-title">Dashboard Overview</h2>
                    <p className="page-subtitle">Your automated job scraping insights for today.</p>
                </div>
                <div className="overview-actions">
                    <button className="btn btn-primary">
                        <Globe size={16} />
                        Force Scrape Now
                    </button>
                </div>
            </div>

            <div className="stats-grid">
                <StatCard
                    title="Total Jobs Scraped"
                    value={stats.totalJobs.toLocaleString()}
                    icon={Briefcase}
                    trend="All time"
                    colorClass="icon-primary"
                />
                <StatCard
                    title="New Today"
                    value={stats.newToday.toLocaleString()}
                    icon={TrendingUp}
                    trend="Last 24h"
                    colorClass="icon-success"
                />
                <StatCard
                    title="Sent to Telegram"
                    value={stats.sentToTelegram.toLocaleString()}
                    icon={CheckCircle}
                    trend="Processing queue"
                    colorClass="icon-info"
                />
                <StatCard
                    title="Active Sources"
                    value={stats.activeSources.toLocaleString()}
                    icon={Globe}
                    trend="Scraped portals"
                    colorClass="icon-warning"
                />
            </div>
        </div>
    );
};

export default DashboardOverview;
