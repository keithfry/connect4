import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8080',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'sh',
      args: ['-c', 'cd backend && ../.venv/bin/python manage.py runserver 0.0.0.0:8000'],
      url: 'http://127.0.0.1:8000/health/',
      reuseExistingServer: !process.env.CI,
      stdout: 'pipe',
      stderr: 'pipe',
      timeout: 20000, // 20 seconds for server startup
    },
    {
      command: 'sh',
      args: ['-c', 'cd frontend && python3 -m http.server 8080'],
      url: 'http://127.0.0.1:8080/',
      reuseExistingServer: !process.env.CI,
      stdout: 'pipe',
      stderr: 'pipe',
      timeout: 10000, // 10 seconds for frontend server
    },
  ],
});

