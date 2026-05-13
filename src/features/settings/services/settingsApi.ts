/**
 * Settings API service — encapsulates settings-related API calls.
 * Uses the shared API client for consistent error handling.
 */
import { get, post } from '../../../shared/services/apiClient';
import { API } from '../../../config/api';
import type { SettingsPayload } from '../types';

interface SettingsResponse {
    keywords?: string;
    telegramToken?: string;
    telegramChatId?: string;
    scheduleInterval?: string;
    maxResults?: string;
    scrapers?: unknown;
}

/**
 * Load current settings from the API.
 */
export async function fetchSettings(): Promise<SettingsResponse> {
    return get<SettingsResponse>(API.settings());
}

/**
 * Save settings to the API.
 */
export async function saveSettings(payload: SettingsPayload): Promise<void> {
    await post(API.settings(), payload);
}

/**
 * Trigger a manual scrape run.
 */
export async function triggerScrape(): Promise<void> {
    await post(API.scrape());
}
