import React from 'react';
import { Header } from './Header';
import { Footer } from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />
      <main className="flex-1 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
};
