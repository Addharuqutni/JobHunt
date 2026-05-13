/**
 * Tests for SettingsForm component.
 * Verifies immutable state updates, save/error behavior, and accessibility.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SettingsForm from '../../features/settings/components/SettingsForm';

// Mock the settings API service
vi.mock('../../features/settings/services/settingsApi', () => ({
    fetchSettings: vi.fn(),
    saveSettings: vi.fn(),
    triggerScrape: vi.fn(),
}));

import { fetchSettings, saveSettings, triggerScrape } from '../../features/settings/services/settingsApi';
const mockFetchSettings = vi.mocked(fetchSettings);
const mockSaveSettings = vi.mocked(saveSettings);
const mockTriggerScrape = vi.mocked(triggerScrape);

describe('SettingsForm', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockFetchSettings.mockResolvedValue({
            keywords: 'react, node',
            telegramToken: 'tok123',
            telegramChatId: '-100123',
            scheduleInterval: '4',
            maxResults: '200',
            scrapers: [
                { name: 'Jobstreet', enabled: true, maxPages: 2 },
                { name: 'Glints', enabled: false, maxPages: 1 },
            ],
        });
    });

    it('shows loading state initially', () => {
        mockFetchSettings.mockReturnValue(new Promise(() => {}));
        render(<SettingsForm />);
        expect(screen.getByText('Loading settings...')).toBeInTheDocument();
    });

    it('renders form after settings load', async () => {
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Keywords')).toHaveValue('react, node');
        });

        expect(screen.getByLabelText('Bot Token')).toHaveValue('tok123');
        expect(screen.getByLabelText('Chat ID')).toHaveValue('-100123');
    });

    it('has accessible labels on all form controls', async () => {
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Keywords')).toBeInTheDocument();
        });

        expect(screen.getByLabelText('Bot Token')).toBeInTheDocument();
        expect(screen.getByLabelText('Chat ID')).toBeInTheDocument();
        expect(screen.getByLabelText(/run every/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/max results/i)).toBeInTheDocument();
    });

    it('toggle buttons have switch role and aria-checked', async () => {
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Keywords')).toBeInTheDocument();
        });

        const toggles = screen.getAllByRole('switch');
        expect(toggles.length).toBeGreaterThanOrEqual(2);

        // Jobstreet should be enabled (from mock)
        const jobstreetToggle = screen.getByLabelText('Toggle Jobstreet');
        expect(jobstreetToggle).toHaveAttribute('aria-checked', 'true');

        // Glints should be disabled (from mock)
        const glintsToggle = screen.getByLabelText('Toggle Glints');
        expect(glintsToggle).toHaveAttribute('aria-checked', 'false');
    });

    it('toggling a scraper uses immutable update', async () => {
        const user = userEvent.setup();
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Toggle Glints')).toBeInTheDocument();
        });

        const glintsToggle = screen.getByLabelText('Toggle Glints');
        await user.click(glintsToggle);

        expect(glintsToggle).toHaveAttribute('aria-checked', 'true');
    });

    it('saves settings and shows success toast', async () => {
        mockSaveSettings.mockResolvedValue(undefined);
        const user = userEvent.setup();
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Keywords')).toBeInTheDocument();
        });

        const saveButton = screen.getByRole('button', { name: /save settings/i });
        await user.click(saveButton);

        await waitFor(() => {
            expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument();
        });

        expect(mockSaveSettings).toHaveBeenCalledWith(expect.objectContaining({
            keywords: 'react, node',
            telegramToken: 'tok123',
            telegramChatId: '-100123',
        }));
    });

    it('shows error banner when save fails', async () => {
        mockSaveSettings.mockRejectedValue(new Error('Server error'));
        const user = userEvent.setup();
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Keywords')).toBeInTheDocument();
        });

        const saveButton = screen.getByRole('button', { name: /save settings/i });
        await user.click(saveButton);

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument();
            expect(screen.getByText('Server error')).toBeInTheDocument();
        });
    });

    it('triggers scrape and shows alert on success', async () => {
        mockTriggerScrape.mockResolvedValue(undefined);
        const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});
        const user = userEvent.setup();
        render(<SettingsForm />);

        await waitFor(() => {
            expect(screen.getByLabelText('Keywords')).toBeInTheDocument();
        });

        const runButton = screen.getByRole('button', { name: /run scraper now/i });
        await user.click(runButton);

        await waitFor(() => {
            expect(alertMock).toHaveBeenCalledWith('Scraping pipeline started! Check dashboard for results.');
        });

        alertMock.mockRestore();
    });
});
