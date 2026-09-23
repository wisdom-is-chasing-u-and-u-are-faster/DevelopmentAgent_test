'use client';

import React, { useState } from 'react';

interface SwapShadeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmSwap: (shadeName: string, hexCode: string) => void;
}

const SHADE_OPTIONS = [
  { name: 'Ivory Fair #10', hex: '#F5E3D0' },
  { name: 'Golden Warm #20', hex: '#E2B88F' },
  { name: 'Warm Olive #30', hex: '#C89562' },
  { name: 'Espresso Deep #40', hex: '#4D3021' }
];

export const SwapShadeModal: React.FC<SwapShadeModalProps> = ({
  isOpen,
  onClose,
  onConfirmSwap
}) => {
  const [selected, setSelected] = useState(SHADE_OPTIONS[1]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-md p-6 bg-white rounded-2xl shadow-xl">
        <h3 className="text-lg font-bold text-gray-900">Swap Refill Shade</h3>
        <p className="mt-1 text-sm text-gray-500">
          Pick your updated shade for all future replenishment shipments.
        </p>

        <div className="mt-4 space-y-2">
          {SHADE_OPTIONS.map((shade) => (
            <div
              key={shade.name}
              onClick={() => setSelected(shade)}
              className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition ${
                selected.name === shade.name ? 'border-black bg-neutral-50 ring-1 ring-black' : 'border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="w-6 h-6 rounded-full border shadow-xs" style={{ backgroundColor: shade.hex }} />
                <span className="text-sm font-medium text-gray-900">{shade.name}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-black">
            Cancel
          </button>
          <button
            onClick={() => onConfirmSwap(selected.name, selected.hex)}
            className="px-4 py-2 text-sm font-semibold text-white bg-black rounded-xl hover:bg-gray-800"
          >
            Confirm Swap
          </button>
        </div>
      </div>
    </div>
  );
};
