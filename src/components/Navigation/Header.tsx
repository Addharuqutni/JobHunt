import React, { useState, useEffect } from 'react';
import { Menu, Search, Wifi, WifiOff, Clock } from 'lucide-react';
import './Header.css';

interface HeaderProps {
    onMenuClick: () => void;
}

/**
 * Header — provides global search, live clock, and connection status.
 * Functional indicators replace decorative admin elements.
 */
const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
    const [currentTime, setCurrentTime] = useState(new Date());
    const [isOnline, setIsOnline] = useState(navigator.onLine);

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);
        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);
        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString('id-ID', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    const formatDate = (date: Date) => {
        return date.toLocaleDateString('id-ID', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
        });
    };

    return (
        <header className="header glass-panel">
            <button
                type="button"
                className="icon-button menu-button"
                aria-label="Open navigation menu"
                onClick={onMenuClick}
            >
                <Menu size={20} aria-hidden="true" />
            </button>

            <div className="header-search" role="search">
                <label className="sr-only" htmlFor="global-job-search">Search jobs</label>
                <div className="search-input-wrapper">
                    <Search size={18} className="search-icon" aria-hidden="true" />
                    <input
                        id="global-job-search"
                        type="search"
                        placeholder="Search jobs, companies, or keywords..."
                        className="search-input"
                    />
                    <kbd className="search-shortcut">⌘K</kbd>
                </div>
            </div>

            <div className="header-actions">
                <div className={`connection-status ${isOnline ? 'online' : 'offline'}`} aria-label={isOnline ? 'Connected' : 'Disconnected'}>
                    {isOnline ? <Wifi size={14} aria-hidden="true" /> : <WifiOff size={14} aria-hidden="true" />}
                    <span className="connection-label">{isOnline ? 'Connected' : 'Offline'}</span>
                </div>

                <div className="header-clock" aria-live="off">
                    <Clock size={14} aria-hidden="true" />
                    <div className="clock-content">
                        <span className="clock-time">{formatTime(currentTime)}</span>
                        <span className="clock-date">{formatDate(currentTime)}</span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
