import { z } from "zod";

// ============================================================================
// CLI Command Definitions
// ============================================================================

export const CLICommandType = z.enum([
  "setup",
  "create_contract",
  "deploy_contract",
  "search_docs",
  "upload_docs",
  "browse_docs",
  "crawl_docs",
  "firecrawl_search",
  "list_deployments",
  "status",
  "wizard",
  "generate_from_context",
  "mcp_explorer",
  "flow_init",
  "flow_deploy",
  "flow_status",
  "flow_list",
  "flow_generate_deploy",
  "flow_auto",
  "chat"
]);

export type CLICommandType = z.infer<typeof CLICommandType>;

// ============================================================================
// Command Metadata
// ============================================================================

export interface CLICommand {
  id: CLICommandType;
  name: string;
  description: string;
  icon: string;
  category: "contract" | "deployment" | "documentation" | "flow" | "system" | "chat";
  requiresInput: boolean;
  steps?: CommandStep[];
}

export interface CommandStep {
  id: string;
  title: string;
  description?: string;
  fields: CommandField[];
}

export interface CommandField {
  name: string;
  label: string;
  type: "text" | "textarea" | "select" | "file" | "checkbox" | "number";
  required: boolean;
  placeholder?: string;
  options?: { label: string; value: string }[];
  defaultValue?: string | number | boolean;
  helpText?: string;
}

// ============================================================================
// Request/Response Schemas
// ============================================================================

// Contract Creation
export const CreateContractRequestSchema = z.object({
  requirements: z.string().min(1, "Requirements are required"),
  context: z.string().optional(),
  pre_conditions: z.record(z.any()).optional(),
  post_conditions: z.record(z.any()).optional(),
  network: z.enum(["emulator", "testnet", "mainnet"]).default("emulator"),
  input_method: z.enum(["natural_language", "template", "file", "direct_code", "markdown_context", "firecrawl"]).optional(),
});

export type CreateContractRequest = z.infer<typeof CreateContractRequestSchema>;

export const CreateContractResponseSchema = z.object({
  status: z.enum(["success", "failed", "pending"]),
  submission_id: z.string().optional(),
  generated_contract_code: z.string().optional(),
  config_content: z.any().optional(),
  contract_name: z.string().optional(),
  validation_status: z.string().optional(),
  error: z.string().optional(),
  project_dir: z.string().optional(),
});

export type CreateContractResponse = z.infer<typeof CreateContractResponseSchema>;

// Deployment
export const DeployContractRequestSchema = z.object({
  contract_id: z.string().optional(),
  contract_name: z.string(),
  contract_content: z.string(),
  network: z.enum(["emulator", "testnet", "mainnet"]).default("emulator"),
  auto_deploy: z.boolean().default(true),
  account_config: z.object({
    address: z.string().optional(),
    private_key: z.string().optional(),
  }).optional(),
});

export type DeployContractRequest = z.infer<typeof DeployContractRequestSchema>;

export const DeployContractResponseSchema = z.object({
  status: z.enum(["deployed", "failed", "pending", "queued"]),
  deployment_id: z.string().optional(),
  project_id: z.string().optional(),
  project_dir: z.string().optional(),
  transaction_id: z.string().optional(),
  deployment_output: z.string().optional(),
  error: z.string().optional(),
});

export type DeployContractResponse = z.infer<typeof DeployContractResponseSchema>;

// Documentation Search
export const SearchDocsRequestSchema = z.object({
  query: z.string().min(1, "Search query is required"),
  limit: z.number().min(1).max(100).default(20),
});

export type SearchDocsRequest = z.infer<typeof SearchDocsRequestSchema>;

export const SearchDocsResponseSchema = z.object({
  results: z.array(z.object({
    id: z.string(),
    title: z.string(),
    content: z.string(),
    category: z.string().optional(),
    relevance_score: z.number().optional(),
  })),
  total: z.number(),
});

export type SearchDocsResponse = z.infer<typeof SearchDocsResponseSchema>;

// Flow Project
export const FlowInitRequestSchema = z.object({
  name: z.string().optional(),
  directory: z.string().optional(),
});

export type FlowInitRequest = z.infer<typeof FlowInitRequestSchema>;

export const FlowInitResponseSchema = z.object({
  status: z.enum(["success", "failed"]),
  project_dir: z.string().optional(),
  project_id: z.string().optional(),
  error: z.string().optional(),
});

export type FlowInitResponse = z.infer<typeof FlowInitResponseSchema>;

// System Status
export const SystemStatusResponseSchema = z.object({
  server_status: z.enum(["healthy", "unhealthy"]),
  database_status: z.enum(["connected", "disconnected"]),
  total_contracts: z.number(),
  successful_deployments: z.number(),
  pending_submissions: z.number(),
  total_docs: z.number(),
});

export type SystemStatusResponse = z.infer<typeof SystemStatusResponseSchema>;

// Generate from Context
export const GenerateFromContextRequestSchema = z.object({
  requirements: z.string().min(1, "Requirements are required"),
  context_dir: z.string().optional(),
  network: z.enum(["emulator", "testnet", "mainnet"]).default("emulator"),
  stream: z.boolean().default(true),
  auto_deploy: z.boolean().default(false),
  flow_init: z.boolean().default(false),
});

export type GenerateFromContextRequest = z.infer<typeof GenerateFromContextRequestSchema>;

// ============================================================================
// CLI Commands Configuration
// ============================================================================

