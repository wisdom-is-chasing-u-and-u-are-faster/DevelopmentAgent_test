'use client';

import React from 'react';

export const DigitalWalletButton: React.FC = () => {
  return (
    <div className="w-full">
      <button
        type="button"
        onClick={() => alert('Apple Pay / Google Pay express checkout initiated')}
        className="w-full py-3.5 bg-black text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-gray-900 transition shadow"
      >
        <span>Pay</span>
        <span className="text-gray-400">|</span>
        <span>G Pay</span>
      </button>
    </div>
  );
};
