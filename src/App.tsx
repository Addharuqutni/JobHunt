import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import DashboardOverview from './features/dashboard/components/DashboardOverview';
import RecentJobsList from './features/dashboard/components/RecentJobsList';
import './App.css';

/**
 * Lazy-loaded route components — reduces initial bundle size by splitting
 * heavy pages (JobList includes xlsx, SettingsForm has complex form logic).
 */
const JobList = lazy(() => import('./features/jobs/components/JobList'));
const SettingsForm = lazy(() => import('./features/settings/components/SettingsForm'));

/** Fallback shown while lazy chunks load. */
function PageLoader() {
    return (
        <div className="loading-state" aria-live="polite">
            <div className="spin" style={{ width: 32, height: 32, border: '3px solid var(--color-border)', borderTopColor: 'var(--color-primary)', borderRadius: '50%' }} />
            <p>Loading...</p>
        </div>
    );
}

/**
 * Root application component.
 * Defines routing and wraps all pages in the dashboard layout.
 */
function App() {
    return (
        <Router>
            <DashboardLayout>
                <Suspense fallback={<PageLoader />}>
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <div className="dashboard-content">
                                    <DashboardOverview />
                                    <RecentJobsList />
                                </div>
                            }
                        />
                        <Route path="/jobs" element={<JobList />} />
                        <Route path="/settings" element={<SettingsForm />} />
                    </Routes>
                </Suspense>
            </DashboardLayout>
        </Router>
    );
}

export default App;