export const CLI_COMMANDS: CLICommand[] = [
  {
    id: "create_contract",
    name: "Create Contract",
    description: "Create a new smart contract with step-by-step guidance",
    icon: "FileCode",
    category: "contract",
    requiresInput: true,
    steps: [
      {
        id: "requirements",
        title: "Contract Requirements",
        description: "Describe what your contract should do",
        fields: [
          {
            name: "requirements",
            label: "Contract Description",
            type: "textarea",
            required: true,
            placeholder: "Describe your smart contract requirements...",
            helpText: "Be specific about the functionality you need"
          },
          {
            name: "network",
            label: "Target Network",
            type: "select",
            required: true,
            options: [
              { label: "Emulator", value: "emulator" },
              { label: "Testnet", value: "testnet" },
              { label: "Mainnet", value: "mainnet" }
            ],
            defaultValue: "emulator"
          }
        ]
      }
    ]
  },
  {
    id: "deploy_contract",
    name: "Deploy Contract",
    description: "Deploy a smart contract to the blockchain",
    icon: "Rocket",
    category: "deployment",
    requiresInput: true,
    steps: [
      {
        id: "deployment_config",
        title: "Deployment Configuration",
        fields: [
          {
            name: "contract_name",
            label: "Contract Name",
            type: "text",
            required: true,
            placeholder: "MyContract"
          },
          {
            name: "network",
            label: "Network",
            type: "select",
            required: true,
            options: [
              { label: "Emulator", value: "emulator" },
              { label: "Testnet", value: "testnet" },
              { label: "Mainnet", value: "mainnet" }
            ]
          },
          {
            name: "auto_deploy",
            label: "Auto Deploy",
            type: "checkbox",
            required: false,
            defaultValue: true
          }
        ]
      }
    ]
  },
  {
    id: "generate_from_context",
    name: "Generate from Context",
    description: "Generate a contract using local markdown context",
    icon: "Sparkles",
    category: "contract",
    requiresInput: true,
    steps: [
      {
        id: "context_generation",
        title: "Context-Based Generation",
        fields: [
          {
            name: "requirements",
            label: "Contract Requirements",
            type: "textarea",
            required: true,
            placeholder: "Describe the contract you want to build..."
          },
          {
            name: "context_dir",
            label: "Context Directory",
            type: "text",
            required: false,
            placeholder: "context",
            defaultValue: "context"
          },
          {
            name: "network",
            label: "Network",
            type: "select",
            required: true,
            options: [
              { label: "Emulator", value: "emulator" },
              { label: "Testnet", value: "testnet" },
              { label: "Mainnet", value: "mainnet" }
            ]
          },
          {
            name: "auto_deploy",
            label: "Auto Deploy",
            type: "checkbox",
            required: false,
            defaultValue: false
          }
        ]
      }
    ]
  },
  {
    id: "search_docs",
    name: "Search Documentation",
    description: "Search documentation and knowledge base",
    icon: "Search",
    category: "documentation",
    requiresInput: true,
    steps: [
      {
        id: "search",
        title: "Search Query",
        fields: [
          {
            name: "query",
            label: "Search Query",
            type: "text",
            required: true,
            placeholder: "Enter your search query..."
          },
          {
            name: "limit",
            label: "Results Limit",
            type: "number",
            required: false,
            defaultValue: 20
          }
        ]
      }
    ]
  },
  {
    id: "flow_init",
    name: "Initialize Flow Project",
    description: "Initialize a new Flow project with flow init",
    icon: "FolderPlus",
    category: "flow",
    requiresInput: false,
    steps: [
      {
        id: "project_init",
        title: "Project Initialization",
        fields: [
          {
            name: "name",
            label: "Project Name (optional)",
            type: "text",
            required: false,
            placeholder: "Auto-generated if not provided"
          }
        ]
      }
    ]
  },
  {
    id: "flow_list",
    name: "List Flow Projects",
    description: "List all Flow projects",
    icon: "List",
    category: "flow",
    requiresInput: false
  },
  {
    id: "list_deployments",
    name: "List Deployments",
    description: "View all contract deployments",
    icon: "History",
    category: "deployment",
    requiresInput: false
  },
  {
    id: "status",
    name: "System Status",
    description: "Check system status and statistics",
    icon: "Activity",
    category: "system",
    requiresInput: false
  },
  {
    id: "flow_auto",
    name: "Automated Flow Workflow",
    description: "Generate, create MCP server, and deploy to Flow",
    icon: "Zap",
    category: "flow",
    requiresInput: true,
    steps: [
      {
        id: "auto_workflow",
        title: "Automated Workflow",
        description: "This will handle the complete workflow automatically",
        fields: [
          {
            name: "requirements",
            label: "Contract Requirements",
            type: "textarea",
            required: true,
            placeholder: "Describe your contract..."
          }
        ]
      }
    ]
  },
  {
    id: "chat",
    name: "Chat Assistant",
    description: "Chat with AI assistant for guidance",
    icon: "MessageSquare",
    category: "chat",
    requiresInput: false
  }
];

// Export command by ID helper
export function getCommandById(id: CLICommandType): CLICommand | undefined {
  return CLI_COMMANDS.find(cmd => cmd.id === id);
}

// Export commands by category
export function getCommandsByCategory(category: CLICommand["category"]): CLICommand[] {
  return CLI_COMMANDS.filter(cmd => cmd.category === category);
}
