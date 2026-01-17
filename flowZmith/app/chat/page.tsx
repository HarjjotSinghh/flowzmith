"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels"
import Image from "next/image"
import { ThemeSwitcher } from "@/components/theme-switcher"
import { useTheme } from "next-themes"
import {
  Bot,
  Send,
  User,
  Download,
  Copy,
  FolderOpen,
  FileText,
  Trash2,
  Save,
  Terminal
} from "lucide-react"
import Editor from '@monaco-editor/react'
import FileTree from "@/components/FileTree"
import TerminalComponent from "@/components/terminal"
import { useAppStore } from "@/lib/store"
import { db, saveFiles, loadFiles, saveChatMessage, loadChatMessages, updateFile, clearFiles } from "@/lib/db"
import { akaveService } from "@/lib/akave"
import { useStreamingChat } from "@/hooks/use-streaming-chat";
import JSZip from "jszip";

interface GeneratedFile {
  id: string;
  path: string;
  content: string;
  language: string;
  isModified?: boolean;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { resolvedTheme } = useTheme()
  const [isInitialized, setIsInitialized] = useState(false);
  const [isTerminalOpen, setIsTerminalOpen] = useState(false);
  const [isAkaveEnabled, setIsAkaveEnabled] = useState(false);
  const [akaveStatus, setAkaveStatus] = useState<
    "checking" | "available" | "unavailable"
  >("checking");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use Zustand store
  const {
    files,
    selectedFileId,
    messages,
    addFile,
    updateFile,
    selectFile,
    clearFiles,
    addMessage,
    updateMessage,
    clearMessages,
    toggleTerminal,
    _hasHydrated,
  } = useAppStore();

  // Use streaming chat hook
  const {
    messages: streamingMessages,
    input,
    handleInputChange,
    handleSubmit: streamingHandleSubmit,
    isLoading,
    isGenerating,
    error,
    setMessages: setStreamingMessages,
    sendMessage,
    generateContract,
    generateWithContext,
  } = useStreamingChat({
    api: "/api/chat/completions",
    initialMessages: messages.map((msg) => ({
      id: msg.id,
      role: msg.role,
      content: msg.content,
    })),
    onFinish: async (message) => {
      // Extract and save generated contracts from the assistant's response
      await extractAndSaveContracts(message.content, input);

      // Save the message to database
      await saveChatMessage("assistant", message.content);
    },
    onError: (error) => {
      console.error("Streaming error:", error);
    },
  });

  // Debug store state
  useEffect(() => {
    console.log(
      "Store files updated:",
      files.length,
      files.map((f) => f.path)
    );
    console.log(
      "Store messages updated:",
      messages.length,
      messages.map((m) => ({
        id: m.id,
        role: m.role,
        contentLength: m.content.length,
      }))
    );
    console.log("Store state:", {
      files: files.length,
      selectedFileId,
      messages: messages.length,
    });
  }, [files, selectedFileId, messages]);

  const selectedFile = files.find((f) => f.id === selectedFileId);

  useEffect(() => {
    const initializeData = async () => {
      // Wait for store hydration
      if (!_hasHydrated) {
        console.log("Waiting for store hydration...");
        return;
      }

      // Check Akave availability
      try {
        setAkaveStatus("checking");
        const isAvailable = await akaveService.checkHealth();
        setIsAkaveEnabled(isAvailable);
        setAkaveStatus(isAvailable ? "available" : "unavailable");
        console.log(
          "Akave service status:",
          isAvailable ? "available" : "unavailable"
        );
      } catch (error) {
        // Silently handle Akave unavailability - it's optional for the app to function
        console.log(
          "Akave service not available (storage will be local only):"
        );
        setIsAkaveEnabled(false);
        setAkaveStatus("unavailable");
      }

      try {
        const savedFiles = await loadFiles();
        const savedMessages = await loadChatMessages();

        console.log(
          "Loaded files on init:",
          savedFiles.map((f) => f.path)
        );
        console.log("Loaded messages on init:", savedMessages.length);

        // Only load from database if store is empty
        if (files.length === 0 && savedFiles.length > 0) {
          savedFiles.forEach((file) => addFile(file));
        }

        if (messages.length === 0 && savedMessages.length > 0) {
          const formattedMessages = savedMessages.map((msg) => ({
            ...msg,
            id: msg.id?.toString() || Date.now().toString(),
          }));
          formattedMessages.forEach((msg) => addMessage(msg));
        }

        setIsInitialized(true);
      } catch (error) {
        console.error("Error loading data:", error);
        setIsInitialized(true);
      }
    };

    initializeData();
  }, [_hasHydrated, files.length, messages.length, addFile, addMessage]);

