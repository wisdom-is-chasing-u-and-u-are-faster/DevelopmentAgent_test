export type Undertone = 'WARM' | 'COOL' | 'NEUTRAL' | 'OLIVE';
export type Finish = 'MATTE' | 'DEWY' | 'SATIN' | 'NATURAL' | 'SHEER';

export interface ShadeVariant {
  variant_id: string;
  sku: string;
  shade_name: string;
  shade_hex_code: string;
  shade_undertone: Undertone;
  finish: Finish;
  shade_depth: number;
  price: number;
  in_stock: boolean;
}

export interface ProductCatalogItem {
  product_id: string;
  name: string;
  slug: string;
  brand: string;
  base_price: number;
  variants: ShadeVariant[];
}
