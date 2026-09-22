'use client';

import React, { useState } from 'react';

export const StripeElementsWrapper: React.FC = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
    }, 1200);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Email</label>
        <input
          type="email"
          required
          placeholder="elena@example.com"
          className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Card Details</label>
        {/* Mock hosted Stripe iframe field */}
        <div className="w-full px-3.5 py-3 rounded-xl border border-gray-300 bg-neutral-50 flex items-center justify-between text-sm text-gray-600 font-mono">
          <span>•••• •••• •••• 4242</span>
          <span>12/28 · CVC</span>
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting || isSuccess}
        className="w-full py-4 bg-black text-white font-bold rounded-xl hover:bg-neutral-800 disabled:opacity-50 transition shadow-lg"
      >
        {isSubmitting ? 'Authorizing Payment...' : isSuccess ? '✅ Order Placed!' : 'Pay $48.00 USD'}
      </button>
    </form>
  );
};
