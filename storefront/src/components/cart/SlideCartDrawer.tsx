'use client';

import React from 'react';
import { useCartReservation } from '@/hooks/useCartReservation';
import { ReservationCountdown } from './ReservationCountdown';

interface SlideCartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onProceedToCheckout: () => void;
}

export const SlideCartDrawer: React.FC<SlideCartDrawerProps> = ({
  isOpen,
  onClose,
  onProceedToCheckout
}) => {
  const { cart, removeItem, subtotal } = useCartReservation();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs">
      <div className="w-full max-w-md h-full bg-white shadow-2xl flex flex-col p-6 animate-slide-left">
        <div className="flex items-center justify-between border-b pb-4">
          <h2 className="text-xl font-bold text-gray-900">Your Beauty Bag</h2>
          <button onClick={onClose} className="p-2 text-gray-500 hover:text-black">
            ✕
          </button>
        </div>

        {/* Live 10-Minute Reservation Timer */}
        {cart.status === 'HELD' && (
          <div className="my-4">
            <ReservationCountdown remainingSeconds={cart.remaining_seconds} />
          </div>
        )}

        <div className="flex-1 overflow-y-auto divide-y divide-gray-100 my-4">
          {cart.items.length === 0 ? (
            <div className="text-center py-12 text-gray-500">Your bag is empty</div>
          ) : (
            cart.items.map((item) => (
              <div key={item.variant_id} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full border shadow-xs" style={{ backgroundColor: item.shade_hex }} />
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900">{item.product_name}</h4>
                    <p className="text-xs text-gray-500">{item.shade_name} · Qty: {item.quantity}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-gray-900">${(item.price * item.quantity).toFixed(2)}</span>
                  <button
                    onClick={() => removeItem(item.variant_id)}
                    className="block text-xs text-red-500 hover:underline mt-1"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="border-t pt-4">
          <div className="flex justify-between text-base font-bold text-gray-900 mb-4">
            <span>Estimated Total:</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>
          <button
            onClick={onProceedToCheckout}
            disabled={cart.items.length === 0 || cart.status === 'EXPIRED'}
            className="w-full py-3.5 bg-black text-white font-semibold rounded-xl hover:bg-gray-800 disabled:opacity-50 transition-all shadow-lg"
          >
            Checkout with 1-Click
          </button>
        </div>
      </div>
    </div>
  );
};
