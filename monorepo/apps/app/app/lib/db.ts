import Dexie, { type Table } from 'dexie'

export interface FileRecord {
  id?: number
  fileId: string
  path: string
  content: string
  language: string
  createdAt: Date
  updatedAt: Date
}

export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

class CodeGenerationDB extends Dexie {
  files!: Table<FileRecord>
  chatMessages!: Table<ChatMessage>

  constructor() {
    super('CodeGenerationDB')

    this.version(1).stores({
      files: '++id, fileId, path, createdAt, updatedAt',
      chatMessages: '++id, role, timestamp'
    })
  }
}

export const db = new CodeGenerationDB()

export async function saveFiles(files: Array<{
  id: string
  path: string
  content: string
  language: string
}>) {
  const timestamp = new Date()
  
  console.log('Saving files to database:', files.map(f => ({ id: f.id, path: f.path, language: f.language })))

  // Use individual put operations instead of bulkPut to avoid conflicts
  for (const file of files) {
    await db.files.put({
      fileId: file.id,
      path: file.path,
      content: file.content,
      language: file.language,
      createdAt: timestamp,
      updatedAt: timestamp
    })
  }
  
  console.log('Files saved successfully')
}

export async function loadFiles() {
  const files = await db.files.toArray()
  console.log('Loading files from database:', files.map(f => ({ fileId: f.fileId, path: f.path, language: f.language })))
  return files.map(file => ({
    id: file.fileId,
    path: file.path,
    content: file.content,
    language: file.language,
    isModified: true
  }))
}

export async function updateFile(fileId: string, content: string) {
  await db.files
    .where('fileId')
    .equals(fileId)
    .modify({
      content,
      updatedAt: new Date()
    })
}

export async function saveChatMessage(role: 'user' | 'assistant', content: string) {
  await db.chatMessages.add({
    role,
    content,
    timestamp: new Date()
  })
}

export async function loadChatMessages() {
  return await db.chatMessages.orderBy('timestamp').toArray()
}

export async function clearAllData() {
  await db.files.clear()
  await db.chatMessages.clear()
  console.log('Database cleared')
}

export async function clearFiles() {
  await db.files.clear()
  console.log('Files cleared from database')
}