'use client';

import React from 'react';

interface ReservationCountdownProps {
  remainingSeconds: number;
}

export const ReservationCountdown: React.FC<ReservationCountdownProps> = ({ remainingSeconds }) => {
  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;
  const isUrgent = remainingSeconds < 120; // Under 2 minutes warning

  return (
    <div
      role="status"
      aria-live="polite"
      className={`p-3 rounded-xl border flex items-center justify-between text-sm transition-colors ${
        isUrgent
          ? 'bg-amber-50 border-amber-300 text-amber-900 animate-pulse'
          : 'bg-emerald-50 border-emerald-300 text-emerald-900'
      }`}
    >
      <span className="font-medium">
        {isUrgent ? '⚠️ Flash drop stock expiring soon:' : '✨ Stock items reserved for:'}
      </span>
      <span className="font-mono font-bold text-base">
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
    </div>
  );
};
