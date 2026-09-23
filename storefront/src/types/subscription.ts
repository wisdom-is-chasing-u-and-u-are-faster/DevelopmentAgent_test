export interface SubscriptionItem {
  subscription_id: string;
  product_name: string;
  shade_name: string;
  shade_hex: string;
  cadence_days: 30 | 45 | 60 | 90;
  status: 'ACTIVE' | 'PAUSED' | 'SKIPPED' | 'CANCELLED';
  next_billing_date: string;
  unit_price: number;
}
