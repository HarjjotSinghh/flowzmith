// Akave O3 Storage Service
// This service provides integration with Akave decentralized storage for AI-generated files

export interface AkaveFile {
  id: string
  name: string
  path: string
  size: number
  url?: string
  cid?: string
  createdAt: Date
  updatedAt: Date
}

export interface AkaveConfig {
  apiKey?: string
  endpoint?: string
  bucket?: string
  // Akave-specific configuration
  gatewayUrl?: string
  nodeUrl?: string
}

class AkaveService {
  private config: AkaveConfig

  constructor(config: AkaveConfig = {}) {
    this.config = {
      endpoint: config.endpoint || process.env.NEXT_PUBLIC_AKAVE_ENDPOINT || 'https://api.akave.xyz',
      bucket: config.bucket || process.env.NEXT_PUBLIC_AKAVE_BUCKET || 'ai-generated-files',
      apiKey: config.apiKey || process.env.AKAVE_API_KEY,
      gatewayUrl: config.gatewayUrl || process.env.NEXT_PUBLIC_AKAVE_GATEWAY || 'https://gateway.akave.xyz',
      nodeUrl: config.nodeUrl || process.env.NEXT_PUBLIC_AKAVE_NODE || 'https://node.akave.xyz',
      ...config
    }
  }

  /**
   * Upload a file to Akave storage
   */
  async uploadFile(
    fileData: string | Blob,
    filename: string,
    metadata?: Record<string, any>
  ): Promise<AkaveFile> {
    try {
      // Convert string to Blob if needed
      const blob = typeof fileData === 'string'
        ? new Blob([fileData], { type: 'text/plain' })
        : fileData

      // Create form data for upload
      const formData = new FormData()
      formData.append('file', blob, filename)

      if (metadata) {
        formData.append('metadata', JSON.stringify(metadata))
      }

      // Make API request to Akave
      const response = await fetch(`${this.config.endpoint}/v1/buckets/${this.config.bucket}/objects`, {
        method: 'POST',
        headers: {
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Akave upload failed: ${response.statusText}`)
      }

      const result = await response.json()

      const akaveFile: AkaveFile = {
        id: result.id || Date.now().toString(),
        name: filename,
        path: result.path || filename,
        size: result.size || blob.size,
        url: result.url,
        cid: result.cid,
        createdAt: new Date(),
        updatedAt: new Date()
      }

      console.log('File uploaded to Akave:', akaveFile)
      return akaveFile
    } catch (error) {
      console.error('Error uploading file to Akave:', error)
      throw error
    }
  }

  /**
   * Retrieve a file from Akave storage
   */
  async retrieveFile(filePath: string): Promise<string> {
    try {
      const response = await fetch(`${this.config.endpoint}/v1/buckets/${this.config.bucket}/objects/${filePath}`, {
        method: 'GET',
        headers: {
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
      })

      if (!response.ok) {
        throw new Error(`Akave retrieval failed: ${response.statusText}`)
      }

      const content = await response.text()
      return content
    } catch (error) {
      console.error('Error retrieving file from Akave:', error)
      throw error
    }
  }

  /**
   * List files in Akave bucket
   */
  async listFiles(prefix?: string): Promise<AkaveFile[]> {
    try {
      const url = prefix
        ? `${this.config.endpoint}/v1/buckets/${this.config.bucket}/objects?prefix=${prefix}`
        : `${this.config.endpoint}/v1/buckets/${this.config.bucket}/objects`

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
      })

      if (!response.ok) {
        throw new Error(`Akave list failed: ${response.statusText}`)
      }

      const result = await response.json()

      return result.objects?.map((obj: any) => ({
        id: obj.id,
        name: obj.name,
        path: obj.path,
        size: obj.size,
        url: obj.url,
        cid: obj.cid,
        createdAt: new Date(obj.created_at),
        updatedAt: new Date(obj.updated_at)
      })) || []
    } catch (error) {
      console.error('Error listing files from Akave:', error)
      throw error
    }
  }

  /**
   * Delete a file from Akave storage
   */
  async deleteFile(filePath: string): Promise<void> {
    try {
      const response = await fetch(`${this.config.endpoint}/v1/buckets/${this.config.bucket}/objects/${filePath}`, {
        method: 'DELETE',
        headers: {
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
      })

      if (!response.ok) {
        throw new Error(`Akave delete failed: ${response.statusText}`)
      }

      console.log('File deleted from Akave:', filePath)
    } catch (error) {
      console.error('Error deleting file from Akave:', error)
      throw error
    }
  }

  /**
   * Get file URL for public access
   */
  getFileUrl(filePath: string): string {
    return `${this.config.gatewayUrl}/${this.config.bucket}/${filePath}`
  }

  /**
   * Check if Akave service is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.endpoint}/health`, {
        method: 'GET',
      })

      return response.ok
    } catch (error) {
      console.error('Akave health check failed:', error)
      return false
    }
  }

  /**
   * Create a new bucket
   */
  async createBucket(bucketName: string): Promise<void> {
    try {
      const response = await fetch(`${this.config.endpoint}/v1/buckets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
        body: JSON.stringify({
          name: bucketName,
        }),
      })

      if (!response.ok) {
        throw new Error(`Bucket creation failed: ${response.statusText}`)
      }

      console.log('Bucket created:', bucketName)
    } catch (error) {
      console.error('Error creating bucket:', error)
      throw error
    }
  }
}

// Export singleton instance
export const akaveService = new AkaveService()

// Export class for custom instances
export { AkaveService }