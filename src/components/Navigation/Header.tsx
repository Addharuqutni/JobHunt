import React from 'react';
import { Bell, Search, User } from 'lucide-react';
import './Header.css';

const Header: React.FC = () => {
    return (
        <header className="header glass-panel">
            <div className="header-search">
                <div className="search-input-wrapper">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        placeholder="Search jobs, companies, or keywords..."
                        className="search-input"
                    />
                </div>
            </div>

            <div className="header-actions">
                <div className="status-indicator">
                    <span className="pulse-dot"></span>
                    <span className="status-text">Next scraping: 2h 30m</span>
                </div>

                <button className="icon-button notification-btn">
                    <Bell size={20} />
                    <span className="badge">3</span>
                </button>

                <div className="user-profile">
                    <div className="avatar">
                        <User size={18} />
                    </div>
                    <div className="user-info">
                        <span className="user-name">Admin</span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
