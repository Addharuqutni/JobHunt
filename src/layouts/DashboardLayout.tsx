import React from 'react';
import Sidebar from '../components/Navigation/Sidebar';
import Header from '../components/Navigation/Header';

interface DashboardLayoutProps {
    children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
    return (
        <div className="app-container">
            <Sidebar />
            <div className="main-content-wrapper">
                <Header />
                <main className="main-content">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;
