'use client';

import React from 'react';
import { ShadeVariant, Undertone } from '@/types/catalog';

interface ShadeSwatchGridProps {
  variants: ShadeVariant[];
  selectedVariantId: string | null;
  onSelectVariant: (variant: ShadeVariant) => void;
}

export const ShadeSwatchGrid: React.FC<ShadeSwatchGridProps> = ({
  variants,
  selectedVariantId,
  onSelectVariant
}) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        <label className="text-sm font-semibold text-gray-900" id="shade-selector-label">
          Select Shade ({variants.length} Shades Available)
        </label>
      </div>

      <div
        role="radiogroup"
        aria-labelledby="shade-selector-label"
        className="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 gap-2.5 p-2 bg-neutral-50 rounded-xl border border-neutral-200"
      >
        {variants.map((v) => {
          const isSelected = v.variant_id === selectedVariantId;
          return (
            <button
              key={v.variant_id}
              role="radio"
              aria-checked={isSelected}
              aria-label={`${v.shade_name}, Depth ${v.shade_depth}, ${v.shade_undertone} undertone`}
              tabIndex={isSelected ? 0 : -1}
              onClick={() => onSelectVariant(v)}
              className={`relative group flex flex-col items-center justify-center p-1 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 ${
                isSelected ? 'scale-105 ring-2 ring-black' : 'hover:scale-105'
              }`}
            >
              <span
                className="w-8 h-8 rounded-full border border-black/10 shadow-inner group-hover:shadow-md transition-shadow"
                style={{ backgroundColor: v.shade_hex_code }}
              />
              <span className="mt-1 text-[10px] text-gray-700 truncate max-w-[48px] font-medium">
                {v.shade_depth} {v.shade_undertone[0]}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
