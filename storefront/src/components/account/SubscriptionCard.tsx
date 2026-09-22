'use client';

import React from 'react';
import { SubscriptionItem } from '@/types/subscription';

interface SubscriptionCardProps {
  subscription: SubscriptionItem;
  onSkip: () => void;
  onSwapClick: () => void;
}

export const SubscriptionCard: React.FC<SubscriptionCardProps> = ({
  subscription,
  onSkip,
  onSwapClick
}) => {
  return (
    <div className="p-6 bg-white rounded-2xl border border-gray-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div className="flex items-center gap-4">
        <span
          className="w-12 h-12 rounded-full border-2 border-white shadow-md"
          style={{ backgroundColor: subscription.shade_hex }}
        />
        <div>
          <h3 className="text-lg font-bold text-gray-900">{subscription.product_name}</h3>
          <p className="text-sm text-gray-600">
            Current Shade: <span className="font-semibold">{subscription.shade_name}</span>
          </p>
          <div className="mt-2 flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Every {subscription.cadence_days} Days
            </span>
            <span className="text-xs text-gray-500">Next refill: {subscription.next_billing_date}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 w-full md:w-auto">
        <button
          onClick={onSwapClick}
          className="flex-1 md:flex-none px-4 py-2 border border-gray-300 text-sm font-semibold text-gray-700 rounded-xl hover:bg-gray-50 transition"
        >
          Swap Shade
        </button>
        <button
          onClick={onSkip}
          className="flex-1 md:flex-none px-4 py-2 border border-gray-300 text-sm font-semibold text-gray-700 rounded-xl hover:bg-gray-50 transition"
        >
          Skip Refill
        </button>
      </div>
    </div>
  );
};
