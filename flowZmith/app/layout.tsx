import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Analytics } from '@vercel/analytics/next'
import { SessionProvider } from 'next-auth/react'
import AppKitProvider from '@/contexts/AppKitProvider'
import { SimpleConvexProvider } from "@/components/providers/convex-provider";
import { headers } from 'next/headers'
import './globals.css'
import ContextProvider from '@/context'

export const metadata: Metadata = {
  title: 'Smart Contract AI Builder',
  description: 'AI-powered smart contract generation platform',
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const headersObj = await headers()
  const cookies = headersObj.get('cookie')

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${GeistSans.variable} ${GeistMono.variable}`} style={{fontFamily: GeistSans.style.fontFamily }}>
        <SimpleConvexProvider>
          <AppKitProvider cookies={cookies}>
            <ContextProvider cookies={cookies}>
              <SessionProvider>{children}</SessionProvider>
            </ContextProvider>
          </AppKitProvider>
        </SimpleConvexProvider>
        <Analytics />
      </body>
    </html>
  );
}
