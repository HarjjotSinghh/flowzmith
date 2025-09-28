import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Analytics } from '@vercel/analytics/next'
import { SessionProvider } from 'next-auth/react'
import AppKitProvider from '@/contexts/AppKitProvider'
import { headers } from 'next/headers'
import './globals.css'
import ContextProvider from '@/context'

export const metadata: Metadata = {
  title: 'Smart Contract AI Builder',
  description: 'AI-powered smart contract generation platform',
  generator: 'v0.app',
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const headersObj = await headers()
  const cookies = headersObj.get('cookie')

  return (
    <html lang="en">
      <head>
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}
        `}</style>
      </head>
      <body>
        <AppKitProvider cookies={cookies}>
        <ContextProvider cookies={cookies}>
          <SessionProvider>
              {children}
            </SessionProvider>
          </ContextProvider>
        </AppKitProvider>
        <Analytics />
      </body>
    </html>
  )
}
