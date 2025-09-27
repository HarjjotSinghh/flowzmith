# Cadence 1.0 NFT Contract Deployment: Critical Learnings for LLMs

## Overview
This document captures critical learnings from deploying a NonFungibleToken contract in Cadence 1.0 on Flow testnet. These insights are essential for LLMs working with Flow blockchain smart contracts.

## Key Deployment Challenges and Solutions

### 1. Import Address Corrections
**Problem**: Cadence 1.0 uses different import addresses than previous versions.
**Solution**: Always use the correct testnet import addresses:
```cadence
import NonFungibleToken from 0x631e88ae7f1d7c20
import ViewResolver from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20
```

### 2. Interface Conformance Requirements

#### NonFungibleToken.NFT Interface
**Critical**: The NFT resource must include a `createEmptyCollection` method:
```cadence
access(all) resource NFT: NonFungibleToken.NFT {
    access(all) let id: UInt64
    
    access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
        return <-SimpleNFT.createEmptyCollection(nftType: Type<@SimpleNFT.NFT>())
    }
    
    // Other required methods...
}
```

#### NonFungibleToken.Collection Interface
**Required Methods**:
- `getSupportedNFTTypes()`: Returns supported NFT types
- `isSupportedNFTType(type: Type)`: Checks if type is supported
- `createEmptyCollection()`: Creates new collection (without nftType parameter in Collection resource)

**Method Signature Corrections**:
```cadence
// Correct withdraw signature
access(NonFungibleToken.Withdraw) fun withdraw(withdrawID: UInt64): @{NonFungibleToken.NFT}

// Correct deposit signature  
access(all) fun deposit(token: @{NonFungibleToken.NFT})

// Correct borrowNFT signature
access(all) fun borrowNFT(_ id: UInt64): &{NonFungibleToken.NFT}?
```

### 3. createEmptyCollection Method Complexity

**Contract Level**: Must accept `nftType: Type` parameter:
```cadence
access(all) fun createEmptyCollection(nftType: Type): @{NonFungibleToken.Collection} {
    return <- create Collection()
}
```

**NFT Resource Level**: Must include the method:
```cadence
access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
    return <-SimpleNFT.createEmptyCollection(nftType: Type<@SimpleNFT.NFT>())
}
```

**Collection Resource Level**: No nftType parameter:
```cadence
access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
    return <-SimpleNFT.createEmptyCollection(nftType: Type<@SimpleNFT.NFT>())
}
```

### 4. Contract-Level Required Methods

**ViewResolver Conformance**:
```cadence
access(all) fun getContractViews(resourceType: Type?): [Type] {
    return []
}

access(all) fun resolveContractView(resourceType: Type?, viewType: Type): AnyStruct? {
    return nil
}
```

### 5. Type System and Casting

**Critical**: Proper type annotations and casting:
```cadence
// Correct type casting for collections
return <-create Collection() as @{NonFungibleToken.Collection}

// Proper type specification
Type<@SimpleNFT.NFT>()
```

## Common Error Patterns

### 1. "Invalid use of interface as type"
**Cause**: Incorrect return type annotation
**Fix**: Use `@{NonFungibleToken.Collection}` instead of `NonFungibleToken.Collection`

### 2. "Too few arguments" 
**Cause**: Missing `nftType` parameter in `createEmptyCollection` calls
**Fix**: Always pass `nftType: Type<@YourContract.NFT>()`

### 3. "Does not conform to interface"
**Cause**: Missing required methods or incorrect signatures
**Fix**: Implement all interface methods with exact signatures

### 4. "Conformance mismatch"
**Cause**: Method signatures don't match interface requirements
**Fix**: Check parameter names, types, and access modifiers

## Deployment Best Practices

### 1. Use flow.json Configuration
```json
{
  "contracts": {
    "SimpleNFT": "./cadence/contracts/CorrectedContract.cdc"
  },
  "deployments": {
    "testnet": {
      "testnet-account": ["SimpleNFT"]
    }
  }
}
```

### 2. Deploy with Project Command
```bash
flow project deploy --network testnet
```

### 3. Verify Interface Conformance
Always check that your contract implements:
- All required interface methods
- Correct method signatures
- Proper access modifiers
- Required type annotations

## Interface Method Reference

### NonFungibleToken.Collection Required Methods:
1. `withdraw(withdrawID: UInt64): @{NonFungibleToken.NFT}`
2. `deposit(token: @{NonFungibleToken.NFT})`
3. `getIDs(): [UInt64]`
4. `borrowNFT(_ id: UInt64): &{NonFungibleToken.NFT}?`
5. `getSupportedNFTTypes(): {Type: Bool}`
6. `isSupportedNFTType(type: Type): Bool`
7. `createEmptyCollection(): @{NonFungibleToken.Collection}`

### NonFungibleToken.NFT Required Methods:
1. `createEmptyCollection(): @{NonFungibleToken.Collection}`

### Contract Level Required Methods:
1. `createEmptyCollection(nftType: Type): @{NonFungibleToken.Collection}`
2. `getContractViews(resourceType: Type?): [Type]`
3. `resolveContractView(resourceType: Type?, viewType: Type): AnyStruct?`

