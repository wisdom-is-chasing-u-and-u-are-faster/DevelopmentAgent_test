'use client';

import React from 'react';
import { StripeElementsWrapper } from '@/components/checkout/StripeElementsWrapper';
import { DigitalWalletButton } from '@/components/checkout/DigitalWalletButton';

export default function CheckoutPage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4 sm:px-6">
      <h1 className="text-3xl font-extrabold text-gray-900">Secure Tokenized Checkout</h1>
      <p className="mt-1 text-sm text-gray-500">
        PCI-DSS Level 1 Compliant 256-bit encrypted transaction
      </p>

      <div className="mt-8 space-y-6">
        <DigitalWalletButton />
        <div className="relative flex py-2 items-center">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="flex-shrink mx-4 text-xs font-semibold text-gray-400">OR PAY WITH CARD</span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>
        <StripeElementsWrapper />
      </div>
    </main>
  );
}
