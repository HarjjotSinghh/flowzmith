# Akave O3 Storage Integration

Akave O3 is a decentralized, S3-compatible storage API that provides a secure and efficient way to store AI-generated files on the blockchain.

## Overview

This integration allows the AI chat system to automatically store generated contracts and code files in decentralized storage using Akave O3. Files are stored with metadata including language, timestamp, and source information.

## Features

- **Automatic Upload**: AI-generated contracts are automatically uploaded to Akave
- **Manual Upload**: Save files to Akave with a single click
- **Health Monitoring**: Real-time status monitoring of Akave service availability
- **Metadata Storage**: Files include metadata like language, generation time, and source
- **Fallback Support**: Local storage continues to work even if Akave is unavailable

## Setup Instructions

### 1. Environment Variables

Add the following environment variables to your `.env.local` file:

```env
# Akave Configuration
NEXT_PUBLIC_AKAVE_ENDPOINT=https://api.akave.xyz
NEXT_PUBLIC_AKAVE_BUCKET=ai-generated-files
AKAVE_API_KEY=your_akave_api_key_here
NEXT_PUBLIC_AKAVE_GATEWAY=https://gateway.akave.xyz
NEXT_PUBLIC_AKAVE_NODE=https://node.akave.xyz
```

### 2. Optional: Self-Hosted Setup

If you prefer to use a self-hosted Akave instance:

```env
NEXT_PUBLIC_AKAVE_ENDPOINT=http://localhost:8080
NEXT_PUBLIC_AKAVE_BUCKET=ai-generated-files
AKAVE_API_KEY=your_local_api_key
NEXT_PUBLIC_AKAVE_GATEWAY=http://localhost:8080
NEXT_PUBLIC_AKAVE_NODE=http://localhost:8080
```

### 3. Akave Account Setup

1. **Sign up for Akave**: Visit [Akave O3](https://docs.akave.xyz/akave-o3/) to create an account
2. **Get API Key**: Generate an API key from your Akave dashboard
3. **Create Bucket**: Create a bucket for your AI-generated files (or let the app create it automatically)

## API Reference

### AkaveService Class

The main service class provides the following methods:

#### `uploadFile(fileData, filename, metadata?)`
Uploads a file to Akave storage.

```typescript
const akaveFile = await akaveService.uploadFile(
  'pub contract Example { }',
  'example.cdc',
  {
    language: 'cadence',
    generatedAt: new Date().toISOString(),
    source: 'ai-chat'
  }
)
```

#### `retrieveFile(filePath)`
Retrieves a file from Akave storage.

```typescript
const content = await akaveService.retrieveFile('contracts/example.cdc')
```

#### `listFiles(prefix?)`
Lists all files in the bucket, optionally filtered by prefix.

```typescript
const files = await akaveService.listFiles('contracts/')
```

#### `deleteFile(filePath)`
Deletes a file from Akave storage.

```typescript
await akaveService.deleteFile('contracts/example.cdc')
```

#### `checkHealth()`
Checks if the Akave service is available.

```typescript
const isAvailable = await akaveService.checkHealth()
```

#### `createBucket(bucketName)`
Creates a new bucket in Akave.

```typescript
await akaveService.createBucket('my-new-bucket')
```

## Integration Points

### Chat Component

The chat component automatically:
- Checks Akave availability on initialization
- Uploads generated contracts to Akave when available
- Shows status indicator in the header
- Provides manual save button for existing files

### File Metadata

Files stored in Akave include metadata:
- `language`: Programming language of the file
- `generatedAt`: When the file was generated
- `savedAt`: When the file was saved (for manual saves)
- `source`: Source of the file ('ai-chat' or 'manual-save')

## Error Handling

The integration includes robust error handling:
- Graceful degradation when Akave is unavailable
- Local storage continues to work regardless of Akave status
- User notifications for upload success/failure
- Detailed error logging for debugging

## Security Considerations

- API keys are stored securely in environment variables
- Files are uploaded with appropriate metadata for tracking
- No sensitive code or keys are exposed to the client
- Health checks prevent unnecessary API calls when service is down

## Performance

- Automatic uploads happen in the background
- Files are compressed before upload
- Health checks minimize unnecessary API calls
- Local storage provides immediate access while Akave uploads complete

## Troubleshooting

### Common Issues

1. **Akave Service Unavailable**
   - Check your internet connection
   - Verify API key is valid
   - Ensure endpoint URL is correct

2. **Upload Failures**
   - Check file size limits
   - Verify bucket exists
   - Ensure proper API permissions

3. **Status Shows Unavailable**
   - Verify environment variables are set
   - Check Akave service status
   - Confirm API key is valid

### Debug Logging

Enable debug logging in browser console:
```javascript
localStorage.setItem('debug', 'akave:*')
```

## Future Enhancements

- File versioning support
- Batch upload optimization
- File encryption before upload
- Advanced metadata filtering
- Akave bucket management UI
- File sharing capabilities

## Support

For issues or questions:
- [Akave Documentation](https://docs.akave.xyz/akave-o3/)
- [GitHub Issues](https://github.com/your-repo/issues)
- Community Discord (if available)

---

*This integration ensures your AI-generated files are safely stored in decentralized storage while maintaining a smooth user experience.*