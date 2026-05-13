/**
 * Vitest + React Testing Library global setup.
 * Extends expect with DOM matchers and cleans up after each test.
 */
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
    cleanup();
});
