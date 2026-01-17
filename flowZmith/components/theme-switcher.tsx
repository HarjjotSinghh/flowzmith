'use client'

import { useEffect, useState } from 'react'
import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'

export function ThemeSwitcher() {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  const activeTheme = theme === 'system' ? resolvedTheme : theme

  return (
    <div className="inline-flex items-center rounded-full border border-border bg-card/80 p-1 shadow-sm">
      <button
        type="button"
        onClick={() => setTheme('light')}
        aria-label="Switch to light theme"
        className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors ${
          activeTheme === 'light'
            ? 'bg-foreground text-background'
          : 'text-foreground/80 hover:text-foreground'
        }`}
      >
        <Sun className="h-4 w-4" />
      </button>
      <button
        type="button"
        onClick={() => setTheme('dark')}
        aria-label="Switch to dark theme"
        className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors ${
          activeTheme === 'dark'
            ? 'bg-foreground text-background'
          : 'text-foreground/80 hover:text-foreground'
        }`}
      >
        <Moon className="h-4 w-4" />
      </button>
    </div>
  )
}