## Debugging Strategies

### 1. Read Error Messages Carefully
- "conformance mismatch" → Check method signatures
- "missing member" → Add required methods
- "invalid use of interface" → Fix type annotations

### 2. Verify Import Addresses
Always use current testnet addresses for Cadence 1.0

### 3. Check Interface Documentation
Reference official Flow documentation for exact interface requirements

### 4. Test Incrementally
Deploy frequently to catch conformance issues early

## Success Indicators

A successful deployment will show:
```
✅ SimpleNFT -> 0xYourAddress (1 contracts)
```

## Specific Error Messages and Solutions

### Error: "invalid use of interface as type"
```
error: invalid use of interface as type
  --> CorrectedContract.cdc:XX:XX
   |
XX |     access(all) fun createEmptyCollection(): NonFungibleToken.Collection {
   |                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected `{NonFungibleToken.Collection}`, got `NonFungibleToken.Collection`
```
**Solution**: Use `@{NonFungibleToken.Collection}` instead of `NonFungibleToken.Collection`

### Error: "too few arguments"
```
error: too few arguments
  --> CorrectedContract.cdc:XX:XX
   |
XX |         return <-SimpleNFT.createEmptyCollection()
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ missing argument for parameter `nftType`
```
**Solution**: Pass the nftType parameter: `SimpleNFT.createEmptyCollection(nftType: Type<@SimpleNFT.NFT>())`

### Error: "does not conform to interface"
```
error: `SimpleNFT.Collection` does not conform to interface `NonFungibleToken.Collection`
  --> CorrectedContract.cdc:XX:XX
   |
XX |     access(all) resource Collection: NonFungibleToken.Collection {
   |                          ^^^^^^^^^^ missing members: `getSupportedNFTTypes`, `isSupportedNFTType`
```
**Solution**: Implement all required interface methods

### Error: "conformance mismatch"
```
error: conformance mismatch
  --> CorrectedContract.cdc:XX:XX
   |
XX |     access(all) fun withdraw(id: UInt64): @{NonFungibleToken.NFT} {
   |                     ^^^^^^^^ parameter name mismatch: expected `withdrawID`, got `id`
```
**Solution**: Use exact parameter names from interface: `withdraw(withdrawID: UInt64)`

## Migration from Pre-1.0 Cadence

### Key Changes in Cadence 1.0:
1. **Import addresses changed** - Use 0x631e88ae7f1d7c20 for testnet
2. **Interface conformance stricter** - All methods must be implemented
3. **Type system more rigid** - Proper type annotations required
4. **Access control refined** - Specific access modifiers needed

### Common Migration Issues:
1. **Old import addresses** - Update to Cadence 1.0 addresses
2. **Missing interface methods** - Add all required methods
3. **Incorrect type annotations** - Use proper interface types
4. **Access modifier mismatches** - Update to required access levels

## Troubleshooting Workflow

### Step 1: Check Import Addresses
Verify all imports use correct Cadence 1.0 testnet addresses

### Step 2: Validate Interface Conformance
Ensure all interface methods are implemented with correct signatures

### Step 3: Verify Type Annotations
Check that all type annotations match interface requirements

### Step 4: Test Access Modifiers
Confirm access modifiers match interface specifications

### Step 5: Deploy Incrementally
Deploy frequently to catch issues early in development

## Advanced Debugging Techniques

### 1. Use Flow CLI Linting
```bash
flow cadence lint ./cadence/contracts/YourContract.cdc
```

### 2. Check Interface Documentation
```bash
flow cadence doc NonFungibleToken
```

### 3. Validate with Emulator First
```bash
flow emulator start
flow project deploy --network emulator
```

### 4. Compare with Working Examples
Reference official Flow NFT examples for Cadence 1.0

## Performance Considerations

### 1. Resource Management
- Always use `<-` for resource moves
- Properly destroy resources when needed
- Avoid resource leaks

### 2. Gas Optimization
- Minimize complex operations in transactions
- Use efficient data structures
- Batch operations when possible

### 3. Storage Efficiency
- Use appropriate storage paths
- Minimize storage overhead
- Clean up unused resources

## Final Notes for LLMs

1. **Always verify interface conformance** before deployment
2. **Use exact method signatures** from the interface
3. **Include all required methods** even if they return empty/default values
4. **Pay attention to access modifiers** (access(all), access(NonFungibleToken.Withdraw))
5. **Use proper type annotations** throughout the contract
6. **Test with flow.json configuration** for reliable deployment
7. **Read error messages carefully** - they often contain exact solutions
8. **Use incremental deployment** to catch issues early
9. **Reference official documentation** for interface requirements
10. **Test on emulator first** before testnet deployment

## Resources for Further Learning

- [Flow Developer Portal](https://developers.flow.com/)
- [Cadence Language Reference](https://cadence-lang.org/)
- [NonFungibleToken Standard](https://github.com/onflow/flow-nft)
- [Flow CLI Documentation](https://developers.flow.com/tools/flow-cli)

This documentation should significantly reduce deployment issues for future Cadence 1.0 NFT contracts and provide a comprehensive troubleshooting guide for common issues.