"use client";

import { ReactNode } from "react";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { ConvexProviderWithClerk } from "convex/react-clerk";

interface ConvexClientProviderProps {
  children: ReactNode;
}

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function ConvexClientProvider({ children }: ConvexClientProviderProps) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}
    >
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}

// Alternative provider without Clerk (if using different auth)
export function SimpleConvexProvider({ children }: ConvexClientProviderProps) {
  return (
    <ConvexProvider client={convex}>
      {children}
    </ConvexProvider>
  );
}

// Export the main provider
export { ConvexProvider };