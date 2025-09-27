// Test script for Akave integration
import { akaveService } from './lib/akave.js'

async function testAkaveIntegration() {
  console.log('Testing Akave integration...')

  try {
    // Test health check
    console.log('1. Testing health check...')
    const isHealthy = await akaveService.checkHealth()
    console.log('Health check result:', isHealthy)

    if (!isHealthy) {
      console.log('Akave service is not available, skipping upload tests')
      return
    }

    // Test file upload
    console.log('2. Testing file upload...')
    const testFile = await akaveService.uploadFile(
      'pub contract TestContract {\n    pub fun hello(): String {\n        return \"Hello from Akave!\"\n    }\n}',
      'test/TestContract.cdc',
      {
        language: 'cadence',
        generatedAt: new Date().toISOString(),
        source: 'test-script'
      }
    )
    console.log('Upload successful:', testFile)

    // Test file listing
    console.log('3. Testing file listing...')
    const files = await akaveService.listFiles('test/')
    console.log('Files in test/ directory:', files)

    // Test file retrieval
    console.log('4. Testing file retrieval...')
    const content = await akaveService.retrieveFile('test/TestContract.cdc')
    console.log('Retrieved content:', content)

    // Test file URL generation
    console.log('5. Testing URL generation...')
    const fileUrl = akaveService.getFileUrl('test/TestContract.cdc')
    console.log('Generated URL:', fileUrl)

    console.log('All tests completed successfully!')

  } catch (error) {
    console.error('Test failed:', error)
  }
}

// Run the test
testAkaveIntegration()