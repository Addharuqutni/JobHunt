import React, { useState, useEffect, useRef } from 'react';
import { Globe } from 'lucide-react';
import { useDashboardStats } from '../hooks/useDashboardStats';
import { StatsGrid } from './StatsCard';
import { API } from '../../../config/api';
import { post } from '../../../shared/services/apiClient';
import '../../dashboard/styles/DashboardOverview.css';

/**
 * DashboardOverview — main dashboard page component.
 * Displays stats, scraper progress, and force-scrape action.
 */
const DashboardOverview: React.FC = () => {
    const { stats } = useDashboardStats();

    const [scrapingProgress, setScrapingProgress] = useState<number | null>(null);
    const [scrapingMessage, setScrapingMessage] = useState<string>('');
    const [isScraping, setIsScraping] = useState<boolean>(false);

    const isScrapingRef = useRef(isScraping);
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Keep ref in sync with state
    useEffect(() => {
        isScrapingRef.current = isScraping;
    }, [isScraping]);

    useEffect(() => {
        const ws = new WebSocket(API.wsScrapeStatus());

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.message) setScrapingMessage(data.message);
                if (data.progress !== undefined) {
                    setScrapingProgress(data.progress);
                    if (!isScrapingRef.current) setIsScraping(true);

                    if (data.progress >= 100) {
                        timeoutRef.current = setTimeout(() => {
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
            // Connection closed — no auto-reconnect for now
        };

        return () => {
            ws.close();
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    const handleForceScrape = async () => {
        if (isScraping) return;
        try {
            setIsScraping(true);
            setScrapingMessage("Initializing Scraper...");
            setScrapingProgress(0);
            await post(API.scrape());
        } catch (error) {
            console.error("Failed to start scraper", error);
            setIsScraping(false);
            setScrapingProgress(null);
            setScrapingMessage("");
            alert(error instanceof Error ? error.message : 'Could not start scraper.');
        }
    };

    const defaultStats = { totalJobs: 0, newToday: 0, sentToTelegram: 0, activeSources: 0 };

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
                        aria-busy={isScraping}
                    >
                        <Globe size={16} className={isScraping ? "spin-animation" : ""} aria-hidden="true" />
                        {isScraping ? "Scraping in Progress..." : "Force Scrape Now"}
                    </button>
                </div>
            </div>

            {scrapingProgress !== null && (
                <div className="progress-container glass-panel">
                    <div className="progress-header">
                        <span className="progress-text" id="scrape-progress-label">{scrapingMessage}</span>
                        <span className="progress-percentage">{scrapingProgress}%</span>
                    </div>
                    <div
                        className="progress-bar-bg"
                        role="progressbar"
                        aria-valuenow={scrapingProgress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-labelledby="scrape-progress-label"
                    >
                        <div
                            className="progress-bar-fill"
                            style={{ width: `${scrapingProgress}%` }}
                        ></div>
                    </div>
                </div>
            )}

            <StatsGrid stats={stats || defaultStats} />
        </div>
    );
};

export default DashboardOverview;
