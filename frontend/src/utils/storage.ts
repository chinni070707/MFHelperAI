/**
 * Local Storage Manager with type safety
 */

export class StorageManager {
  private prefix: string = 'mfhelper_';

  /**
   * Save data to localStorage
   */
  set<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(this.prefix + key, serialized);
    } catch (error) {
      console.error(`Error saving to localStorage: ${key}`, error);
    }
  }

  /**
   * Get data from localStorage
   */
  get<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(this.prefix + key);
      if (item === null) return defaultValue ?? null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(`Error reading from localStorage: ${key}`, error);
      return defaultValue ?? null;
    }
  }

  /**
   * Remove item from localStorage
   */
  remove(key: string): void {
    localStorage.removeItem(this.prefix + key);
  }

  /**
   * Clear all app data from localStorage
   */
  clear(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
      }
    });
  }

  /**
   * Check if key exists
   */
  has(key: string): boolean {
    return localStorage.getItem(this.prefix + key) !== null;
  }
}

// Export singleton instance
export const storage = new StorageManager();
export default storage;
