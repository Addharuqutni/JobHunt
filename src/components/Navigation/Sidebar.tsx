import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Settings, LogOut } from 'lucide-react';
import './Sidebar.css';

const Sidebar: React.FC = () => {
    return (
        <aside className="sidebar glass-panel">
            <div className="sidebar-header">
                <div className="logo-container">
                    <div className="logo-icon">
                        <Briefcase size={24} color="#6366f1" />
                    </div>
                    <h1 className="logo-text text-gradient">JobSentinel</h1>
                </div>
            </div>

            <nav className="sidebar-nav">
                <ul>
                    <li className="nav-item">
                        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <LayoutDashboard size={20} />
                            <span>Dashboard</span>
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/jobs" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <Briefcase size={20} />
                            <span>All Jobs</span>
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/settings" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                            <Settings size={20} />
                            <span>Settings</span>
                        </NavLink>
                    </li>
                </ul>
            </nav>

            <div className="sidebar-footer">
                <button className="nav-button log-out">
                    <LogOut size={20} />
                    <span>Exit</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
