"use client"

import * as React from "react"
import { CLISidebar } from "@/components/cli-sidebar"
import { CommandDialog } from "@/components/command-dialog"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { FileCode, Terminal, Loader2 } from "lucide-react"
import type { CLICommand } from "@flowzmith/schema"
import { apiClient } from "@/lib/api-client"
import Editor from "@monaco-editor/react"

interface FileNode {
  name: string
  path: string
  type: "file" | "directory"
  content?: string
  children?: FileNode[]
}

export default function CLIWorkspacePage() {
  const [selectedCommand, setSelectedCommand] = React.useState<CLICommand | null>(null)
  const [dialogOpen, setDialogOpen] = React.useState(false)
  const [files, setFiles] = React.useState<FileNode[]>([])
  const [selectedFile, setSelectedFile] = React.useState<FileNode | null>(null)
  const [executionHistory, setExecutionHistory] = React.useState<any[]>([])
  const [isLoading, setIsLoading] = React.useState(false)

  const handleCommandSelect = (command: CLICommand) => {
    setSelectedCommand(command)
    
    // For chat command, redirect to chat page
    if (command.id === "chat") {
      window.location.href = "/chat"
      return
    }
    
    setDialogOpen(true)
  }

  const handleExecuteCommand = async (command: CLICommand, data: any) => {
    setIsLoading(true)
    
    try {
      let result: any

      switch (command.id) {
        case "create_contract":
          result = await apiClient.createContract(data)
          break

        case "generate_from_context":
          result = await apiClient.generateContractWithContext(data)
          break

        case "deploy_contract":
          result = await apiClient.deployContract(data)
          break

        case "search_docs":
          result = await apiClient.searchDocs(data)
          break

        case "flow_init":
          result = await apiClient.flowInit(data)
          break

        case "flow_list":
          result = await apiClient.flowListProjects()
          break

        case "list_deployments":
          result = await apiClient.listDeployments()
          break

        case "status":
          result = await apiClient.getSystemStatus()
          break

        case "flow_auto":
          // This is a complex workflow - use generate with context
          result = await apiClient.generateContractWithContext({
            ...data,
            auto_deploy: true,
          })
          break

        default:
          throw new Error(`Command ${command.id} not implemented`)
      }

      // Add to execution history
      setExecutionHistory(prev => [
        {
          command: command.name,
          timestamp: new Date().toISOString(),
          result,
          data,
        },
        ...prev,
      ])

      // If result contains generated files, add them to the file tree
      if (result.generated_contract_code) {
        const contractFile: FileNode = {
          name: `${result.contract_name || "Contract"}.cdc`,
          path: `/${result.contract_name || "Contract"}.cdc`,
          type: "file",
          content: result.generated_contract_code,
        }

        const configFile: FileNode = {
          name: "flow.json",
          path: "/flow.json",
          type: "file",
          content: JSON.stringify(result.config_content, null, 2),
        }

        setFiles([contractFile, configFile])
        setSelectedFile(contractFile)
      }

      return result
    } catch (error: any) {
      console.error("Command execution error:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const renderFileTree = (nodes: FileNode[], level: number = 0) => {
    return nodes.map((node) => (
      <div key={node.path} style={{ paddingLeft: `${level * 16}px` }}>
        <Button
          variant={selectedFile?.path === node.path ? "secondary" : "ghost"}
          className="w-full justify-start text-sm h-8"
          onClick={() => setSelectedFile(node)}
        >
          <FileCode className="h-4 w-4 mr-2" />
          {node.name}
        </Button>
        {node.children && renderFileTree(node.children, level + 1)}
      </div>
    ))
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 flex-shrink-0">
        <CLISidebar
          onCommandSelect={handleCommandSelect}
          selectedCommand={selectedCommand}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b p-4">
          <h1 className="text-2xl font-bold">CLI Workspace</h1>
          <p className="text-sm text-muted-foreground">
            Execute CLI commands and view results in real-time
          </p>
        </div>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* File Explorer */}
          {files.length > 0 && (
            <div className="w-64 border-r flex flex-col">
              <div className="p-4 border-b">
                <h3 className="font-semibold text-sm">Generated Files</h3>
              </div>
              <ScrollArea className="flex-1">
                <div className="p-2">{renderFileTree(files)}</div>
              </ScrollArea>
            </div>
          )}

          {/* Editor/Output Area */}
          <div className="flex-1 flex flex-col">
            <Tabs defaultValue="editor" className="flex-1 flex flex-col">
              <div className="border-b px-4">
                <TabsList>
                  <TabsTrigger value="editor">
                    <FileCode className="h-4 w-4 mr-2" />
                    Editor
                  </TabsTrigger>
                  <TabsTrigger value="history">
                    <Terminal className="h-4 w-4 mr-2" />
                    History
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="editor" className="flex-1 m-0">
                {selectedFile ? (
                  <Editor
                    height="100%"
                    defaultLanguage={
                      selectedFile.name.endsWith(".cdc")
                        ? "javascript"
                        : selectedFile.name.endsWith(".json")
                        ? "json"
                        : "plaintext"
                    }
                    value={selectedFile.content || ""}
                    theme="vs-dark"
                    options={{
                      readOnly: false,
                      minimap: { enabled: false },
                      fontSize: 14,
                    }}
                    onChange={(value) => {
                      if (selectedFile && value !== undefined) {
                        setSelectedFile({ ...selectedFile, content: value })
                      }
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    <div className="text-center">
                      <FileCode className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No file selected</p>
                      <p className="text-sm mt-2">
                        Execute a command to generate files
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="history" className="flex-1 m-0 p-4">
                <ScrollArea className="h-full">
                  {executionHistory.length === 0 ? (
                    <div className="text-center text-muted-foreground py-8">
                      <Terminal className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No execution history</p>
                      <p className="text-sm mt-2">
                        Commands you execute will appear here
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {executionHistory.map((entry, idx) => (
                        <div
                          key={idx}
                          className="border rounded-lg p-4 space-y-2"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{entry.command}</span>
                            <Badge
                              variant={
                                entry.result.status === "success" ||
                                entry.result.status === "deployed"
                                  ? "default"
                                  : "destructive"
                              }
                            >
                              {entry.result.status}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {new Date(entry.timestamp).toLocaleString()}
                          </p>
                          {entry.result.error && (
                            <p className="text-sm text-red-600">
                              {entry.result.error}
                            </p>
                          )}
                          {entry.result.project_dir && (
                            <p className="text-sm">
                              <strong>Project:</strong> {entry.result.project_dir}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>

      {/* Command Dialog */}
      <CommandDialog
        command={selectedCommand}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onExecute={handleExecuteCommand}
      />

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background p-6 rounded-lg shadow-lg">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-sm">Executing command...</p>
          </div>
        </div>
      )}
    </div>
  )
}
