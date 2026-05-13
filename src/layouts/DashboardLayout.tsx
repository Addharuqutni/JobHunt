import React, { useState } from 'react';
import Sidebar from '../components/Navigation/Sidebar';
import Header from '../components/Navigation/Header';

interface DashboardLayoutProps {
    children: React.ReactNode;
}

/**
 * DashboardLayout owns shell-level navigation state.
 * Keeping mobile sidebar behavior here prevents page components from handling layout concerns.
 */
const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const closeSidebar = () => setIsSidebarOpen(false);

    return (
        <div className="app-container">
            <a className="skip-link" href="#main-content">Skip to main content</a>
            <Sidebar isOpen={isSidebarOpen} onNavigate={closeSidebar} />
            {isSidebarOpen && (
                <button
                    type="button"
                    className="sidebar-backdrop"
                    aria-label="Close navigation menu"
                    onClick={closeSidebar}
                />
            )}
            <div className="main-content-wrapper">
                <Header onMenuClick={() => setIsSidebarOpen(true)} />
                <main id="main-content" className="main-content" tabIndex={-1}>
                    {children}
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;
