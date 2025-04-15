export interface IConfig {
  API_BASE_URL: string;
  PAYMENT_ENABLED: boolean;
  MERCHANT_NAME: string;
  VPA_ADDRESS: string;
  DEFAULT_CURRENCY: string;
  IS_DEV: boolean;
}

export const DEFAULT_CONFIG: IConfig = {
  API_BASE_URL: '',
  PAYMENT_ENABLED: true,
  MERCHANT_NAME: 'BPL Default',
  VPA_ADDRESS: 'example@upi',
  DEFAULT_CURRENCY: 'INR',
  IS_DEV: import.meta.env.DEV,
}; 