import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Settings, Activity, Zap } from 'lucide-react';
import './Sidebar.css';

interface SidebarProps {
    isOpen: boolean;
    onNavigate: () => void;
}

const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
    { to: '/jobs', label: 'All Jobs', icon: Briefcase },
    { to: '/settings', label: 'Settings', icon: Settings },
];

/**
 * Sidebar — primary navigation with pipeline status and branding.
 * Supports mobile drawer via isOpen prop.
 */
const Sidebar: React.FC<SidebarProps> = ({ isOpen, onNavigate }) => {
    return (
        <>
            {/* Mobile backdrop */}
            {isOpen && (
                <div
                    className="sidebar-backdrop"
                    onClick={onNavigate}
                    aria-hidden="true"
                />
            )}

            <aside className={`sidebar glass-panel ${isOpen ? 'open' : ''}`} aria-label="Primary navigation">
                {/* Brand */}
                <div className="sidebar-header">
                    <div className="logo-container">
                        <div className="logo-icon" aria-hidden="true">
                            <Zap size={20} />
                        </div>
                        <div className="logo-text-group">
                            <h1 className="logo-text text-gradient">JobSentinel</h1>
                            <span className="logo-version">v2.0</span>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="sidebar-nav">
                    <span className="nav-section-label">Menu</span>
                    <ul>
                        {navItems.map(({ to, label, icon: Icon, end }) => (
                            <li className="nav-item" key={to}>
                                <NavLink
                                    to={to}
                                    end={end}
                                    onClick={onNavigate}
                                    className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                                >
                                    <span className="nav-icon-wrapper">
                                        <Icon size={18} aria-hidden="true" />
                                    </span>
                                    <span className="nav-label">{label}</span>
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </nav>

                {/* Pipeline Status */}
                <div className="sidebar-footer">
                    <div className="pipeline-card">
                        <div className="pipeline-header">
                            <Activity size={14} className="pipeline-icon" aria-hidden="true" />
                            <span className="pipeline-title">Pipeline Status</span>
                        </div>
                        <div className="pipeline-body">
                            <div className="pipeline-indicator">
                                <span className="pipeline-dot" aria-hidden="true" />
                                <span className="pipeline-status">All systems operational</span>
                            </div>
                            <div className="pipeline-metrics">
                                <div className="metric">
                                    <span className="metric-value">4</span>
                                    <span className="metric-label">Sources</span>
                                </div>
                                <div className="metric-divider" />
                                <div className="metric">
                                    <span className="metric-value">2h</span>
                                    <span className="metric-label">Interval</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
