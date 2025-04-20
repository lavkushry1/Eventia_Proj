/**
 * Configuration management
 * This module handles various application configuration settings
 */

// Default configuration
interface Config {
  apiUrl: string;
  staticUrl: string;
  debug: boolean;
}

// Default configuration values
const defaultConfig: Config = {
  apiUrl: 'http://localhost:3000/api/v1',
  staticUrl: 'http://localhost:3000/static',
  debug: true
};

// Load configuration from environment variables if available
const loadConfig = (): Config => {
  return {
    apiUrl: import.meta.env.VITE_API_URL || defaultConfig.apiUrl,
    staticUrl: import.meta.env.VITE_STATIC_URL || defaultConfig.staticUrl,
    debug: import.meta.env.VITE_DEBUG === 'true' || defaultConfig.debug
  };
};

class ConfigManager {
  private static instance: ConfigManager;
  private _config: Config;

  private constructor() {
    this._config = loadConfig();
  }

  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  public config(): Config {
    return this._config;
  }

  /**
   * Get a full URL to a static asset
   * @param type - The type of asset (events, teams, etc.)
   * @param path - The asset path
   * @returns The full URL to the asset
   */
  public getStaticUrl(type: string, path: string): string {
    if (!path) return '/placeholder.svg';
    
    // Return as is if it's an absolute URL already
    if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('/assets')) {
      return path;
    }
    
    // Ensure path doesn't start with a slash
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    
    // Build and return the static URL
    return `${this._config.staticUrl}/${type}/${cleanPath}`;
  }

  /**
   * Get a full API URL
   * @param path - The API path
   * @returns The full URL to the API endpoint
   */
  public getApiUrl(path: string): string {
    // Ensure path starts with a slash
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${this._config.apiUrl}${cleanPath}`;
  }
}

// Export a singleton instance
const configManager = ConfigManager.getInstance();
export default configManager; 