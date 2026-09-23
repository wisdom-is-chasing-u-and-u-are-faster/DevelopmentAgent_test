import React from 'react';
import './globals.css';

export const metadata = {
  title: 'AURA Cosmetics | Next.js Enterprise Storefront (PR 1)',
  description: 'Enterprise MACH Storefront built with Next.js 14 and React 18 TypeScript',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#F8F5F2] text-[#2D2D2D] antialiased">
        <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-gray-200">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" className="font-extrabold text-xl tracking-tight text-gray-900 flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-[#D8B2A9]"></span>
              AURA COSMETICS <span className="text-xs px-2 py-0.5 rounded bg-black text-white font-mono">Next.js 14</span>
            </a>
            <nav className="flex items-center gap-6 text-sm font-semibold">
              <a href="/" className="hover:text-black text-gray-700">PDP & Shade Swatches</a>
              <a href="/checkout" className="hover:text-black text-gray-700">Checkout</a>
              <a href="/account/subscriptions" className="hover:text-black text-gray-700">Subscriptions</a>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
