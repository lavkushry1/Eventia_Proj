interface Config {
  API_BASE_URL: string;
  FRONTEND_BASE_URL: string;
  STATIC_BASE_URL: string;
  TEAM_LOGOS_PATH: string;
  EVENT_IMAGES_PATH: string;
  STADIUM_IMAGES_PATH: string;
  PAYMENT_QR_PATH: string;
  UPLOADS_PATH: string;
  DEFAULT_PAGE_SIZE: number;
  MAX_PAGE_SIZE: number;
  ENABLE_ANALYTICS: boolean;
  ENABLE_DEBUG: boolean;
}

const config: Config = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  FRONTEND_BASE_URL: import.meta.env.VITE_FRONTEND_BASE_URL || 'http://localhost:5173',
  STATIC_BASE_URL: import.meta.env.VITE_STATIC_BASE_URL || 'http://localhost:8000/static',
  TEAM_LOGOS_PATH: '/teams',
  EVENT_IMAGES_PATH: '/events',
  STADIUM_IMAGES_PATH: '/stadiums',
  PAYMENT_QR_PATH: '/payments',
  UPLOADS_PATH: '/uploads',
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true',
};

export default config; 