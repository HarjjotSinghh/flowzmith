import type { Metadata } from 'next'
import { Kode_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { SessionProvider } from 'next-auth/react'
import AppKitProvider from '@/contexts/AppKitProvider'
import { SimpleConvexProvider } from "@/components/providers/convex-provider";
import { WalletProvider } from '@/contexts/WalletProviderHybrid'
import { headers } from 'next/headers'
import './globals.css'
import ContextProvider from '@/context'
import { ThemeProvider } from '@/components/theme-provider'

const mono = Kode_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'FLOWZMITH // AI BUILDER',
  description: 'AI-powered smart contract generation platform for Flow',
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const headersObj = await headers()
  const cookies = headersObj.get('cookie')

  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={`${mono.variable} font-mono selection:bg-accent selection:text-black`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false} forcedTheme="dark">
          <SimpleConvexProvider>
            <AppKitProvider cookies={cookies}>
              <WalletProvider>
                <ContextProvider cookies={cookies}>
                  <SessionProvider>{children}</SessionProvider>
                </ContextProvider>
              </WalletProvider>
            </AppKitProvider>
          </SimpleConvexProvider>
        </ThemeProvider>
        <Analytics />
      </body>
    </html>
  );
}