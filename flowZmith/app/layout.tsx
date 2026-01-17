import type { Metadata } from 'next'
import { Manrope, Space_Grotesk, JetBrains_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { SessionProvider } from 'next-auth/react'
import AppKitProvider from '@/contexts/AppKitProvider'
import { SimpleConvexProvider } from "@/components/providers/convex-provider";
import { headers } from 'next/headers'
import './globals.css'
import ContextProvider from '@/context'
import { ThemeProvider } from '@/components/theme-provider'

const manrope = Manrope({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['400', '500', '600', '700'],
})

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['400', '500', '600', '700'],
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500', '600'],
})

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
      <body className={`${manrope.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} font-sans`}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
          <SimpleConvexProvider>
            <AppKitProvider cookies={cookies}>
              <ContextProvider cookies={cookies}>
                <SessionProvider>{children}</SessionProvider>
              </ContextProvider>
            </AppKitProvider>
          </SimpleConvexProvider>
        </ThemeProvider>
        <Analytics />
      </body>
    </html>
  );
}
