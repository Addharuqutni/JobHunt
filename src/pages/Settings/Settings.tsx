import React, { useState, useEffect } from 'react';
import { Save, Bot, Globe, Clock, Key, Bell, Shield, RefreshCw, Zap, Database } from 'lucide-react';
import { API, getHeaders } from '../../config';
import './Settings.css';

interface ScraperConfig {
    enabled: boolean;
    name: string;
    icon: string;
    maxPages: number;
}

const Settings: React.FC = () => {
    const [keywords, setKeywords] = useState('react developer, frontend developer');
    const [telegramToken, setTelegramToken] = useState('');
    const [telegramChatId, setTelegramChatId] = useState('');
    const [scheduleInterval, setScheduleInterval] = useState('6');
    const [maxResults, setMaxResults] = useState('100');
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(true);

    const [scrapers, setScrapers] = useState<ScraperConfig[]>([
        { enabled: true, name: 'Jobstreet', icon: '🏢', maxPages: 1 },
        { enabled: true, name: 'Glints', icon: '✨', maxPages: 3 },
        { enabled: true, name: 'Kalibrr', icon: '🎯', maxPages: 1 },
    ]);

    // Load settings from backend on mount
    useEffect(() => {
        const loadSettings = async () => {
            try {
                const response = await fetch(API.settings(), { headers: getHeaders() });
                if (response.ok) {
                    const data = await response.json();
                    if (data.keywords) setKeywords(data.keywords);
                    if (data.telegramToken) setTelegramToken(data.telegramToken);
                    if (data.telegramChatId) setTelegramChatId(data.telegramChatId);
                    if (data.scheduleInterval) setScheduleInterval(data.scheduleInterval);
                    if (data.maxResults) setMaxResults(data.maxResults);
                    if (data.scrapers) {
                        try {
                            const savedScrapers = typeof data.scrapers === 'string'
                                ? JSON.parse(data.scrapers)
                                : data.scrapers;
                            if (Array.isArray(savedScrapers)) setScrapers(savedScrapers);
                        } catch { /* keep defaults */ }
                    }
                }
            } catch (error) {
                console.error('Failed to load settings:', error);
            } finally {
                setLoading(false);
            }
        };
        loadSettings();
    }, []);

    const toggleScraper = (index: number) => {
        const updated = [...scrapers];
        updated[index].enabled = !updated[index].enabled;
        setScrapers(updated);
    };

    const updateMaxPages = (index: number, value: number) => {
        const updated = [...scrapers];
        updated[index].maxPages = value;
        setScrapers(updated);
    };

    const handleSave = async () => {
        try {
            const response = await fetch(API.settings(), {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    keywords,
                    telegramToken,
                    telegramChatId,
                    scheduleInterval,
                    maxResults,
                    scrapers,
                }),
            });
            if (response.ok) {
                setSaved(true);
                setTimeout(() => setSaved(false), 3000);
            }
        } catch (error) {
            console.error('Failed to save settings:', error);
            alert('Could not save settings. Make sure the API is running.');
        }
    };

    const handleRunNow = async () => {
        try {
            const response = await fetch(API.scrape(), {
                method: 'POST',
                headers: getHeaders()
            });
            if (response.ok) {
                alert('Scraping pipeline started! Check dashboard for results.');
            }
        } catch {
            alert('Could not connect to backend. Make sure api.py is running.');
        }
    };

    return (
        <div className="settings-page animate-fade-in">
            <div className="settings-header">
                <div>
                    <h2 className="page-title">Settings</h2>
                    <p className="page-subtitle">Configure your scraping pipeline and notifications.</p>
                </div>
                <div className="settings-actions">
                    <button className="btn btn-secondary" onClick={handleRunNow}>
                        <Zap size={16} />
                        Run Scraper Now
                    </button>
                    <button className="btn btn-primary" onClick={handleSave}>
                        <Save size={16} />
                        {saved ? 'Saved!' : 'Save Settings'}
                    </button>
                </div>
            </div>

            <div className="settings-grid">
                {/* Scraper Sources */}
                <div className="settings-section glass-panel">
                    <div className="section-header">
                        <Globe size={20} className="section-icon" />
                        <h3>Scraper Sources</h3>
                    </div>
                    <p className="section-desc">Enable or disable individual job portals and configure their depth.</p>

                    <div className="scraper-list">
                        {scrapers.map((scraper, idx) => (
                            <div key={scraper.name} className={`scraper-item ${scraper.enabled ? 'enabled' : 'disabled'}`}>
                                <div className="scraper-info">
                                    <span className="scraper-icon">{scraper.icon}</span>
                                    <div>
                                        <span className="scraper-name">{scraper.name}</span>
                                        <span className="scraper-status">
                                            {scraper.enabled ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                </div>
                                <div className="scraper-controls">
                                    <div className="pages-control">
                                        <label>Pages:</label>
                                        <select
                                            value={scraper.maxPages}
                                            onChange={(e) => updateMaxPages(idx, Number(e.target.value))}
                                            className="mini-select"
                                            disabled={!scraper.enabled}
                                        >
                                            {[1, 2, 3, 5, 10].map(n => (
                                                <option key={n} value={n}>{n}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <button
                                        className={`toggle-btn ${scraper.enabled ? 'on' : 'off'}`}
                                        onClick={() => toggleScraper(idx)}
                                    >
                                        <span className="toggle-knob" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Keywords */}
                <div className="settings-section glass-panel">
                    <div className="section-header">
                        <Key size={20} className="section-icon" />
                        <h3>Search Keywords</h3>
                    </div>
                    <p className="section-desc">Comma-separated list of keywords to search across all portals.</p>

                    <textarea
                        className="settings-textarea"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        rows={4}
                        placeholder="e.g. react developer, frontend engineer, fullstack"
                    />
                    <div className="keyword-tags">
                        {keywords.split(',').map((kw, i) => (
                            kw.trim() && (
                                <span key={i} className="keyword-tag">
                                    {kw.trim()}
                                </span>
                            )
                        ))}
                    </div>
                </div>

                {/* Telegram */}
                <div className="settings-section glass-panel">
                    <div className="section-header">
                        <Bot size={20} className="section-icon" />
                        <h3>Telegram Bot</h3>
                    </div>
                    <p className="section-desc">Connect to your Telegram bot for real-time job alerts.</p>

                    <div className="form-group">
                        <label className="form-label">
                            <Shield size={14} />
                            Bot Token
                        </label>
                        <input
                            type="password"
                            className="form-input"
                            value={telegramToken}
                            onChange={(e) => setTelegramToken(e.target.value)}
                            placeholder="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">
                            <Bell size={14} />
                            Chat ID
                        </label>
                        <input
                            type="text"
                            className="form-input"
                            value={telegramChatId}
                            onChange={(e) => setTelegramChatId(e.target.value)}
                            placeholder="-1001234567890"
                        />
                    </div>

                    <div className="telegram-status">
                        <span className={`connection-dot ${telegramToken && telegramChatId ? 'connected' : 'disconnected'}`} />
                        <span>
                            {telegramToken && telegramChatId ? 'Configured — ready to send' : 'Not configured'}
                        </span>
                    </div>
                </div>

                {/* Schedule */}
                <div className="settings-section glass-panel">
                    <div className="section-header">
                        <Clock size={20} className="section-icon" />
                        <h3>Schedule & Limits</h3>
                    </div>
                    <p className="section-desc">Configure how frequently the scrapers run and result limits.</p>

                    <div className="form-group">
                        <label className="form-label">
                            <RefreshCw size={14} />
                            Run every (hours)
                        </label>
                        <div className="range-group">
                            <input
                                type="range"
                                min="1"
                                max="24"
                                value={scheduleInterval}
                                onChange={(e) => setScheduleInterval(e.target.value)}
                                className="range-input"
                            />
                            <span className="range-value">{scheduleInterval}h</span>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">
                            <Database size={14} />
                            Max results per scraper
                        </label>
                        <input
                            type="number"
                            className="form-input"
                            value={maxResults}
                            onChange={(e) => setMaxResults(e.target.value)}
                            min={10}
                            max={500}
                        />
                    </div>

                    <div className="schedule-info">
                        <Clock size={14} />
                        <span>Estimated next run: {scheduleInterval} hours from last execution</span>
                    </div>
                </div>
            </div>

            {/* Save feedback */}
            {saved && (
                <div className="save-toast animate-fade-in">
                    <Save size={16} />
                    Settings saved successfully!
                </div>
            )}
        </div>
    );
};

export default Settings;
