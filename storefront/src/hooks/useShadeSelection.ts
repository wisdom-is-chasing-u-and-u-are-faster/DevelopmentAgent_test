'use client';

import { useState, useMemo } from 'react';
import { ShadeVariant, Undertone } from '@/types/catalog';

export function useShadeSelection(initialVariants: ShadeVariant[]) {
  const [selectedVariant, setSelectedVariant] = useState<ShadeVariant | null>(
    initialVariants.length > 0 ? initialVariants[0] : null
  );
  const [filterUndertone, setFilterUndertone] = useState<Undertone | 'ALL'>('ALL');

  const filteredVariants = useMemo(() => {
    if (filterUndertone === 'ALL') return initialVariants;
    return initialVariants.filter((v) => v.shade_undertone === filterUndertone);
  }, [initialVariants, filterUndertone]);

  const selectByHex = (hex: string) => {
    // Find closest or matching variant
    const match = initialVariants.find((v) => v.shade_hex_code.toLowerCase() === hex.toLowerCase());
    if (match) setSelectedVariant(match);
  };

  return {
    selectedVariant,
    setSelectedVariant,
    filterUndertone,
    setFilterUndertone,
    filteredVariants,
    selectByHex
  };
}
