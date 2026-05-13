/**
 * TypeScript types for the Settings feature.
 */

/** Scraper configuration for a single source. */
export interface ScraperConfig {
    name: string;
    enabled: boolean;
    maxPages: number;
}

/** Application settings shape. */
export interface AppSettings {
    keywords?: string;
    telegramToken?: string;
    telegramChatId?: string;
    scrapers?: ScraperConfig[];
    [key: string]: unknown;
}

/** Payload sent to the settings API on save. */
export interface SettingsPayload {
    keywords: string;
    telegramToken: string;
    telegramChatId: string;
    scheduleInterval: string;
    maxResults: string;
    scrapers: ScraperConfig[];
}
