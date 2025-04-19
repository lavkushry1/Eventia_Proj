// Unified configuration pulled from Vite environment variables
export interface AppConfig {
  API_BASE_URL: string;
  PAYMENT_VPA: string;
  ENABLE_QR: boolean;
  DOMAIN: string;
  MERCHANT_NAME: string;
  PAYMENT_ENABLED: boolean;
  QR_IMAGE_URL: string;
  ENV: string;
}

// Default configuration
const defaultConfig: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || '',
  PAYMENT_VPA: import.meta.env.VITE_PAYMENT_VPA || '',
  ENABLE_QR: import.meta.env.VITE_ENABLE_QR === 'true',
  DOMAIN: import.meta.env.VITE_DOMAIN || '',
  MERCHANT_NAME: import.meta.env.VITE_MERCHANT_NAME || '',
  PAYMENT_ENABLED: import.meta.env.VITE_PAYMENT_ENABLED === 'true',
  QR_IMAGE_URL: import.meta.env.VITE_QR_IMAGE_URL || '',
  ENV: import.meta.env.MODE
};

// Configuration manager
const configManager = {
  _config: { ...defaultConfig },
  
  // Initialize configuration, potentially from a remote source
  async init(): Promise<AppConfig> {
    try {
      // Here you could fetch remote config and merge with defaults
      // For now, just returning the default config
      this._config = { ...defaultConfig };
      return this._config;
    } catch (error) {
      console.error('Failed to initialize configuration:', error);
      return this._config;
    }
  },
  
  // Get current configuration
  config(): AppConfig {
    return this._config;
  }
};

export default configManager;
