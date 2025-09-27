'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Terminal, X, ChevronUp, ChevronDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAppStore, GeneratedFile } from '@/lib/store'

interface TerminalProps {
  isOpen: boolean
  onToggle: () => void
}

export default function TerminalComponent({ isOpen, onToggle }: TerminalProps) {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const terminalRef = useRef<HTMLDivElement>(null)
  
  const { addFile, files, deleteFile, clearFiles } = useAppStore()

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [history])

  const executeCommand = async (command: string) => {
    const trimmedCommand = command.trim()
    if (!trimmedCommand) return

    // Add to history
    setHistory(prev => [...prev, `$ ${trimmedCommand}`])
    setHistoryIndex(-1)

    // Parse command
    const [cmd, ...args] = trimmedCommand.split(' ')

    switch (cmd.toLowerCase()) {
      case 'help':
        setHistory(prev => [...prev, 
          'Available commands:',
          '  help                    - Show this help message',
          '  ls                     - List all files',
          '  rm <filename>          - Delete a file',
          '  clear                  - Clear terminal',
          '  generate <prompt>      - Generate a new file with AI',
          '  install <package>      - Install a package (placeholder)',
          '  uninstall <package>    - Uninstall a package (placeholder)',
          '  exit                   - Close terminal'
        ])
        break

      case 'ls':
        if (files.length === 0) {
          setHistory(prev => [...prev, 'No files found'])
        } else {
          setHistory(prev => [...prev, ...files.map(f => `  ${f.path} (${f.language})`)])
        }
        break

      case 'rm':
        if (args.length === 0) {
          setHistory(prev => [...prev, 'Usage: rm <filename>'])
        } else {
          const filename = args[0]
          const file = files.find(f => f.path.includes(filename))
          if (file) {
            deleteFile(file.id)
            setHistory(prev => [...prev, `Deleted: ${file.path}`])
          } else {
            setHistory(prev => [...prev, `File not found: ${filename}`])
          }
        }
        break

      case 'clear':
        setHistory([])
        break

      case 'generate':
        if (args.length === 0) {
          setHistory(prev => [...prev, 'Usage: generate <prompt>'])
        } else {
          const prompt = args.join(' ')
          setHistory(prev => [...prev, `Generating: ${prompt}...`])
          
          try {
            const response = await fetch('/api/generate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ prompt })
            })

            if (!response.ok) {
              throw new Error('Failed to generate')
            }

            const reader = response.body?.getReader()
            if (!reader) {
              throw new Error('No response body')
            }

            let content = ''
            const decoder = new TextDecoder()
            let done = false

            while (!done) {
              const { value, done: readerDone } = await reader.read()
              done = readerDone
              if (value) {
                content += decoder.decode(value)
              }
            }

            // Extract code blocks
            const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
            const contracts: GeneratedFile[] = []
            let match

            while ((match = codeBlockRegex.exec(content)) !== null) {
              const language = match[1] || 'cadence'
              const code = match[2].trim()
              
              if (code.length > 50) {
                const filename = `contracts/${language}_${Date.now()}.${language === 'cadence' ? 'cdc' : language}`
                const contract: GeneratedFile = {
                  id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                  path: filename,
                  content: code,
                  language: language,
                  isModified: true
                }
                contracts.push(contract)
              }
            }

            if (contracts.length > 0) {
              contracts.forEach(contract => addFile(contract))
              setHistory(prev => [...prev, `Generated ${contracts.length} file(s) successfully`])
            } else {
              setHistory(prev => [...prev, 'No code blocks found in response'])
            }
          } catch (error) {
            setHistory(prev => [...prev, `Error: ${error instanceof Error ? error.message : 'Unknown error'}`])
          }
        }
        break

      case 'install':
        setHistory(prev => [...prev, `Installing ${args.join(' ')}... (Feature coming soon)`])
        break

      case 'uninstall':
        setHistory(prev => [...prev, `Uninstalling ${args.join(' ')}... (Feature coming soon)`])
        break

      case 'exit':
        onToggle()
        break

      default:
        setHistory(prev => [...prev, `Command not found: ${cmd}. Type 'help' for available commands.`])
    }

    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      executeCommand(input)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (historyIndex < history.length - 1) {
        setHistoryIndex(prev => prev + 1)
        setInput(history[history.length - 2 - historyIndex]?.replace('$ ', '') || '')
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex > 0) {
        setHistoryIndex(prev => prev - 1)
        setInput(history[history.length - 1 - historyIndex]?.replace('$ ', '') || '')
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setInput('')
      }
    }
  }

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={onToggle}
          className="bg-gray-800 hover:bg-gray-700 text-white rounded-full p-3 shadow-lg"
        >
          <Terminal className="w-5 h-5" />
        </Button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 z-50 h-80 flex flex-col">
      <div className="flex items-center justify-between p-3 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-green-400" />
          <span className="text-sm font-medium text-gray-300">Terminal</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setHistory([])}
            className="h-6 w-6 p-0 text-gray-400 hover:text-gray-200"
          >
            <ChevronUp className="w-3 h-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="h-6 w-6 p-0 text-gray-400 hover:text-gray-200"
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
      </div>
      
      <div
        ref={terminalRef}
        className="flex-1 p-3 overflow-y-auto font-mono text-sm text-gray-300 custom-scrollbar"
      >
        {history.map((line, index) => (
          <div key={index} className="mb-1">
            {line}
          </div>
        ))}
      </div>
      
      <div className="p-3 border-t border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-green-400">$</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 focus:outline-none"
            placeholder="Enter command..."
            autoComplete="off"
          />
        </div>
      </div>
    </div>
  )
}
