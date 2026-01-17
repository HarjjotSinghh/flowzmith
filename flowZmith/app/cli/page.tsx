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
import { ThemeSwitcher } from "@/components/theme-switcher"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  FileCode,
  Terminal,
  Loader2,
  Activity,
  Download,
  Github,
  Play,
  Rocket,
  ChevronDown,
  Folder,
  File,
  ChevronRight
} from "lucide-react";
import type { CLICommand } from "@/lib/cli-commands"
import dynamic from "next/dynamic"
import JSZip from "jszip"
import { configureMonacoLanguages, getLanguageFromFileName, getEditorOptions } from "@/lib/monaco-config"
import { useTheme } from "next-themes"

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false })

interface FileNode {
  name: string
  path: string
  type: "file" | "directory"
  content?: string
  children?: FileNode[]
}

interface ProjectData {
  projectPath: string
  projectId: string
  files: FileNode[]
}

export default function CLIWorkspacePage() {
  const { resolvedTheme } = useTheme()
  const [selectedCommand, setSelectedCommand] =
    React.useState<CLICommand | null>(null);
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [files, setFiles] = React.useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = React.useState<FileNode | null>(null);
  const [executionHistory, setExecutionHistory] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [projectData, setProjectData] = React.useState<ProjectData | null>(null);
  const [expandedFolders, setExpandedFolders] = React.useState<Set<string>>(new Set());
  const [isCompiling, setIsCompiling] = React.useState(false);
  const [isDeploying, setIsDeploying] = React.useState(false);
  const [isExporting, setIsExporting] = React.useState(false);
  const editorTheme = resolvedTheme === "dark" ? "vs-dark" : "vs";

  // Terminal logs
  const {
    logs,
    isStreaming,
    addLog,
    clearLogs,
    startStreaming,
    stopStreaming,
  } = useTerminalLogs();

  // Fetch project files from backend
  const fetchProjectFiles = async (projectPath: string) => {
    try {
      addLog(`Fetching project files from ${projectPath}...`, "info");

      const response = await fetch(`/api/projects/files?path=${encodeURIComponent(projectPath)}`);
      if (!response.ok) {
        throw new Error("Failed to fetch project files");
      }

      const data = await response.json();
      return data.files || [];
    } catch (error: any) {
      addLog(`Error fetching files: ${error.message}`, "error");
      return [];
    }
  };

  // Build file tree from flat file list
  const buildFileTree = (fileList: any[]): FileNode[] => {
    const root: FileNode[] = [];
    const map = new Map<string, FileNode>();

    fileList.forEach((file) => {
      const node: FileNode = {
        name: file.name,
        path: file.path,
        type: file.type,
        content: file.content,
        children: file.type === "directory" ? [] : undefined,
      };
      map.set(file.path, node);
    });

    fileList.forEach((file) => {
      const node = map.get(file.path);
      if (!node) return;

      const parentPath = file.path.substring(0, file.path.lastIndexOf("/"));
      const parent = map.get(parentPath);

      if (parent && parent.children) {
        parent.children.push(node);
      } else {
        root.push(node);
      }
    });

    return root;
  };

  // Export project as ZIP
  const handleExportZip = async () => {
    if (!projectData || files.length === 0) {
      addLog("No project to export", "warning");
      return;
    }

    setIsExporting(true);
    addLog("Creating ZIP archive...", "info");

    try {
      const zip = new JSZip();

      const addFilesToZip = (nodes: FileNode[], folder: JSZip) => {
        nodes.forEach((node) => {
          if (node.type === "file" && node.content) {
            folder.file(node.name, node.content);
          } else if (node.type === "directory" && node.children) {
            const subFolder = folder.folder(node.name);
            if (subFolder) {
              addFilesToZip(node.children, subFolder);
            }
          }
        });
      };

      addFilesToZip(files, zip);

      const blob = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${projectData.projectId || "project"}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      addLog("Project exported successfully as ZIP", "success");
    } catch (error: any) {
      addLog(`Export failed: ${error.message}`, "error");
    } finally {
      setIsExporting(false);
    }
  };

  // Export project as TAR
  const handleExportTar = async () => {
    if (!projectData || files.length === 0) {
      addLog("No project to export", "warning");
      return;
    }

    setIsExporting(true);
    addLog("Creating TAR archive...", "info");

    try {
      // For TAR, we'll use a simple text-based format
      // In production, you'd want to use a proper TAR library
      const tarContent: string[] = [];

      const addFilesToTar = (nodes: FileNode[], prefix = "") => {
        nodes.forEach((node) => {
          const fullPath = prefix + node.name;
          if (node.type === "file" && node.content) {
            tarContent.push(`=== ${fullPath} ===`);
            tarContent.push(node.content);
            tarContent.push("");
          } else if (node.type === "directory" && node.children) {
            addFilesToTar(node.children, fullPath + "/");
          }
        });
      };

      addFilesToTar(files);

      const blob = new Blob([tarContent.join("\n")], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${projectData.projectId || "project"}.tar`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      addLog("Project exported successfully as TAR", "success");
    } catch (error: any) {
      addLog(`Export failed: ${error.message}`, "error");
    } finally {
      setIsExporting(false);
    }
  };

  // Compile contract
  const handleCompile = async () => {
    if (!selectedFile || !selectedFile.content) {
      addLog("No contract selected for compilation", "warning");
      return;
    }

    setIsCompiling(true);
    addLog(`Compiling ${selectedFile.name}...`, "info");

    try {
      const response = await fetch("/api/contracts/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contract_code: selectedFile.content,
          contract_name: selectedFile.name.replace(".cdc", ""),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Compilation failed");
      }

      const result = await response.json();
      addLog("Compilation successful!", "success");

      if (result.warnings && result.warnings.length > 0) {
        result.warnings.forEach((warning: string) => {
          addLog(`Warning: ${warning}`, "warning");
        });
      }
    } catch (error: any) {
      addLog(`Compilation error: ${error.message}`, "error");
    } finally {
      setIsCompiling(false);
    }
  };

  // Deploy contract on-chain
  const handleDeploy = async () => {
    if (!selectedFile || !selectedFile.content) {
      addLog("No contract selected for deployment", "warning");
      return;
    }

    if (!projectData) {
      addLog("No project data available", "warning");
      return;
    }

    setIsDeploying(true);
    addLog(`Deploying ${selectedFile.name} on-chain...`, "info");

    try {
      const response = await fetch("/api/contracts/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_path: '../' + projectData.projectPath,
          contract_name: selectedFile.name.replace(".cdc", ""),
          network: "testnet",
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Deployment failed");
      }

      const result = await response.json();
      addLog("Deployment successful!", "success");

      if (result.transaction_id) {
        addLog(`Transaction ID: ${result.transaction_id}`, "info");
      }

      if (result.contract_address) {
        addLog(`Contract Address: ${result.contract_address}`, "info");
      }
    } catch (error: any) {
      addLog(`Deployment error: ${error.message}`, "error");
    } finally {
      setIsDeploying(false);
    }
  };

  // GitHub integration
  const handleGitHubExport = async () => {
    if (!projectData || files.length === 0) {
      addLog("No project to export to GitHub", "warning");
      return;
    }

    // Check if already authenticated
    const urlParams = new URLSearchParams(window.location.search);
    const isConnected = urlParams.get("github_connected") === "true";

    if (!isConnected) {
      addLog("Redirecting to GitHub OAuth...", "info");

      // Store project data in sessionStorage for after OAuth redirect
      sessionStorage.setItem("pendingGitHubExport", JSON.stringify({
        projectId: projectData.projectId,
        projectPath: projectData.projectPath,
      }));

      // Redirect to GitHub OAuth
      window.location.href = "/api/auth/github?redirect=/cli";
      return;
    }

    // Create repository
    addLog("Creating GitHub repository...", "info");

    try {
      const repoName = `flow-${projectData.projectId.substring(0, 8)}`;

      // Flatten files for upload
      const flatFiles: any[] = [];
      const flattenFiles = (nodes: FileNode[], prefix = "") => {
        nodes.forEach((node) => {
          if (node.type === "file" && node.content) {
            flatFiles.push({
              path: prefix + node.name,
              content: node.content,
            });
          } else if (node.type === "directory" && node.children) {
            flattenFiles(node.children, prefix + node.name + "/");
          }
        });
      };
      flattenFiles(files);

      const response = await fetch("/api/github/create-repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_name: repoName,
          description: "Flow smart contract project generated by Flowzmith",
          files: flatFiles,
          is_private: false,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to create repository");
      }

      const result = await response.json();
      addLog(`Repository created: ${result.repo_url}`, "success");

      // Open repository in new tab
      window.open(result.repo_url, "_blank");
    } catch (error: any) {
      addLog(`GitHub export failed: ${error.message}`, "error");
    }
  };

  // Check for GitHub OAuth callback on mount
  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const isConnected = urlParams.get("github_connected") === "true";

    if (isConnected) {
      const pendingExport = sessionStorage.getItem("pendingGitHubExport");
      if (pendingExport) {
        sessionStorage.removeItem("pendingGitHubExport");
        addLog("GitHub connected successfully", "success");

        // Trigger export
        setTimeout(() => {
          handleGitHubExport();
        }, 500);
      }

      // Clean URL
      window.history.replaceState({}, "", "/cli");
    }
  }, []);

  // Configure Monaco Editor languages on mount
  React.useEffect(() => {
    configureMonacoLanguages();
  }, []);

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

      // If result contains project path, fetch all files
      if (result.project_path) {
        addLog("Loading project files...", "info");
        addLog(`Project path: ${result.project_path}`, "info");

        const projectFiles = await fetchProjectFiles(result.project_path);

        if (projectFiles.length > 0) {
          const fileTree = buildFileTree(projectFiles);
          setFiles(fileTree);

          // Set project data
          setProjectData({
            projectPath: result.project_path,
            projectId: result.submission_id || result.project_id || "unknown",
            files: fileTree,
          });

          // Select the main contract file
          const mainContract = projectFiles.find((f: any) =>
            f.type === "file" && f.name.endsWith(".cdc") && f.path.includes("/contracts/")
          );

          if (mainContract) {
            setSelectedFile({
              name: mainContract.name,
              path: mainContract.path,
              type: "file",
              content: mainContract.content,
            });
          }

          addLog(`Loaded ${projectFiles.length} files`, "success");
        } else {
          addLog("No files found in project directory", "warning");
        }
      }
      // Fallback for old format
      else if (result.generated_contract_code) {
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

  const toggleFolder = (path: string) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderFileTree = (nodes: FileNode[], level: number = 0) => {
    return nodes.map((node) => {
      const isExpanded = expandedFolders.has(node.path);
      const isSelected = selectedFile?.path === node.path;

      if (node.type === "directory") {
        return (
          <div key={node.path}>
            <Button
              variant="ghost"
              className="w-full justify-start text-sm h-8"
              style={{ paddingLeft: `${level * 12 + 8}px` }}
              onClick={() => toggleFolder(node.path)}
            >
              <ChevronRight
                className={`h-4 w-4 mr-1 transition-transform ${isExpanded ? "rotate-90" : ""
                  }`}
              />
              <Folder className="h-4 w-4 mr-2" />
              {node.name}
            </Button>
            {isExpanded && node.children && (
              <div>{renderFileTree(node.children, level + 1)}</div>
            )}
          </div>
        );
      }

      return (
        <Button
          key={node.path}
          variant={isSelected ? "secondary" : "ghost"}
          className="w-full justify-start text-sm h-8"
          style={{ paddingLeft: `${level * 12 + 24}px` }}
          onClick={() => setSelectedFile(node)}
        >
          <File className="h-4 w-4 mr-2" />
          {node.name}
        </Button>
      );
    });
  };

  return (
    <div className="flex h-screen bg-background">
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
        <div className="border-b border-border bg-card/80 p-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-display font-semibold text-foreground">CLI Workspace</h1>
              <p className="text-sm text-foreground/80">
                Execute CLI commands and view results in real-time
              </p>
            </div>
            <ThemeSwitcher />
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* File Explorer */}
          {files.length > 0 && (
            <div className="w-64 border-r border-border bg-card/80 flex flex-col">
              <div className="p-4 border-b border-border">
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
                        <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-primary opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                      </span>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="history">
                    <Activity className="h-4 w-4 mr-2" />
                    History
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="editor" className="flex-1 m-0 flex flex-col">
                {/* Action Toolbar */}
                {files.length > 0 && (
                  <div className="border-b p-2 flex items-center gap-2 bg-muted/30">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={isExporting}
                        >
                          {isExporting ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4 mr-2" />
                          )}
                          Export
                          <ChevronDown className="h-4 w-4 ml-2" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem onClick={handleExportZip}>
                          <Download className="h-4 w-4 mr-2" />
                          Export as .zip
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={handleExportTar}>
                          <Download className="h-4 w-4 mr-2" />
                          Export as .tar
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleGitHubExport}
                    >
                      <Github className="h-4 w-4 mr-2" />
                      Push to GitHub
                    </Button>

                    <div className="flex-1" />

                    {selectedFile?.name.endsWith(".cdc") && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleCompile}
                          disabled={isCompiling}
                        >
                          {isCompiling ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Play className="h-4 w-4 mr-2" />
                          )}
                          Compile
                        </Button>

                        <Button
                          size="sm"
                          onClick={handleDeploy}
                          disabled={isDeploying}
                        >
                          {isDeploying ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Rocket className="h-4 w-4 mr-2" />
                          )}
                          Deploy On-Chain
                        </Button>
                      </>
                    )}
                  </div>
                )}

                {/* Editor */}
                <div className="flex-1">
                  {selectedFile ? (
                    <Editor
                      height="100%"
                      language={getLanguageFromFileName(selectedFile.name)}
                      value={selectedFile.content || ""}
                      theme={editorTheme}
                      options={getEditorOptions(getLanguageFromFileName(selectedFile.name))}
                      onChange={(value) => {
                        if (selectedFile && value !== undefined) {
                          setSelectedFile({ ...selectedFile, content: value });
                        }
                      }}
                    />
                  ) : (
                      <div className="flex items-center justify-center h-full text-foreground/80">
                      <div className="text-center">
                        <FileCode className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No file selected</p>
                        <p className="text-sm mt-2">
                          Execute a command to generate files
                        </p>
                      </div>
                    </div>
                  )}
                </div>
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
                    <div className="text-center text-foreground/80 py-8">
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
                          <p className="text-xs text-foreground/80">
                            {new Date(entry.timestamp).toLocaleString()}
                          </p>
                          {entry.result.error && (
                            <p className="text-sm text-destructive">
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
          <div className="bg-background p-6 rounded-lg shadow-lg max-w-md">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-sm text-center font-medium mb-2">Processing...</p>
            <p className="text-xs text-center text-foreground/80">
              Generating contract files and setting up project structure
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
