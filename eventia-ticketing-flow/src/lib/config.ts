interface Config {
  API_BASE_URL: string;
  API_VERSION: string;
  STATIC_URL: string;
  IMAGE_PATHS: {
    events: string;
    teams: string;
    venues: string;
    stadiums: string;
    payments: string;
  };
}

class ConfigManager {
  private config: Config;

  constructor() {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const API_VERSION = 'v1';
    const STATIC_URL = `${API_BASE_URL}/static`;

    this.config = {
      API_BASE_URL,
      API_VERSION,
      STATIC_URL,
      IMAGE_PATHS: {
        events: `${STATIC_URL}/events`,
        teams: `${STATIC_URL}/teams`,
        venues: `${STATIC_URL}/venues`,
        stadiums: `${STATIC_URL}/stadiums`,
        payments: `${STATIC_URL}/payments`,
      },
    };
  }

  public getConfig(): Config {
    return this.config;
  }

  public getImageUrl(type: keyof Config['IMAGE_PATHS'], filename?: string | null): string {
    if (!filename) return '';
    return `${this.config.IMAGE_PATHS[type]}/${filename}`;
  }

  public getApiUrl(path: string): string {
    return `${this.config.API_BASE_URL}/api/${this.config.API_VERSION}${path}`;
  }
}

const configManager = new ConfigManager();
export default configManager; 