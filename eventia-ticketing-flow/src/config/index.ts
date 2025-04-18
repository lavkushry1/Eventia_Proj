import axios from 'axios';

interface IConfig {
  API_BASE_URL: string;
  FRONTEND_URL: string;
  PAYMENT_ENABLED: boolean;
  MERCHANT_NAME: string;
  VPA_ADDRESS: string;
  QR_IMAGE_URL: string;
  DEFAULT_CURRENCY: string;
  ENV: string;
}

interface BackendConfig {
  api_base_url: string;
  payment_enabled: boolean;
  merchant_name: string;
  vpa_address: string;
  default_currency: string;
}

// Default configuration
const defaultConfig: IConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3003',
  FRONTEND_URL: import.meta.env.VITE_FRONTEND_URL || 'http://localhost:3000',
  PAYMENT_ENABLED: import.meta.env.VITE_PAYMENT_ENABLED === 'true',
  MERCHANT_NAME: import.meta.env.VITE_MERCHANT_NAME || 'Eventia Ticketing',
  VPA_ADDRESS: import.meta.env.VITE_VPA_ADDRESS || 'eventia@axis',
  QR_IMAGE_URL: import.meta.env.VITE_QR_IMAGE_URL || '/qr-placeholder.png',
  DEFAULT_CURRENCY: import.meta.env.VITE_DEFAULT_CURRENCY || 'INR',
  ENV: import.meta.env.VITE_NODE_ENV || 'development',
};

// Combine with backend config if available
export class ConfigManager {
  private config: IConfig;
  private loadPromise: Promise<IConfig> | null = null;
  
  constructor() {
    this.config = defaultConfig;
  }

  // Add init method as an alias for loadConfig
  public async init(): Promise<IConfig> {
    return this.loadConfig();
  }

  public async loadConfig(): Promise<IConfig> {
    if (this.loadPromise) {
      return this.loadPromise;
    }

    this.loadPromise = new Promise<IConfig>((resolve) => {
      // Determine the correct API base URL for config
      const apiBaseUrl = this.config.API_BASE_URL;
      const configUrl = apiBaseUrl.endsWith('/api') 
        ? `${apiBaseUrl}/config/public` 
        : `${apiBaseUrl}/api/config/public`;
      
      console.log('Loading config from:', configUrl);
      
      // Try to load config from backend
      fetch(configUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to load config from server');
          }
          return response.json();
        })
        .then(data => {
          console.log('Config loaded from server:', data);
          
          // Merge with default config
          this.config = {
            ...defaultConfig,
            API_BASE_URL: data.api_base_url || defaultConfig.API_BASE_URL,
            PAYMENT_ENABLED: data.payment_enabled !== undefined ? data.payment_enabled : defaultConfig.PAYMENT_ENABLED,
            MERCHANT_NAME: data.merchant_name || defaultConfig.MERCHANT_NAME,
            VPA_ADDRESS: data.vpa_address || defaultConfig.VPA_ADDRESS,
            QR_IMAGE_URL: data.qr_image_url || defaultConfig.QR_IMAGE_URL,
            DEFAULT_CURRENCY: data.default_currency || defaultConfig.DEFAULT_CURRENCY,
          };
          
          resolve(this.config);
        })
        .catch(error => {
          console.warn('Error loading config, using defaults:', error);
          resolve(defaultConfig);
        });
    });

    return this.loadPromise;
  }

  public getConfig(): IConfig {
    return this.config;
  }

  // Check if we're in development mode
  public isDevelopment(): boolean {
    return this.config.ENV === 'development';
  }

  // Check if we're in production mode
  public isProduction(): boolean {
    return this.config.ENV === 'production';
  }

  // Format a path with the API base URL
  public apiUrl(path: string): string {
    const baseUrl = this.config.API_BASE_URL.endsWith('/')
      ? this.config.API_BASE_URL.slice(0, -1)
      : this.config.API_BASE_URL;
    
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${baseUrl}${normalizedPath}`;
  }
}

// Create a singleton instance
const configManager = new ConfigManager();

// Export the singleton
export default configManager;

// Utility function to get config after initialization
export async function getConfig(): Promise<IConfig> {
  return await configManager.loadConfig();
}

// Utility function to get config synchronously (use only after initialization)
export function config(): IConfig {
  return configManager.getConfig();
} 