  // Sync streaming messages with store messages
  useEffect(() => {
    // Update store messages when streaming messages change
    if (streamingMessages.length > 0) {
      const formattedMessages = streamingMessages
        .filter((msg) => msg.role !== "system") // Filter out system messages
        .map((msg) => ({
          ...msg,
          role: msg.role as "user" | "assistant", // Type assertion since we filtered out system
          timestamp: new Date(),
        }));

      // Only update if messages are different (compare lengths and last message content to avoid infinite loops)
      const lastStreamingMessage =
        formattedMessages[formattedMessages.length - 1];
      const lastStoreMessage = messages[messages.length - 1];

      if (
        formattedMessages.length !== messages.length ||
        (lastStreamingMessage &&
          lastStoreMessage &&
          lastStreamingMessage.content !== lastStoreMessage.content)
      ) {
        // Clear existing messages and add new ones
        clearMessages();
        formattedMessages.forEach((msg) => addMessage(msg));
      }
    }
  }, [streamingMessages, clearMessages, addMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessages]);

  // Debug files state changes
  useEffect(() => {
    console.log(
      "Files state updated:",
      files.map((f) => ({
        id: f.id,
        path: f.path,
        language: f.language,
        content: f.content.substring(0, 50) + "...",
      }))
    );
    console.log("Files count:", files.length);
  }, [files]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Save user message to database
    await saveChatMessage("user", input);

    // Use the streaming chat hook's submit handler
    await streamingHandleSubmit(e);
  };

  const handleEditorChange = (value: string | undefined) => {
    if (!selectedFileId || value === undefined) return;

    updateFile(selectedFileId, value);
  };

  const handleFileCopy = async (fileId: string) => {
    const file = files.find((f) => f.id === fileId);
    if (file) {
      await navigator.clipboard.writeText(file.content);
    }
  };

