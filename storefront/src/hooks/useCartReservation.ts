'use client';

import { useState, useEffect } from 'react';
import { CartReservationState, CartItem } from '@/types/cart';

export function useCartReservation() {
  const [cart, setCart] = useState<CartReservationState>({
    reservation_id: 'res_sample_01',
    items: [
      {
        variant_id: 'var_01',
        product_name: 'Luminous Silk Foundation',
        shade_name: 'Ivory Fair #10',
        shade_hex: '#F5E3D0',
        price: 48.0,
        quantity: 1
      }
    ],
    status: 'HELD',
    expires_at: Date.now() + 600 * 1000,
    remaining_seconds: 600
  });

  useEffect(() => {
    if (cart.status !== 'HELD' || !cart.expires_at) return;

    const timer = setInterval(() => {
      const diff = Math.max(0, Math.floor((cart.expires_at! - Date.now()) / 1000));
      setCart((prev) => ({
        ...prev,
        remaining_seconds: diff,
        status: diff === 0 ? 'EXPIRED' : 'HELD'
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, [cart.expires_at, cart.status]);

  const removeItem = (variantId: string) => {
    setCart((prev) => ({
      ...prev,
      items: prev.items.filter((i) => i.variant_id !== variantId)
    }));
  };

  const subtotal = cart.items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return { cart, removeItem, subtotal };
}
