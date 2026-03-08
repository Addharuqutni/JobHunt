import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import DashboardOverview from './components/Dashboard/DashboardOverview';
import JobList from './components/Dashboard/JobList';
import AllJobs from './pages/AllJobs/AllJobs';
import Settings from './pages/Settings/Settings';
import './App.css';

function App() {
    return (
        <Router>
            <DashboardLayout>
                <Routes>
                    <Route
                        path="/"
                        element={
                            <div className="dashboard-content">
                                <DashboardOverview />
                                <JobList />
                            </div>
                        }
                    />
                    <Route path="/jobs" element={<AllJobs />} />
                    <Route path="/settings" element={<Settings />} />
                </Routes>
            </DashboardLayout>
        </Router>
    );
}

export default App;
