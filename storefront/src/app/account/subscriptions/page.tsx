'use client';

import React, { useState } from 'react';
import { SubscriptionItem } from '@/types/subscription';
import { SubscriptionCard } from '@/components/account/SubscriptionCard';
import { SwapShadeModal } from '@/components/account/SwapShadeModal';

export default function CustomerSubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[]>([
    {
      subscription_id: 'sub_001',
      product_name: 'Luminous Silk Hydrating Foundation',
      shade_name: 'Ivory Fair #10',
      shade_hex: '#F5E3D0',
      cadence_days: 60,
      status: 'ACTIVE',
      next_billing_date: '2026-10-15',
      unit_price: 43.20 // 10% auto-replenish discount
    }
  ]);

  const [activeSwapSub, setActiveSwapSub] = useState<SubscriptionItem | null>(null);

  const handleSkip = (id: string) => {
    setSubscriptions((prev) =>
      prev.map((s) => (s.subscription_id === id ? { ...s, status: 'SKIPPED' } : s))
    );
  };

  const handleSwapVariant = (newShadeName: string, newHex: string) => {
    if (!activeSwapSub) return;
    setSubscriptions((prev) =>
      prev.map((s) =>
        s.subscription_id === activeSwapSub.subscription_id
          ? { ...s, shade_name: newShadeName, shade_hex: newHex }
          : s
      )
    );
    setActiveSwapSub(null);
  };

  return (
    <main className="max-w-4xl mx-auto py-12 px-4 sm:px-6">
      <h1 className="text-2xl font-bold text-gray-900">Your Beauty Regimen & Subscriptions</h1>
      <p className="mt-1 text-sm text-gray-500">
        Manage your auto-replenishment deliveries, swap seasonal shades, or skip shipments with ease.
      </p>

      <div className="mt-8 space-y-6">
        {subscriptions.map((sub) => (
          <SubscriptionCard
            key={sub.subscription_id}
            subscription={sub}
            onSkip={() => handleSkip(sub.subscription_id)}
            onSwapClick={() => setActiveSwapSub(sub)}
          />
        ))}
      </div>

      <SwapShadeModal
        isOpen={activeSwapSub !== null}
        onClose={() => setActiveSwapSub(null)}
        onConfirmSwap={handleSwapVariant}
      />
    </main>
  );
}
