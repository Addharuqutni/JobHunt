import React from 'react';
import { Briefcase, TrendingUp, CheckCircle, Globe, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import type { DashboardStats } from '../types';

interface StatCardProps {
    title: string;
    value: string;
    icon: React.ElementType;
    trend: string;
    trendDirection?: 'up' | 'down' | 'neutral';
    colorClass: string;
    delay?: number;
}

/**
 * Individual stat card — displays a metric with icon, animated value, and trend.
 */
const StatsCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, trend, trendDirection = 'neutral', colorClass, delay = 0 }) => (
    <div className="stat-card glass-panel" style={{ animationDelay: `${delay}ms` }}>
        <div className="stat-card-header">
            <div className={`stat-icon-wrapper ${colorClass}`}>
                <Icon size={20} aria-hidden="true" />
            </div>
            <div className={`stat-trend ${trendDirection}`}>
                {trendDirection === 'up' && <ArrowUpRight size={13} aria-hidden="true" />}
                {trendDirection === 'down' && <ArrowDownRight size={13} aria-hidden="true" />}
                <span>{trend}</span>
            </div>
        </div>
        <div className="stat-card-body">
            <div className="stat-value">{value}</div>
            <h3 className="stat-title">{title}</h3>
        </div>
        <div className={`stat-accent-bar ${colorClass}`} aria-hidden="true" />
    </div>
);

interface StatsGridProps {
    stats: DashboardStats;
}

/**
 * Stats grid — renders the 4 dashboard metric cards with staggered animation.
 */
export const StatsGrid: React.FC<StatsGridProps> = ({ stats }) => (
    <div className="stats-grid">
        <StatsCard
            title="Total Jobs Scraped"
            value={stats.totalJobs.toLocaleString()}
            icon={Briefcase}
            trend="All time"
            trendDirection="neutral"
            colorClass="icon-primary"
            delay={0}
        />
        <StatsCard
            title="New Today"
            value={stats.newToday.toLocaleString()}
            icon={TrendingUp}
            trend={stats.newToday > 0 ? `+${stats.newToday}` : 'No new'}
            trendDirection={stats.newToday > 0 ? 'up' : 'neutral'}
            colorClass="icon-success"
            delay={60}
        />
        <StatsCard
            title="Sent to Telegram"
            value={stats.sentToTelegram.toLocaleString()}
            icon={CheckCircle}
            trend="Delivered"
            trendDirection="up"
            colorClass="icon-info"
            delay={120}
        />
        <StatsCard
            title="Active Sources"
            value={stats.activeSources.toLocaleString()}
            icon={Globe}
            trend="Portals"
            trendDirection="neutral"
            colorClass="icon-warning"
            delay={180}
        />
    </div>
);

export default StatsCard;
