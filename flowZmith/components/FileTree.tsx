'use client'

import React, { useState } from 'react'
import { File, Folder, FolderOpen, FileText, Download, Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface FileNode {
  id: string
  path: string
  content: string
  language: string
  isModified?: boolean
}

interface FileTreeProps {
  files: FileNode[]
  selectedFileId: string | null
  onFileSelect: (fileId: string) => void
  onFileDownload: (fileId: string) => void
  onFileCopy: (fileId: string) => void
}

interface TreeItem {
  name: string
  path: string
  type: 'file' | 'folder'
  children?: TreeItem[]
  fileId?: string
  isModified?: boolean
}

function buildTree(files: FileNode[]): TreeItem[] {
  console.log('Building tree for files:', files.map(f => f.path))
  
  const tree: { [key: string]: TreeItem } = {}
  const root: TreeItem[] = []

  files.forEach(file => {
    const parts = file.path.split('/')
    
    // Create all parent directories first
    let currentPath = ''
    for (let i = 0; i < parts.length - 1; i++) {
      currentPath = currentPath ? `${currentPath}/${parts[i]}` : parts[i]
      
      if (!tree[currentPath]) {
        tree[currentPath] = {
          name: parts[i],
          path: currentPath,
          type: 'folder',
          children: [],
          fileId: undefined,
          isModified: undefined
        }
      }
    }

    // Create the file
    const filePath = file.path
    tree[filePath] = {
      name: parts[parts.length - 1],
      path: filePath,
      type: 'file',
      children: undefined,
      fileId: file.id,
      isModified: file.isModified
    }

    // Add to parent or root
    if (parts.length === 1) {
      // Top-level file
      if (!root.find(item => item.path === filePath)) {
        root.push(tree[filePath])
      }
    } else {
      // Add to parent folder
      const parentPath = parts.slice(0, -1).join('/')
      if (tree[parentPath] && tree[parentPath].children) {
        if (!tree[parentPath].children!.find(child => child.path === filePath)) {
          tree[parentPath].children!.push(tree[filePath])
        }
      }
    }
  })

  // Add all top-level folders to root
  Object.values(tree).forEach(item => {
    if (item.type === 'folder' && !item.path.includes('/')) {
      if (!root.find(rootItem => rootItem.path === item.path)) {
        root.push(item)
      }
    }
  })

  console.log('Built tree root:', root.map(item => ({ name: item.name, path: item.path, type: item.type })))
  return root
}

interface FileTreeItemProps {
  item: TreeItem
  level: number
  selectedFileId: string | null
  onFileSelect: (fileId: string) => void
  onFileDownload: (fileId: string) => void
  onFileCopy: (fileId: string) => void
}

function FileTreeItem({ item, level, selectedFileId, onFileSelect, onFileDownload, onFileCopy }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const padding = level * 16
  
  console.log('Rendering FileTreeItem:', { name: item.name, type: item.type, level })

  const handleClick = () => {
    if (item.type === 'folder') {
      setIsExpanded(!isExpanded)
    } else if (item.fileId) {
      onFileSelect(item.fileId)
    }
  }

  const getFileIcon = () => {
    if (item.type === 'folder') {
      return isExpanded ? (
        <FolderOpen className="w-4 h-4 text-blue-400" />
      ) : (
        <Folder className="w-4 h-4 text-blue-400" />
      )
    }

    // Cadence files
    if (item.name.endsWith('.cdc')) {
      return <FileText className="w-4 h-4 text-purple-400" />
    }

    // JavaScript/TypeScript files
    if (item.name.endsWith('.js') || item.name.endsWith('.jsx') || item.name.endsWith('.ts') || item.name.endsWith('.tsx')) {
      return <FileText className="w-4 h-4 text-yellow-400" />
    }

    // CSS files
    if (item.name.endsWith('.css')) {
      return <FileText className="w-4 h-4 text-blue-400" />
    }

    // JSON files
    if (item.name.endsWith('.json')) {
      return <FileText className="w-4 h-4 text-green-400" />
    }

    // Python files
    if (item.name.endsWith('.py')) {
      return <FileText className="w-4 h-4 text-yellow-500" />
    }

    // Solidity files
    if (item.name.endsWith('.sol')) {
      return <FileText className="w-4 h-4 text-gray-400" />
    }

    return <File className="w-4 h-4 text-gray-400" />
  }

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1 px-2 hover:bg-gray-700 rounded cursor-pointer transition-colors ${
          selectedFileId === item.fileId ? 'bg-blue-600/20 border-l-2 border-blue-400' : ''
        }`}
        style={{ paddingLeft: `${padding + 8}px` }}
        onClick={handleClick}
      >
        {getFileIcon()}
        <span className={`text-sm ${item.isModified ? 'text-orange-400 font-medium' : 'text-gray-300'}`}>
          {item.name}
          {item.isModified && ' *'}
        </span>
        {item.type === 'file' && (
          <div className="flex gap-1 ml-auto">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 hover:bg-gray-700 text-gray-400 hover:text-gray-200"
              onClick={(e) => {
                e.stopPropagation()
                onFileCopy(item.fileId!)
              }}
            >
              <Copy className="w-3 h-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 hover:bg-gray-700 text-gray-400 hover:text-gray-200"
              onClick={(e) => {
                e.stopPropagation()
                onFileDownload(item.fileId!)
              }}
            >
              <Download className="w-3 h-3" />
            </Button>
          </div>
        )}
      </div>
      {item.type === 'folder' && isExpanded && item.children && (
        <div>
          {item.children.map((child, index) => (
            <FileTreeItem
              key={child.path}
              item={child}
              level={level + 1}
              selectedFileId={selectedFileId}
              onFileSelect={onFileSelect}
              onFileDownload={onFileDownload}
              onFileCopy={onFileCopy}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function FileTree({ files, selectedFileId, onFileSelect, onFileDownload, onFileCopy }: FileTreeProps) {
  console.log('FileTree received files:', files.map(f => ({ id: f.id, path: f.path, language: f.language })))
  const tree = buildTree(files)
  console.log('Built tree:', tree)

  return (
    <div className="overflow-y-auto h-full bg-gray-900 border-r border-gray-700 custom-scrollbar">
      <div className="p-3 border-b border-gray-700">
        <h3 className="text-sm font-medium text-gray-300">Files</h3>
      </div>
      <div className="p-2">
        {tree.length === 0 && files.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-4">
            No files generated yet
          </div>
        ) : tree.length === 0 && files.length > 0 ? (
          // Fallback: show files as flat list if tree building fails
          <div className="space-y-1 overflow-y-auto custom-scrollbar">
            {files.map((file) => (
              <div
                key={file.id}
                className={`flex items-center gap-2 py-1 px-2 hover:bg-gray-700 rounded cursor-pointer transition-colors ${
                  selectedFileId === file.id ? 'bg-blue-600/20 border-l-2 border-blue-400' : ''
                }`}
                onClick={() => onFileSelect(file.id)}
              >
                <FileText className="w-4 h-4 text-purple-400" />
                <span className={`text-sm ${file.isModified ? 'text-orange-400 font-medium' : 'text-gray-300'}`}>
                  {file.path.split('/').pop()}
                  {file.isModified && ' *'}
                </span>
                <div className="flex gap-1 ml-auto">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 hover:bg-gray-700 text-gray-400 hover:text-gray-200"
                    onClick={(e) => {
                      e.stopPropagation()
                      onFileCopy(file.id)
                    }}
                  >
                    <Copy className="w-3 h-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 hover:bg-gray-700 text-gray-400 hover:text-gray-200"
                    onClick={(e) => {
                      e.stopPropagation()
                      onFileDownload(file.id)
                    }}
                  >
                    <Download className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {console.log('Rendering tree items:', tree.map(item => ({ name: item.name, type: item.type })))}
            {tree.map((item) => (
              <FileTreeItem
                key={item.path}
                item={item}
                level={0}
                selectedFileId={selectedFileId}
                onFileSelect={onFileSelect}
                onFileDownload={onFileDownload}
                onFileCopy={onFileCopy}
              />
            ))}
          </>
        )}
      </div>
    </div>
  )
}