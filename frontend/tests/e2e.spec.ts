import { test, expect } from '@playwright/test';

const BASE = 'http://127.0.0.1:5173';

test.describe('Ecotopia E2E', () => {
  test('title screen loads and shows NEW GAME', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForLoadState('networkidle');
    const errors: string[] = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    await page.waitForTimeout(2000);
    const canvas = page.locator('#game-container canvas');
    await expect(canvas).toBeVisible();
    expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0);
  });

  test('backend health check', async ({ request }) => {
    const response = await request.post('http://127.0.0.1:7777/api/games');
    expect(response.ok()).toBeTruthy();
  });

  test('can create a game via API', async ({ request }) => {
    const response = await request.post('http://127.0.0.1:7777/api/games');
    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.id).toBeDefined();
    expect(body.status).toBe('RUNNING');
    expect(body.currentRound).toBe(1);
    expect(body.resources).toBeDefined();
    expect(body.citizens.length).toBeGreaterThan(0);
    expect(body.tiles.length).toBeGreaterThan(0);
  });

  test('game API full flow', async ({ request }) => {
    test.setTimeout(120000);

    // Create game
    const createRes = await request.post('http://127.0.0.1:7777/api/games');
    const game = await createRes.json();
    const gameId = game.id;

    // Get tile actions for a tile
    const actionsRes = await request.get(`http://127.0.0.1:7777/api/games/${gameId}/tiles/0/0/actions`);
    expect(actionsRes.ok()).toBeTruthy();
    const actionsBody = await actionsRes.json();
    const actions = actionsBody.availableActions ?? actionsBody;
    expect(Array.isArray(actions)).toBeTruthy();

    // If there are actions, execute one
    if (actions.length > 0) {
      const execRes = await request.post(`http://127.0.0.1:7777/api/games/${gameId}/tiles/0/0/actions`, {
        data: { action: actions[0] }
      });
      expect(execRes.ok()).toBeTruthy();
    }

    // Submit speech
    const speechRes = await request.post(`http://127.0.0.1:7777/api/games/${gameId}/speech`, {
      data: { text: 'I promise to protect our forests and create green jobs for everyone!' }
    });
    expect(speechRes.ok()).toBeTruthy();
    const speechData = await speechRes.json();
    expect(speechData.citizenReactions).toBeDefined();
    expect(speechData.citizenReactions.length).toBeGreaterThan(0);

    // End round
    const endRes = await request.post(`http://127.0.0.1:7777/api/games/${gameId}/rounds/end`);
    expect(endRes.ok()).toBeTruthy();
    const newState = await endRes.json();
    expect(newState.currentRound).toBe(2);
  });

  test('no console errors on game load', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    await page.goto(BASE);
    await page.waitForTimeout(3000);
    const realErrors = errors.filter(e => !e.includes('favicon') && !e.includes('404'));
    expect(realErrors).toHaveLength(0);
  });

  test('UI overlay exists', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForTimeout(2000);
    const overlay = page.locator('#ui-overlay');
    await expect(overlay).toBeVisible();
  });
});
