import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Automatically cleanup after each test
afterEach(() => {
  cleanup();
});

// Extend Vitest's expect with React Testing Library's expect
expect.extend({
  // Add any custom matchers here
}); 