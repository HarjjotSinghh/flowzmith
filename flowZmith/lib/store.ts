import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface GeneratedFile {
  id: string
  path: string
  content: string
  language: string
  isModified?: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface AppState {
  // Files state
  files: GeneratedFile[]
  selectedFileId: string | null
  
  // Chat state
  messages: ChatMessage[]
  
  // Terminal state
  terminalHistory: string[]
  terminalInput: string
  isTerminalOpen: boolean
  
  // Hydration state
  _hasHydrated: boolean
  
  // Actions
  addFile: (file: GeneratedFile) => void
  updateFile: (id: string, content: string) => void
  deleteFile: (id: string) => void
  selectFile: (id: string) => void
  clearFiles: () => void
  
  addMessage: (message: ChatMessage) => void
  updateMessage: (id: string, content: string) => void
  clearMessages: () => void
  
  addTerminalHistory: (command: string) => void
  setTerminalInput: (input: string) => void
  toggleTerminal: () => void
  clearTerminal: () => void
  
  setHasHydrated: (state: boolean) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      files: [],
      selectedFileId: null,
      messages: [],
      terminalHistory: [],
      terminalInput: '',
      isTerminalOpen: false,
      _hasHydrated: false,
      
      // File actions
      addFile: (file) => {
        console.log('Adding file to store:', file)
        set((state) => ({
          files: [...state.files, file],
          selectedFileId: file.id
        }))
      },
      
      updateFile: (id, content) => {
        set((state) => ({
          files: state.files.map(file =>
            file.id === id ? { ...file, content, isModified: true } : file
          )
        }))
      },
      
      deleteFile: (id) => {
        set((state) => ({
          files: state.files.filter(file => file.id !== id),
          selectedFileId: state.selectedFileId === id ? null : state.selectedFileId
        }))
      },
      
      selectFile: (id) => {
        set({ selectedFileId: id })
      },
      
      clearFiles: () => {
        set({ files: [], selectedFileId: null })
      },
      
      // Chat actions
      addMessage: (message) => {
        set((state) => ({
          messages: [...state.messages, message]
        }))
      },
      
      updateMessage: (id: string, content: string) => {
        set((state) => ({
          messages: state.messages.map(msg =>
            msg.id === id ? { ...msg, content } : msg
          )
        }))
      },
      
      clearMessages: () => {
        set({ messages: [] })
      },
      
      // Terminal actions
      addTerminalHistory: (command) => {
        set((state) => ({
          terminalHistory: [...state.terminalHistory, command]
        }))
      },
      
      setTerminalInput: (input) => {
        set({ terminalInput: input })
      },
      
      toggleTerminal: () => {
        set((state) => ({ isTerminalOpen: !state.isTerminalOpen }))
      },
      
      clearTerminal: () => {
        set({ terminalHistory: [], terminalInput: '' })
      },
      
      setHasHydrated: (state) => {
        set({ _hasHydrated: state })
      }
    }),
    {
      name: 'app-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        files: state.files,
        messages: state.messages,
        selectedFileId: state.selectedFileId
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setHasHydrated(true)
        }
      }
    }
  )
)
