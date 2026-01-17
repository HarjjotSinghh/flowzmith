"use client";

import { ReactNode } from "react";
import { ConvexProvider, ConvexReactClient } from "convex/react";

interface ConvexClientProviderProps {
  children: ReactNode;
}

// Only initialize Convex client if the URL is provided
const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL;
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null;

// Simple Convex provider for NextAuth integration
export function SimpleConvexProvider({ children }: ConvexClientProviderProps) {
  // If no Convex URL is provided, just render children without Convex
  if (!convex) {
    console.warn("NEXT_PUBLIC_CONVEX_URL not set - Convex functionality disabled");
    return <>{children}</>;
  }

  return (
    <ConvexProvider client={convex}>
      {children}
    </ConvexProvider>
  );
}

// Export the main provider
export { ConvexProvider };