  const handleFileDownload = (fileId: string) => {
    const file = files.find((f) => f.id === fileId);
    if (file) {
      const blob = new Blob([file.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.path.split("/").pop() || "file";
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleDownloadAll = async () => {
    const zip = new JSZip();

    files.forEach((file) => {
      const filePath = file.path.startsWith("/")
        ? file.path.substring(1)
        : file.path;
      zip.file(filePath, file.content);
    });

    const content = await zip.generateAsync({ type: "blob" });
    const url = URL.createObjectURL(content);
    const a = document.createElement("a");
    a.href = url;
    a.download = "generated-code.zip";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSaveToAkave = async () => {
    if (!isAkaveEnabled) {
      alert("Akave storage is not available");
      return;
    }

    try {
      console.log("Saving files to Akave...");

      for (const file of files) {
        await akaveService.uploadFile(file.content, file.path, {
          language: file.language,
          savedAt: new Date().toISOString(),
          source: "manual-save",
        });
      }

      // Show success notification
      const notification = document.createElement("div");
      notification.className =
        "fixed top-4 right-4 bg-foreground text-background px-4 py-2 rounded-full shadow-lg z-50";
      notification.textContent = `☁️ All files saved to Akave storage`;
      document.body.appendChild(notification);

      setTimeout(() => {
        document.body.removeChild(notification);
      }, 3000);
    } catch (error) {
      console.error("Error saving to Akave:", error);
      alert("Failed to save files to Akave storage");
    }
  };

  const handleClearAll = async () => {
    clearFiles();
    clearMessages();
    await clearFiles();
    await db.chatMessages.clear();
    console.log("All data cleared");
  };

  const getLanguageFromPath = (path: string) => {
    const ext = path.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "js":
      case "jsx":
      case "mjs":
        return "javascript";
      case "ts":
      case "tsx":
        return "typescript";
      case "css":
        return "css";
      case "scss":
        return "scss";
      case "html":
        return "html";
      case "json":
        return "json";
      case "py":
        return "python";
      case "java":
        return "java";
      case "cpp":
      case "cc":
      case "cxx":
        return "cpp";
      case "c":
        return "c";
      case "go":
        return "go";
      case "rs":
        return "rust";
      case "php":
        return "php";
      case "rb":
        return "ruby";
      case "sql":
        return "sql";
      case "md":
        return "markdown";
      case "xml":
        return "xml";
      case "yaml":
      case "yml":
        return "yaml";
      case "cdc":
        return "cadence";
      default:
        return "plaintext";
    }
  };

  const extractAndSaveContracts = async (
    content: string,
    userPrompt: string
  ) => {
    try {
      console.log(
        "Extracting contracts from content:",
        content.substring(0, 200) + "..."
      );

      // Extract code blocks from the AI response
      const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
      const contracts: GeneratedFile[] = [];
      let match;

      while ((match = codeBlockRegex.exec(content)) !== null) {
        const language = match[1] || "cadence";
        const code = match[2].trim();

        console.log(
          `Found code block: language=${language}, length=${code.length}`
        );

        if (code.length > 50) {
          // Only save substantial code blocks
          // Generate filename based on content analysis
          const filename = generateFilename(code, userPrompt, language);

          const contract: GeneratedFile = {
            id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}_${Math.floor(Math.random() * 10000)}`,
            path: filename,
            content: code,
            language: language,
            isModified: true,
          };

          contracts.push(contract);
          console.log(`Added contract: ${filename}`, {
            id: contract.id,
            path: contract.path,
            language: contract.language,
          });
        }
      }

      // If we found contracts, add them to the files
      if (contracts.length > 0) {
        console.log(`Found ${contracts.length} contracts to add to files`);

        // Add each contract to the store
        contracts.forEach((contract) => {
          addFile(contract);
          console.log("Added file to store:", contract.path);
        });

        // Save to database
        saveFiles(contracts);

        // Upload to Akave if enabled
        if (isAkaveEnabled) {
          try {
            console.log("Uploading contracts to Akave...");
            for (const contract of contracts) {
              await akaveService.uploadFile(contract.content, contract.path, {
                language: contract.language,
                generatedAt: new Date().toISOString(),
                source: "ai-chat",
              });
            }
            console.log("Contracts uploaded to Akave successfully");
          } catch (akaveError) {
            console.error("Error uploading to Akave:", akaveError);
            // Don't fail the entire process if Akave upload fails
          }
        }

        console.log(
          `Extracted ${contracts.length} contract(s) from AI response`
        );

        // Show notification
        const notification = document.createElement("div");
        notification.className =
          "fixed top-4 right-4 bg-foreground text-background px-4 py-2 rounded-full shadow-lg z-50";
        notification.textContent = `📄 Generated ${contracts.length} contract(s)${isAkaveEnabled ? " and uploaded to Akave" : ""} and added to editor`;
        document.body.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 3000);
      }
    } catch (error) {
      console.error("Error extracting contracts:", error);
    }
  };

  const generateFilename = (
    code: string,
    userPrompt: string,
    language: string
  ): string => {
    console.log("Generating filename for:", {
      userPrompt,
      language,
      codeLength: code.length,
    });

    // Analyze the code to determine what type of contract it is
    const lowerCode = code.toLowerCase();
    const lowerPrompt = userPrompt.toLowerCase();

    let baseName = "Contract";
    let extension = language === "cadence" ? ".cdc" : `.${language}`;

    // Detect contract type from code content and prompt
    if (
      lowerCode.includes("nft") ||
      lowerCode.includes("nonfungibletoken") ||
      lowerPrompt.includes("nft")
    ) {
      baseName = "NFT";
    } else if (
      lowerCode.includes("fungibletoken") ||
      lowerCode.includes("ft") ||
      lowerPrompt.includes("token")
    ) {
      baseName = "FungibleToken";
    } else if (
      lowerCode.includes("marketplace") ||
      lowerPrompt.includes("marketplace")
    ) {
      baseName = "Marketplace";
    } else if (
      lowerCode.includes("staking") ||
      lowerCode.includes("stake") ||
      lowerPrompt.includes("stake")
    ) {
      baseName = "Staking";
    } else if (
      lowerCode.includes("dao") ||
      lowerCode.includes("governance") ||
      lowerPrompt.includes("dao")
    ) {
      baseName = "DAO";
    } else if (
      lowerCode.includes("auction") ||
      lowerPrompt.includes("auction")
    ) {
      baseName = "Auction";
    } else if (lowerCode.includes("vault") || lowerPrompt.includes("vault")) {
      baseName = "Vault";
    } else if (lowerCode.includes("swap") || lowerPrompt.includes("swap")) {
      baseName = "Swap";
    } else if (
      lowerCode.includes("lending") ||
      lowerPrompt.includes("lending")
    ) {
      baseName = "Lending";
    } else if (
      lowerCode.includes("utility") ||
      lowerPrompt.includes("utility")
    ) {
      baseName = "Utility";
    } else if (
      lowerCode.includes("counter") ||
      lowerPrompt.includes("counter")
    ) {
      baseName = "Counter";
    } else if (lowerCode.includes("hello") || lowerPrompt.includes("hello")) {
      baseName = "HelloWorld";
    } else if (lowerCode.includes("simple") || lowerPrompt.includes("simple")) {
      baseName = "Simple";
    }

    // Try to extract contract name from the code itself
    const contractNameMatch = code.match(/pub\s+contract\s+(\w+)/i);
    if (contractNameMatch && contractNameMatch[1]) {
      baseName = contractNameMatch[1];
    }

    // Add timestamp to make filename unique
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    const filename = `contracts/${baseName}_${timestamp}${extension}`;

    console.log("Generated filename:", filename);
    return filename;
  };

  if (!isInitialized || !_hasHydrated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-foreground/80">
            {!_hasHydrated ? "Hydrating store..." : "Loading workspace..."}
          </p>
        </div>
      </div>
    );
  }

  const editorTheme = resolvedTheme === "dark" ? "vs-dark" : "vs"

  return (
    <div className="min-h-screen bg-background">
      <div className="h-screen flex flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card/80 p-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-muted/60 rounded-full flex items-center justify-center border border-border">
                <Image
                  src="/images/flowZmithsLogo.svg"
                  alt="Flowzmith"
                  width={32}
                  height={32}
                />
              </div>
              <div>
                <div className="flex items-center space-x-3">
                  <span className="text-xl font-semibold text-foreground">
                    Flowzmith
                  </span>
                </div>
                <p className="text-sm text-foreground/80">
                  Generate and edit code with AI assistance
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <ThemeSwitcher />
              {/* Akave Status Indicator */}
              <div className="flex items-center gap-1">
                <div
                  className={`w-2 h-2 rounded-full ${
                    akaveStatus === "available"
                      ? "bg-primary"
                      : akaveStatus === "checking"
                        ? "bg-muted-foreground"
                        : "bg-destructive"
                  }`}
                ></div>
                <span className="text-xs text-foreground/80">
                  {akaveStatus === "available"
                    ? "Akave"
                    : akaveStatus === "checking"
                      ? "Checking..."
                      : "Akave Offline"}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  // Test adding a file to the store
                  const testFile = {
                    id: `test_${Date.now()}`,
                    path: "test/TestFile.cdc",
                    content: "pub contract Test { }",
                    language: "cadence",
                    isModified: true,
                  };
                  addFile(testFile);
                  console.log("Added test file to store");
                }}
              >
                Test File
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsTerminalOpen(!isTerminalOpen)}
              >
                <Terminal className="w-4 h-4 mr-2" />
                Terminal
              </Button>
              {files.length > 0 && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDownloadAll}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download All
                  </Button>
                  {isAkaveEnabled && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleSaveToAkave}
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Save to Akave
                    </Button>
                  )}
                  <Button variant="outline" size="sm" onClick={handleClearAll}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear All
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          <PanelGroup direction="horizontal">
            {/* Chat Panel */}
            <Panel defaultSize={30} minSize={20}>
              <div className="h-full flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                  {streamingMessages.length === 0 ? (
                    <div className="text-center text-foreground/80">
                      <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="mb-2">Welcome to Flowzmith!</p>
                      <p className="text-sm">
                        Describe what you want to build and I'll generate the
                        code for you.
                      </p>
                    </div>
                  ) : (
                    <>
                      {console.log(
                        "Rendering messages:",
                        streamingMessages.map((m) => ({
                          id: m.id,
                          role: m.role,
                          contentLength: m.content.length,
                        }))
                      )}
                      {streamingMessages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex gap-3 ${
                            message.role === "assistant"
                              ? "flex-row"
                              : "flex-row-reverse"
                          }`}
                        >
                          <div
                            className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                              message.role === "assistant"
                                ? "bg-primary/10"
                                : "bg-muted/60"
                            }`}
                          >
                            {message.role === "assistant" ? (
                              <Bot className="w-4 h-4 text-primary" />
                            ) : (
                              <User className="w-4 h-4 text-foreground" />
                            )}
                          </div>
                          <div
                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                              message.role === "assistant"
                                ? "bg-card/80 border border-border/70 text-foreground"
                                : "bg-foreground text-background"
                            }`}
                          >
                            <div className="text-sm whitespace-pre-wrap">
                              {message.content}
                            </div>
                          </div>
                        </div>
                      ))}
                    </>
                  )}
                  {isLoading && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-primary/10">
                        <Bot className="w-4 h-4 text-primary" />
                      </div>
                      <div className="bg-muted rounded-2xl px-4 py-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                          <div
                            className="w-2 h-2 bg-primary rounded-full animate-bounce"
                            style={{ animationDelay: "0.1s" }}
                          />
                          <div
                            className="w-2 h-2 bg-primary rounded-full animate-bounce"
                            style={{ animationDelay: "0.2s" }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-border bg-card/80">
                  <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                      value={input}
                      onChange={handleInputChange}
                      placeholder="Describe what you want to build..."
                      className="flex-1 bg-background border border-border rounded-2xl px-4 py-3 text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary"
                      disabled={isLoading}
                    />
                    <Button
                      type="submit"
                      disabled={isLoading || !input.trim()}
                      className="bg-primary text-primary-foreground hover:bg-primary/90 px-6 py-3 rounded-2xl"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </form>
                </div>
              </div>
            </Panel>

            <PanelResizeHandle className="w-2 bg-border hover:bg-muted-foreground/30 transition-colors" />

            {/* Editor Panel */}
            <Panel minSize={30}>
              <div className="h-full flex">
                {/* File Tree */}
                <div className="overflow-y-auto w-64 border-r border-border bg-card/80 custom-scrollbar">
                  <FileTree
                    files={files}
                    selectedFileId={selectedFileId}
                    onFileSelect={selectFile}
                    onFileDownload={handleFileDownload}
                    onFileCopy={handleFileCopy}
                  />
                </div>

                {/* Editor */}
                <div className="flex-1 flex flex-col">
                  <div className="border-b border-border bg-card/80 p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-foreground/80" />
                        <span className="text-sm font-medium">
                          {selectedFile?.path || "No file selected"}
                        </span>
                        {selectedFile?.isModified && (
                          <span className="text-xs text-orange-600">
                            • Modified
                          </span>
                        )}
                      </div>
                      {selectedFile && (
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => handleFileCopy(selectedFile.id)}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => handleFileDownload(selectedFile.id)}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex-1">
                    {selectedFile ? (
                      <Editor
                        height="100%"
                        language={getLanguageFromPath(selectedFile.path)}
                        value={selectedFile.content}
                        onChange={handleEditorChange}
                        theme={editorTheme}
                        options={{
                          minimap: { enabled: false },
                          fontSize: 14,
                          wordWrap: "on",
                          automaticLayout: true,
                          scrollBeyondLastLine: false,
                        }}
                      />
                    ) : (
                        <div className="h-full flex items-center justify-center text-foreground/80">
                        <div className="text-center">
                          <FolderOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
                          <p>Select a file to edit</p>
                          <p className="text-sm">
                            Or generate code using the chat interface
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </Panel>
          </PanelGroup>
        </div>
      </div>

      {/* Terminal Component */}
      <TerminalComponent
        isOpen={isTerminalOpen}
        onToggle={() => setIsTerminalOpen(!isTerminalOpen)}
      />
    </div>
  );
}
