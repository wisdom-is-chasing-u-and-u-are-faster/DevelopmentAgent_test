export interface CartItem {
  variant_id: string;
  product_name: string;
  shade_name: string;
  shade_hex: string;
  price: number;
  quantity: number;
}

export type ReservationStatus = 'IDLE' | 'RESERVING' | 'HELD' | 'EXPIRED' | 'CONFLICT';

export interface CartReservationState {
  reservation_id: string | null;
  items: CartItem[];
  status: ReservationStatus;
  expires_at: number | null; // epoch ms
  remaining_seconds: number;
}
