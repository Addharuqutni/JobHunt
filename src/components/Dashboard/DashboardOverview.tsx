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

    const [scrapingProgress, setScrapingProgress] = useState<number | null>(null);
    const [scrapingMessage, setScrapingMessage] = useState<string>('');
    const [isScraping, setIsScraping] = useState<boolean>(false);

    useEffect(() => {
        let ws: WebSocket;
        const connectWs = () => {
            ws = new WebSocket(API.wsScrapeStatus());
            
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.message) setScrapingMessage(data.message);
                    if (data.progress !== undefined) {
                        setScrapingProgress(data.progress);
                        if (!isScraping) setIsScraping(true);
                        
                        if (data.progress >= 100) {
                            setTimeout(() => {
                                setScrapingProgress(null);
                                setScrapingMessage('');
                                setIsScraping(false);
                            }, 5000);
                        }
                    }
                } catch (e) {
                    console.error("Failed to parse WS message", e);
                }
            };
            
            ws.onclose = () => {
                // Optional: Attempt reconnect after a delay if desired. 
                // Currently, we'll let it close safely.
            };
        };
        
        connectWs();
        return () => {
            if (ws) ws.close();
        };
    }, []);

    const handleForceScrape = async () => {
        if (isScraping) return;
        try {
            setIsScraping(true);
            setScrapingMessage("Initializing Scraper...");
            setScrapingProgress(0);
            const response = await fetch(API.scrape(), {
                method: 'POST',
                headers: getHeaders()
            });
            if (!response.ok) {
                const err = await response.json();
                console.error("Scrape trigged failed:", err);
                setIsScraping(false);
                setScrapingProgress(null);
                setScrapingMessage("");
                alert(`Error: ${err.detail || 'Could not start scraper.'}`);
            }
        } catch (error) {
            console.error("Failed to start scraper", error);
            setIsScraping(false);
            setScrapingProgress(null);
            setScrapingMessage("");
        }
    };

    return (
        <div className="dashboard-overview">
            <div className="overview-header">
                <div>
                    <h2 className="page-title">Dashboard Overview</h2>
                    <p className="page-subtitle">Your automated job scraping insights for today.</p>
                </div>
                <div className="overview-actions">
                    <button 
                        className="btn btn-primary" 
                        onClick={handleForceScrape}
                        disabled={isScraping}
                    >
                        <Globe size={16} className={isScraping ? "spin-animation" : ""} />
                        {isScraping ? "Scraping in Progress..." : "Force Scrape Now"}
                    </button>
                </div>
            </div>

            {scrapingProgress !== null && (
                <div className="progress-container glass-panel">
                    <div className="progress-header">
                        <span className="progress-text">{scrapingMessage}</span>
                        <span className="progress-percentage">{scrapingProgress}%</span>
                    </div>
                    <div className="progress-bar-bg">
                        <div 
                            className="progress-bar-fill" 
                            style={{ width: `${scrapingProgress}%` }}
                        ></div>
                    </div>
                </div>
            )}

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
