import commandsConfig from '@/config/cli-commands.json'

export interface CommandField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'select' | 'file' | 'checkbox' | 'number'
  required: boolean
  placeholder?: string
  options?: { label: string; value: string }[]
  defaultValue?: string | number | boolean
  helpText?: string
}

export interface CommandStep {
  id: string
  title: string
  description?: string
  fields: CommandField[]
}

export interface CLICommand {
  id: string
  name: string
  description: string
  icon: string
  category: 'contract' | 'deployment' | 'flow' | 'documentation' | 'system' | 'chat'
  requiresInput: boolean
  endpoint?: string | null
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  streaming?: boolean
  redirectTo?: string
  steps?: CommandStep[]
}

export interface CommandCategory {
  id: string
  label: string
  color: string
}

export interface CommandsConfig {
  version: string
  commands: CLICommand[]
  categories: CommandCategory[]
}

// Load commands from JSON
export const CLI_COMMANDS: CLICommand[] = commandsConfig.commands as CLICommand[]
export const COMMAND_CATEGORIES: CommandCategory[] = commandsConfig.categories as CommandCategory[]
export const CONFIG_VERSION: string = commandsConfig.version

// Helper functions
export function getCommandById(id: string): CLICommand | undefined {
  return CLI_COMMANDS.find(cmd => cmd.id === id)
}

export function getCommandsByCategory(category: string): CLICommand[] {
  return CLI_COMMANDS.filter(cmd => cmd.category === category)
}

export function getCategoryById(id: string): CommandCategory | undefined {
  return COMMAND_CATEGORIES.find(cat => cat.id === id)
}

export function getAllCategories(): CommandCategory[] {
  return COMMAND_CATEGORIES
}

export function getAllCommands(): CLICommand[] {
  return CLI_COMMANDS
}
