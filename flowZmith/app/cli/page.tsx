"use client"

import * as React from "react"
import { CLISidebar } from "@/components/cli/cli-sidebar"
import { CommandDialog } from "@/components/cli/command-dialog"
import {
  TerminalOutput,
  useTerminalLogs,
} from "@/components/cli/terminal-output";
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { FileCode, Terminal, Loader2, Activity } from "lucide-react";
import type { CLICommand } from "@/lib/cli-commands"
import dynamic from "next/dynamic"

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false })

interface FileNode {
  name: string
  path: string
  type: "file" | "directory"
  content?: string
  children?: FileNode[]
}

export default function CLIWorkspacePage() {
  const [selectedCommand, setSelectedCommand] =
    React.useState<CLICommand | null>(null);
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [files, setFiles] = React.useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = React.useState<FileNode | null>(null);
  const [executionHistory, setExecutionHistory] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  // Terminal logs
  const {
    logs,
    isStreaming,
    addLog,
    clearLogs,
    startStreaming,
    stopStreaming,
  } = useTerminalLogs();

  const handleCommandSelect = (command: CLICommand) => {
    setSelectedCommand(command);

    // For chat command, redirect to chat page
    if (command.redirectTo) {
      window.location.href = command.redirectTo;
      return;
    }

    setDialogOpen(true);
  };

  const handleExecuteCommand = async (command: CLICommand, data: any) => {
    setIsLoading(true);
    startStreaming();

    // Log command execution start
    addLog(`Executing command: ${command.name}`, "command");
    addLog(`Parameters: ${JSON.stringify(data, null, 2)}`, "info");

    try {
      let result: any;

      // Make API call based on command endpoint
      if (command.endpoint) {
        addLog(
          `Calling API endpoint: ${command.method} ${command.endpoint}`,
          "info"
        );

        // Transform form data for create_contract command to match backend expectations
        let requestData = data;
        if (command.id === "create_contract") {
          requestData = {
            contract_name: data.contract_name || "Contract",
            contract_type: data.contract_type || "custom",
            description: data.description || "",
            network: data.network || "testnet",
            account_setup: data.account_setup || "single",
            features: [],
          };

          // Add features based on checkboxes
          if (data.include_transactions)
            requestData.features.push("transactions");
          if (data.include_deployment)
            requestData.features.push("deployment_scripts");
          if (data.include_tests) requestData.features.push("test_cases");

          // If no features selected, add default ones
          if (requestData.features.length === 0) {
            requestData.features = [
              "transactions",
              "deployment_scripts",
              "test_cases",
            ];
          }

          addLog(
            `Transformed request data: ${JSON.stringify(requestData, null, 2)}`,
            "info"
          );
        }

        // Check if streaming is supported
        if (command.streaming) {
          // Handle streaming response
          const response = await fetch(command.endpoint, {
            method: command.method || "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body:
              command.method !== "GET"
                ? JSON.stringify(requestData)
                : undefined,
          });

          if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          if (reader) {
            addLog("Receiving streaming response...", "info");
            let buffer = "";

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              buffer += decoder.decode(value, { stream: true });
              const lines = buffer.split("\n");
              buffer = lines.pop() || "";

              for (const line of lines) {
                if (line.startsWith("data: ")) {
                  const dataContent = line.slice(6).trim();

                  // Handle end of stream
                  if (dataContent === "[DONE]") {
                    addLog("Stream completed", "success");
                    break;
                  }

                  try {
                    const chunk = JSON.parse(dataContent);

                    // Handle OpenAI-compatible streaming format
                    if (chunk.choices && chunk.choices[0]) {
                      const choice = chunk.choices[0];

                      if (choice.delta && choice.delta.content) {
                        // Accumulate content for streaming text
                        if (!result.content) result.content = "";
                        result.content += choice.delta.content;
                        addLog(choice.delta.content, "info");
                      }

                      if (choice.finish_reason === "stop") {
                        addLog("Generation completed", "success");
                      }
                    }
                    // Handle legacy format for backward compatibility
                    else if (chunk.type === "content") {
                      addLog(chunk.chunk || chunk.message, "info");
                    } else if (chunk.type === "error") {
                      addLog(chunk.error || chunk.message, "error");
                    } else if (chunk.type === "status") {
                      addLog(chunk.data?.stage || chunk.message, "success");
                    } else if (chunk.type === "progress") {
                      addLog(chunk.data?.message || chunk.message, "info");
                    } else if (chunk.type === "complete") {
                      result = chunk.data || {};
                      addLog("Command completed successfully", "success");
                    }
                  } catch (e) {
                    // Skip invalid JSON or handle plain text
                    if (dataContent && dataContent !== "") {
                      addLog(dataContent, "info");
                    }
                  }
                }
              }
            }
          }
        } else {
          // Handle regular response
          const response = await fetch(command.endpoint, {
            method: command.method || "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body:
              command.method !== "GET"
                ? JSON.stringify(requestData)
                : undefined,
          });

          if (!response.ok) {
            const errorText = await response.text();
            addLog(`API error: ${response.statusText}`, "error");
            addLog(errorText, "error");
            throw new Error(`API call failed: ${response.statusText}`);
          }

          result = await response.json();
          addLog("Response received", "success");
          addLog(JSON.stringify(result, null, 2), "info");
        }
      } else {
        // For commands without endpoints, return a placeholder
        addLog("Command executed locally (no API endpoint)", "warning");
        result = { status: "success", message: "Command executed locally" };
      }

      // Add to execution history
      setExecutionHistory((prev) => [
        {
          command: command.name,
          timestamp: new Date().toISOString(),
          result,
          data,
        },
        ...prev,
      ]);

      // If result contains generated files, add them to the file tree
      if (result.generated_contract_code) {
        addLog("Generated contract code received", "success");
        addLog(`Contract name: ${result.contract_name || "Contract"}`, "info");

        const contractFile: FileNode = {
          name: `${result.contract_name || "Contract"}.cdc`,
          path: `/${result.contract_name || "Contract"}.cdc`,
          type: "file",
          content: result.generated_contract_code,
        };

        const configFile: FileNode = {
          name: "flow.json",
          path: "/flow.json",
          type: "file",
          content: JSON.stringify(result.config_content, null, 2),
        };

        setFiles([contractFile, configFile]);
        setSelectedFile(contractFile);
        addLog("Files added to workspace", "success");
      }

      addLog(`Command "${command.name}" completed successfully`, "success");
      return result;
    } catch (error: any) {
      console.error("Command execution error:", error);
      addLog(`Error: ${error.message}`, "error");
      throw error;
    } finally {
      setIsLoading(false);
      stopStreaming();
    }
  };

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
    ));
  };

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
              <div className="border-b pr-4">
                <TabsList>
                  <TabsTrigger value="editor">
                    <FileCode className="h-4 w-4 mr-2" />
                    Editor
                  </TabsTrigger>
                  <TabsTrigger value="terminal">
                    <Terminal className="h-4 w-4 mr-2" />
                    Terminal
                    {isStreaming && (
                      <span className="ml-2 flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                      </span>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="history">
                    <Activity className="h-4 w-4 mr-2" />
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
                        setSelectedFile({ ...selectedFile, content: value });
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

              <TabsContent value="terminal" className="flex-1 m-0 p-4">
                <TerminalOutput
                  logs={logs}
                  isStreaming={isStreaming}
                  onClear={clearLogs}
                  className="h-full"
                />
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
                              <strong>Project:</strong>{" "}
                              {entry.result.project_dir}
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
  );
}
