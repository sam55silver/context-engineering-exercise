import { Title, WatchlistItem, WatchlistPage } from "../api";

type CacheEntry<T> = {
  data: T;
  timestamp: number;
};

type PendingRequest<T> = Promise<T>;

const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

class ApiClient {
  private cache = new Map<string, CacheEntry<any>>();
  private pendingRequests = new Map<string, PendingRequest<any>>();
  private invalidationCallbacks = new Map<string, Set<() => void>>();

  /**
   * Makes an API request with built-in caching and deduplication
   */
  async request<T>(
    url: string,
    options?: RequestInit,
    cacheKey?: string
  ): Promise<T> {
    const key = cacheKey || url;

    // Return cached data if valid
    if (this.cache.has(key)) {
      const cached = this.cache.get(key)!;
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
      }
      this.cache.delete(key);
    }

    // Deduplicate pending requests
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)!;
    }

    // Make the request
    const promise = (async () => {
      const res = await fetch(url, options);
      const data = await res.json();
      this.cache.set(key, { data, timestamp: Date.now() });
      this.pendingRequests.delete(key);
      return data as T;
    })();

    this.pendingRequests.set(key, promise);
    return promise;
  }

  /**
   * Invalidates cache for a specific key
   */
  invalidate(key: string): void {
    this.cache.delete(key);
    this.notifyInvalidation(key);
  }

  /**
   * Invalidates cache for multiple keys
   */
  invalidateMultiple(keys: string[]): void {
    keys.forEach((key) => this.invalidate(key));
  }

  /**
   * Registers a callback to be called when a cache key is invalidated
   */
  onInvalidate(key: string, callback: () => void): () => void {
    if (!this.invalidationCallbacks.has(key)) {
      this.invalidationCallbacks.set(key, new Set());
    }
    this.invalidationCallbacks.get(key)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.invalidationCallbacks.get(key)?.delete(callback);
    };
  }

  private notifyInvalidation(key: string): void {
    this.invalidationCallbacks.get(key)?.forEach((cb) => cb());
  }

  // API Methods

  async fetchCatalog(): Promise<Title[]> {
    return this.request<Title[]>("/api/catalog", undefined, "catalog");
  }

  async fetchWatchlist(page: number, size: number): Promise<WatchlistPage> {
    const cacheKey = `watchlist:${page}:${size}`;
    return this.request<WatchlistPage>(
      `/api/watchlist?page=${page}&size=${size}`,
      undefined,
      cacheKey
    );
  }

  async addToWatchlist(titleId: number): Promise<void> {
    await fetch("/api/watchlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title_id: titleId }),
    });
    // Invalidate affected caches
    this.invalidate("catalog");
    this.invalidateWatchlistCache();
  }

  async markWatched(watchlistId: number, isWatched: boolean): Promise<void> {
    await fetch(`/api/watchlist/${watchlistId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_watched: isWatched }),
    });
    // Invalidate affected caches
    this.invalidateWatchlistCache();
    this.invalidate("recently-watched");
  }

  async fetchRecent(): Promise<WatchlistItem[]> {
    return this.request<WatchlistItem[]>(
      "/api/watchlist/recent",
      undefined,
      "recently-watched"
    );
  }

  private invalidateWatchlistCache(): void {
    // Invalidate all watchlist pages
    const keysToInvalidate: string[] = [];
    this.cache.forEach((_, key) => {
      if (key.startsWith("watchlist:")) {
        keysToInvalidate.push(key);
      }
    });
    this.invalidateMultiple(keysToInvalidate);
  }
}

export const apiClient = new ApiClient();
