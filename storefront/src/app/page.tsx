'use client';

import React, { useState } from 'react';
import { ShadeSwatchGrid } from '@/components/pdp/ShadeSwatchGrid';
import { CameraSamplerModal } from '@/components/shade-finder/CameraSamplerModal';
import { SlideCartDrawer } from '@/components/cart/SlideCartDrawer';
import { useShadeSelection } from '@/hooks/useShadeSelection';
import { ShadeVariant } from '@/types/catalog';

const SAMPLE_SHADES: ShadeVariant[] = [
  { variant_id: 'v1', sku: 'AURA-FND-01', shade_name: 'Alabaster Fair', shade_hex_code: '#F7E7D5', shade_undertone: 'COOL', finish: 'SATIN', shade_depth: 1, price: 48, in_stock: true },
  { variant_id: 'v2', sku: 'AURA-FND-02', shade_name: 'Ivory Warm', shade_hex_code: '#F3DFC5', shade_undertone: 'WARM', finish: 'SATIN', shade_depth: 2, price: 48, in_stock: true },
  { variant_id: 'v3', sku: 'AURA-FND-03', shade_name: 'Bisque Neutral', shade_hex_code: '#E8CEAE', shade_undertone: 'NEUTRAL', finish: 'SATIN', shade_depth: 3, price: 48, in_stock: true },
  { variant_id: 'v4', sku: 'AURA-FND-04', shade_name: 'Honey Olive', shade_hex_code: '#DEBE95', shade_undertone: 'OLIVE', finish: 'SATIN', shade_depth: 4, price: 48, in_stock: true },
  { variant_id: 'v5', sku: 'AURA-FND-05', shade_name: 'Amber Glow', shade_hex_code: '#C69D71', shade_undertone: 'WARM', finish: 'SATIN', shade_depth: 5, price: 48, in_stock: true },
  { variant_id: 'v6', sku: 'AURA-FND-06', shade_name: 'Caramel Rich', shade_hex_code: '#A5734A', shade_undertone: 'NEUTRAL', finish: 'SATIN', shade_depth: 6, price: 48, in_stock: true },
  { variant_id: 'v7', sku: 'AURA-FND-07', shade_name: 'Mocha Deep', shade_hex_code: '#6E4327', shade_undertone: 'COOL', finish: 'SATIN', shade_depth: 7, price: 48, in_stock: true },
  { variant_id: 'v8', sku: 'AURA-FND-08', shade_name: 'Espresso Eclipse', shade_hex_code: '#442618', shade_undertone: 'NEUTRAL', finish: 'SATIN', shade_depth: 8, price: 48, in_stock: true },
];

export default function HomePage() {
  const {
    selectedVariant,
    setSelectedVariant,
    filterUndertone,
    setFilterUndertone,
    filteredVariants,
    selectByHex
  } = useShadeSelection(SAMPLE_SHADES);

  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);

  return (
    <main className="max-w-6xl mx-auto py-10 px-4 sm:px-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        {/* Left: Product Visual */}
        <div className="bg-white p-8 rounded-3xl border border-gray-200 shadow-sm flex flex-col items-center justify-center">
          <div
            className="w-48 h-64 rounded-2xl shadow-inner flex items-center justify-center border-4 border-white transition-colors duration-500 relative"
            style={{ backgroundColor: selectedVariant?.shade_hex_code || '#F3DFC5' }}
          >
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-2xl pointer-events-none" />
            <span className="font-serif text-white/90 text-2xl font-bold tracking-widest drop-shadow">AURA</span>
          </div>
          <div className="mt-6 text-center">
            <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-neutral-100 text-gray-700">
              {selectedVariant?.shade_undertone} UNDERTONE · DEPTH {selectedVariant?.shade_depth}
            </span>
            <h3 className="mt-2 text-xl font-bold text-gray-900">{selectedVariant?.shade_name}</h3>
            <p className="text-gray-500 text-sm font-mono mt-0.5">{selectedVariant?.shade_hex_code}</p>
          </div>
        </div>

        {/* Right: PDP Controls */}
        <div className="space-y-6">
          <div>
            <span className="text-xs font-bold text-[#D8B2A9] uppercase tracking-wider">Luminous Complexion</span>
            <h1 className="text-3xl font-extrabold text-gray-900 mt-1">Luminous Silk Hydrating Foundation</h1>
            <p className="text-2xl font-bold text-gray-900 mt-2">$48.00 USD</p>
          </div>

          <p className="text-gray-600 text-sm leading-relaxed">
            Formulated with Micro-fil™ technology for an ultra-weightless, buildable medium coverage that blurs imperfections and enhances natural radiance for up to 16 hours.
          </p>

          {/* Undertone Filter Pills */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Filter Undertone</label>
            <div className="flex gap-2">
              {(['ALL', 'WARM', 'COOL', 'NEUTRAL', 'OLIVE'] as const).map((tone) => (
                <button
                  key={tone}
                  onClick={() => setFilterUndertone(tone)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
                    filterUndertone === tone
                      ? 'bg-black text-white border-black'
                      : 'bg-white text-gray-700 border-gray-200 hover:border-gray-400'
                  }`}
                >
                  {tone}
                </button>
              ))}
            </div>
          </div>

          {/* Shade Swatch Grid Component (ARCH-1085) */}
          <ShadeSwatchGrid
            variants={filteredVariants}
            selectedVariantId={selectedVariant?.variant_id || null}
            onSelectVariant={setSelectedVariant}
          />

          {/* AI Shade Camera Finder Trigger (ARCH-1086) */}
          <button
            type="button"
            onClick={() => setIsCameraOpen(true)}
            className="w-full py-3 px-4 rounded-xl border-2 border-dashed border-gray-300 hover:border-black text-gray-700 hover:text-black text-sm font-semibold flex items-center justify-center gap-2 transition bg-white"
          >
            <span>📷</span>
            <span>Scan Face with Camera for AI Shade Match</span>
          </button>

          {/* Actions: Add to Cart & Drawer */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={() => setIsCartOpen(true)}
              className="flex-1 py-4 bg-black text-white font-bold rounded-xl hover:bg-neutral-800 transition shadow-lg text-center"
            >
              Add to Bag & Hold Stock (10 Min)
            </button>
            <a
              href="/checkout"
              className="py-4 px-6 bg-neutral-100 text-gray-900 font-bold rounded-xl hover:bg-neutral-200 transition text-center"
            >
              Express Checkout
            </a>
          </div>

          {/* Direct Link to Subscriptions */}
          <div className="pt-2">
            <a
              href="/account/subscriptions"
              className="text-xs text-gray-500 hover:text-black underline block text-center"
            >
              Manage Auto-Replenishment Subscriptions →
            </a>
          </div>
        </div>
      </div>

      {/* Camera Sampler Modal (ARCH-1086) */}
      <CameraSamplerModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onColorSampled={(hex) => {
          selectByHex(hex);
          setIsCameraOpen(false);
        }}
      />

      {/* Slide Cart Drawer (ARCH-1087) */}
      <SlideCartDrawer
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        onProceedToCheckout={() => {
          window.location.href = '/checkout';
        }}
      />
    </main>
  );
}
