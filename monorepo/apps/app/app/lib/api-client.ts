import type {
  CreateContractRequest,
  CreateContractResponse,
  DeployContractRequest,
  DeployContractResponse,
  SearchDocsRequest,
  SearchDocsResponse,
  FlowInitRequest,
  FlowInitResponse,
  SystemStatusResponse,
  GenerateFromContextRequest,
} from "@flowzmith/schema"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class APIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: response.statusText }))
      throw new Error(error.error || error.detail || "Request failed")
    }

    return response.json()
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    return this.request("/health")
  }

  // Contract Creation
  async createContract(data: CreateContractRequest): Promise<CreateContractResponse> {
    return this.request("/api/contracts/submit", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async generateContractWithContext(
    data: GenerateFromContextRequest
  ): Promise<CreateContractResponse> {
    return this.request("/api/contracts/generate-with-context", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  // Streaming generation
  async *streamGenerateContract(
    data: GenerateFromContextRequest
  ): AsyncGenerator<any> {
    const url = `${this.baseUrl}/api/contracts/generate-with-context/stream`
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error("Stream request failed")
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error("No reader available")
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split("\n")

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6))
            yield data
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  }

  // Contract Deployment
  async deployContract(data: DeployContractRequest): Promise<DeployContractResponse> {
    return this.request("/api/deployments/deploy", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async queueDeployment(data: DeployContractRequest): Promise<DeployContractResponse> {
    return this.request("/api/deployments/queue", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async getDeploymentStatus(deploymentId: string): Promise<DeployContractResponse> {
    return this.request(`/api/deployments/${deploymentId}/status`)
  }

  async listDeployments(limit: number = 50): Promise<{ deployments: any[] }> {
    return this.request(`/api/deployments?limit=${limit}`)
  }

  // Documentation
  async searchDocs(data: SearchDocsRequest): Promise<SearchDocsResponse> {
    return this.request("/api/documentation/search", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async browseDocs(): Promise<{ categories: any[] }> {
    return this.request("/api/documentation/categories")
  }

  // Flow Projects
  async flowInit(data: FlowInitRequest): Promise<FlowInitResponse> {
    return this.request("/api/flow/init", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async flowDeploy(projectId: string, network: string): Promise<DeployContractResponse> {
    return this.request("/api/flow/deploy", {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, network }),
    })
  }

  async flowListProjects(): Promise<{ projects: any[] }> {
    return this.request("/api/flow/projects")
  }

  async flowProjectStatus(projectId: string): Promise<any> {
    return this.request(`/api/flow/projects/${projectId}/status`)
  }

  // System Status
  async getSystemStatus(): Promise<SystemStatusResponse> {
    return this.request("/api/system/status")
  }

  async getDashboardStats(): Promise<any> {
    return this.request("/api/dashboard/stats")
  }

  // Contracts List
  async getContracts(status?: string, limit: number = 50): Promise<{ contracts: any[] }> {
    const params = new URLSearchParams()
    if (status) params.append("status", status)
    params.append("limit", limit.toString())
    return this.request(`/api/contracts?${params}`)
  }

  async getContract(contractId: string): Promise<any> {
    return this.request(`/api/contracts/${contractId}`)
  }
}

export const apiClient = new APIClient()
export default apiClient
