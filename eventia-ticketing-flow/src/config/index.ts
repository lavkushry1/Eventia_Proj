import { z } from "zod";

/**
 * Configuration manager for Eventia Frontend
 * Centralizes all configuration settings for the application
 */

// Define the shape of our configuration using Zod for type validation
const ConfigSchema = z.object({
  API_BASE_URL: z.string().url(),
  MERCHANT_NAME: z.string().default("Eventia Payments"),
  PAYMENT_VPA: z.string().default("eventia@upi"),
  PAYMENT_ENABLED: z.boolean().default(true),
  QR_IMAGE_URL: z.string().optional(),
  
  // Static asset paths
  STATIC_BASE_PATH: z.string().default("/static"),
  TEAM_LOGOS_PATH: z.string().default("/static/teams"),
  EVENT_IMAGES_PATH: z.string().default("/static/events"),
  STADIUM_IMAGES_PATH: z.string().default("/static/stadiums"),
  PAYMENT_QR_PATH: z.string().default("/static/payments"),
  
  // Default placeholders
  DEFAULT_TEAM_LOGO: z.string().default("/static/placeholders/team_placeholder.png"),
  DEFAULT_EVENT_IMAGE: z.string().default("/static/placeholders/event_placeholder.png"),
  DEFAULT_STADIUM_IMAGE: z.string().default("/static/placeholders/stadium_placeholder.png"),
  
  // App behavior settings
  REFRESH_INTERVAL: z.number().default(300000), // 5 minutes in milliseconds
  MAX_BOOKING_TIME: z.number().default(600000), // 10 minutes in milliseconds
});

// Type for our config object
type Config = z.infer<typeof ConfigSchema>;

class ConfigManager {
  private _config: Config | null = null;
  
  /**
   * Initialize configuration from environment variables
   */
  async init(): Promise<Config> {
    try {
      // Load from environment variables (Vite exposes these with import.meta.env)
      const envConfig = {
        API_BASE_URL: import.meta.env.VITE_API_BASE_URL || window.location.origin,
        MERCHANT_NAME: import.meta.env.VITE_MERCHANT_NAME || "Eventia Payments",
        PAYMENT_VPA: import.meta.env.VITE_PAYMENT_VPA || "eventia@upi",
        PAYMENT_ENABLED: import.meta.env.VITE_PAYMENT_ENABLED === "true",
        QR_IMAGE_URL: import.meta.env.VITE_QR_IMAGE_URL || null,
        STATIC_BASE_PATH: import.meta.env.VITE_STATIC_BASE_PATH || "/static",
        REFRESH_INTERVAL: Number(import.meta.env.VITE_REFRESH_INTERVAL || 300000),
        MAX_BOOKING_TIME: Number(import.meta.env.VITE_MAX_BOOKING_TIME || 600000),
      };
      
      // Parse and validate the config
      this._config = ConfigSchema.parse(envConfig);
      
      // Derive the static paths from the base path
      this._config.TEAM_LOGOS_PATH = `${this._config.STATIC_BASE_PATH}/teams`;
      this._config.EVENT_IMAGES_PATH = `${this._config.STATIC_BASE_PATH}/events`;
      this._config.STADIUM_IMAGES_PATH = `${this._config.STATIC_BASE_PATH}/stadiums`;
      this._config.PAYMENT_QR_PATH = `${this._config.STATIC_BASE_PATH}/payments`;
      
      console.log("Config initialized:", this._config);
      return this._config;
    } catch (error) {
      console.error("Error initializing config:", error);
      
      // Fallback to default config
      this._config = {
        API_BASE_URL: window.location.origin,
        MERCHANT_NAME: "Eventia Payments",
        PAYMENT_VPA: "eventia@upi",
        PAYMENT_ENABLED: true,
        QR_IMAGE_URL: null,
        STATIC_BASE_PATH: "/static",
        TEAM_LOGOS_PATH: "/static/teams",
        EVENT_IMAGES_PATH: "/static/events",
        STADIUM_IMAGES_PATH: "/static/stadiums",
        PAYMENT_QR_PATH: "/static/payments",
        DEFAULT_TEAM_LOGO: "/static/placeholders/team_placeholder.png",
        DEFAULT_EVENT_IMAGE: "/static/placeholders/event_placeholder.png",
        DEFAULT_STADIUM_IMAGE: "/static/placeholders/stadium_placeholder.png",
        REFRESH_INTERVAL: 300000,
        MAX_BOOKING_TIME: 600000,
      };
      
      return this._config;
    }
  }
  
  /**
   * Get the current configuration
   */
  config(): Config {
    if (!this._config) {
      throw new Error("Config not initialized. Call init() first.");
    }
    return this._config;
  }
  
  /**
   * Get a static URL for an asset
   * @param type The type of asset (teams, events, stadiums, payments)
   * @param filename The filename of the asset
   * @returns The full URL to the asset
   */
  getStaticUrl(type: 'teams' | 'events' | 'stadiums' | 'payments', filename: string): string {
    if (!this._config) {
      throw new Error("Config not initialized. Call init() first.");
    }
    
    // If the filename already includes http:// or https://, return it as is
    if (filename.startsWith('http://') || filename.startsWith('https://')) {
      return filename;
    }
    
    // If the filename already includes the static path, don't add it again
    if (filename.startsWith(this._config.STATIC_BASE_PATH)) {
      return this._config.API_BASE_URL + filename;
    }
    
    // Get the appropriate static path based on the type
    let staticPath: string;
    let defaultImage: string;
    
    switch (type) {
      case 'teams':
        staticPath = this._config.TEAM_LOGOS_PATH;
        defaultImage = this._config.DEFAULT_TEAM_LOGO;
        break;
      case 'events':
        staticPath = this._config.EVENT_IMAGES_PATH;
        defaultImage = this._config.DEFAULT_EVENT_IMAGE;
        break;
      case 'stadiums':
        staticPath = this._config.STADIUM_IMAGES_PATH;
        defaultImage = this._config.DEFAULT_STADIUM_IMAGE;
        break;
      case 'payments':
        staticPath = this._config.PAYMENT_QR_PATH;
        defaultImage = ''; // No default for payments
        break;
    }
    
    // If filename is 'placeholder.png', return the default image
    if (filename === 'placeholder.png' && defaultImage) {
      return this._config.API_BASE_URL + defaultImage;
    }
    
    // Construct the full URL
    return `${this._config.API_BASE_URL}${staticPath}/${filename}`;
  }
}

// Export singleton instance
const configManager = new ConfigManager();
export default configManager;
