import { gameState } from './GameStateManager.ts';

export class TileActionCache {
  private cache = new Map<string, string[]>();
  private pending = new Map<string, Promise<string[]>>();

  private key(x: number, y: number): string {
    return `${x},${y}`;
  }

  hasCache(x: number, y: number): boolean {
    return this.cache.has(this.key(x, y));
  }

  getCached(x: number, y: number): string[] | null {
    return this.cache.get(this.key(x, y)) ?? null;
  }

  async getActions(x: number, y: number): Promise<string[]> {
    const k = this.key(x, y);

    const cached = this.cache.get(k);
    if (cached) return cached;

    // Deduplicate in-flight requests
    const inflight = this.pending.get(k);
    if (inflight) return inflight;

    const promise = gameState.getTileActions(x, y).then((actions) => {
      this.cache.set(k, actions);
      this.pending.delete(k);
      return actions;
    }).catch((err) => {
      this.pending.delete(k);
      throw err;
    });

    this.pending.set(k, promise);
    return promise;
  }

  invalidate(): void {
    this.cache.clear();
  }
}
