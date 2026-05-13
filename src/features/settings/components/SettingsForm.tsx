import React, { useState, useEffect } from 'react';
import { Save, Bot, Globe, Clock, Key, Bell, Shield, RefreshCw, Zap, Database } from 'lucide-react';
import { fetchSettings, saveSettings, triggerScrape } from '../services/settingsApi';
import type { ScraperConfig } from '../types';
import '../styles/Settings.css';

/**
 * SettingsForm — full settings page component.
 * Manages scraper sources, keywords, Telegram config, and schedule.
 */
const SettingsForm: React.FC = () => {
    const [keywords, setKeywords] = useState('full stack developer, frontend developer');
    const [telegramToken, setTelegramToken] = useState('');
    const [telegramChatId, setTelegramChatId] = useState('');
    const [scheduleInterval, setScheduleInterval] = useState('2');
    const [maxResults, setMaxResults] = useState('100');
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [scrapers, setScrapers] = useState<ScraperConfig[]>([
        { enabled: true, name: 'Jobstreet', maxPages: 1 },
        { enabled: true, name: 'Glints', maxPages: 1 },
        { enabled: true, name: 'Kalibrr', maxPages: 1 },
        { enabled: true, name: 'Dealls', maxPages: 1 },
    ]);

    useEffect(() => {
        const loadSettings = async () => {
            try {
                const data = await fetchSettings();
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
                        if (Array.isArray(savedScrapers)) {
                            setScrapers(prevScrapers => {
                                const merged = prevScrapers.map(scraper => {
                                    const saved = savedScrapers.find((s: ScraperConfig) => s.name === scraper.name);
                                    return saved ? { ...scraper, ...saved } : scraper;
                                });
                                // Add any new scrapers from backend not in defaults
                                savedScrapers.forEach((s: ScraperConfig) => {
                                    if (!merged.find(m => m.name === s.name)) {
                                        merged.push(s);
                                    }
                                });
                                return merged;
                            });
                        }
                    } catch { /* keep defaults */ }
                }
            } catch (err) {
                const message = err instanceof Error ? err.message : 'Failed to load settings';
                setError(message);
                console.error('Failed to load settings:', err);
            } finally {
                setLoading(false);
            }
        };
        loadSettings();
    }, []);

    /** Immutable toggle — creates new array with new object at index. */
    const toggleScraper = (index: number) => {
        setScrapers(current =>
            current.map((scraper, i) =>
                i === index ? { ...scraper, enabled: !scraper.enabled } : scraper
            )
        );
    };

    /** Immutable maxPages update. */
    const updateMaxPages = (index: number, value: number) => {
        setScrapers(current =>
            current.map((scraper, i) =>
                i === index ? { ...scraper, maxPages: value } : scraper
            )
        );
    };

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        try {
            await saveSettings({
                keywords,
                telegramToken,
                telegramChatId,
                scheduleInterval,
                maxResults,
                scrapers,
            });
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Could not save settings.';
            setError(message);
            console.error('Failed to save settings:', err);
        } finally {
            setSaving(false);
        }
    };

    const handleRunNow = async () => {
        try {
            await triggerScrape();
            alert('Scraping pipeline started! Check dashboard for results.');
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Could not connect to backend.';
            alert(message);
        }
    };

    if (loading) {
        return (
            <div className="settings-page animate-fade-in">
                <div className="loading-state" aria-live="polite">
                    <RefreshCw size={32} className="spin" aria-hidden="true" />
                    <p>Loading settings...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="settings-page animate-fade-in">
            <div className="settings-header">
                <div>
                    <h2 className="page-title">Settings</h2>
                    <p className="page-subtitle">Configure your scraping pipeline and notifications.</p>
                </div>
                <div className="settings-actions">
                    <button className="btn btn-secondary" onClick={handleRunNow}>
                        <Zap size={16} aria-hidden="true" />
                        Run Scraper Now
                    </button>
                    <button className="btn btn-primary" onClick={handleSave} disabled={saving} aria-busy={saving}>
                        <Save size={16} aria-hidden="true" />
                        {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Settings'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-banner glass-panel" role="alert">
                    <p>{error}</p>
                    <button className="btn btn-secondary" onClick={() => setError(null)}>Dismiss</button>
                </div>
            )}

            <div className="settings-grid">
                {/* Scraper Sources */}
                <div className="settings-section glass-panel">
                    <div className="section-header">
                        <Globe size={20} className="section-icon" aria-hidden="true" />
                        <h3>Scraper Sources</h3>
                    </div>
                    <p className="section-desc">Enable or disable individual job portals and configure their depth.</p>

                    <div className="scraper-list">
                        {scrapers.map((scraper, idx) => (
                            <div key={scraper.name} className={`scraper-item ${scraper.enabled ? 'enabled' : 'disabled'}`}>
                                <div className="scraper-info">
                                    <div>
                                        <span className="scraper-name">{scraper.name}</span>
                                        <span className="scraper-status">
                                            {scraper.enabled ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                </div>
                                <div className="scraper-controls">
                                    <div className="pages-control">
                                        <label htmlFor={`pages-${scraper.name}`}>Pages:</label>
                                        <select
                                            id={`pages-${scraper.name}`}
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
                                        role="switch"
                                        aria-checked={scraper.enabled}
                                        aria-label={`Toggle ${scraper.name}`}
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
                        <Key size={20} className="section-icon" aria-hidden="true" />
                        <h3>Search Keywords</h3>
                    </div>
                    <p className="section-desc">Comma-separated list of keywords to search across all portals.</p>

                    <label htmlFor="keywords-input" className="sr-only">Keywords</label>
                    <textarea
                        id="keywords-input"
                        className="settings-textarea"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        rows={4}
                        placeholder="e.g. react developer, frontend engineer, fullstack"
                    />
                    <div className="keyword-tags" aria-label="Active keywords">
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
                        <Bot size={20} className="section-icon" aria-hidden="true" />
                        <h3>Telegram Bot</h3>
                    </div>
                    <p className="section-desc">Connect to your Telegram bot for real-time job alerts.</p>

                    <div className="form-group">
                        <label className="form-label" htmlFor="telegram-token">
                            <Shield size={14} aria-hidden="true" />
                            Bot Token
                        </label>
                        <input
                            id="telegram-token"
                            type="password"
                            className="form-input"
                            value={telegramToken}
                            onChange={(e) => setTelegramToken(e.target.value)}
                            placeholder="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
                            autoComplete="off"
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="telegram-chat-id">
                            <Bell size={14} aria-hidden="true" />
                            Chat ID
                        </label>
                        <input
                            id="telegram-chat-id"
                            type="text"
                            className="form-input"
                            value={telegramChatId}
                            onChange={(e) => setTelegramChatId(e.target.value)}
                            placeholder="-1001234567890"
                        />
                    </div>

                    <div className="telegram-status">
                        <span className={`connection-dot ${telegramToken && telegramChatId ? 'connected' : 'disconnected'}`} aria-hidden="true" />
                        <span>
                            {telegramToken && telegramChatId ? 'Configured — ready to send' : 'Not configured'}
                        </span>
                    </div>
                </div>

                {/* Schedule */}
                <div className="settings-section glass-panel">
                    <div className="section-header">
                        <Clock size={20} className="section-icon" aria-hidden="true" />
                        <h3>Schedule & Limits</h3>
                    </div>
                    <p className="section-desc">Configure how frequently the scrapers run and result limits.</p>

                    <div className="form-group">
                        <label className="form-label" htmlFor="schedule-interval">
                            <RefreshCw size={14} aria-hidden="true" />
                            Run every (hours)
                        </label>
                        <div className="range-group">
                            <input
                                id="schedule-interval"
                                type="range"
                                min="1"
                                max="24"
                                value={scheduleInterval}
                                onChange={(e) => setScheduleInterval(e.target.value)}
                                className="range-input"
                                aria-valuemin={1}
                                aria-valuemax={24}
                                aria-valuenow={Number(scheduleInterval)}
                            />
                            <span className="range-value" aria-live="polite">{scheduleInterval}h</span>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="max-results">
                            <Database size={14} aria-hidden="true" />
                            Max results per scraper
                        </label>
                        <input
                            id="max-results"
                            type="number"
                            className="form-input"
                            value={maxResults}
                            onChange={(e) => setMaxResults(e.target.value)}
                            min={10}
                            max={500}
                        />
                    </div>

                    <div className="schedule-info">
                        <Clock size={14} aria-hidden="true" />
                        <span>Estimated next run: {scheduleInterval} hours from last execution</span>
                    </div>
                </div>
            </div>

            {/* Save feedback */}
            {saved && (
                <div className="save-toast animate-fade-in" role="status" aria-live="polite">
                    <Save size={16} aria-hidden="true" />
                    Settings saved successfully!
                </div>
            )}
        </div>
    );
};

export default SettingsForm;
