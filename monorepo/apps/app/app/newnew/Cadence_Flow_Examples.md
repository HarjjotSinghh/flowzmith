
// HelloWorld.cdc
//
// Welcome to Cadence! This is one of the simplest programs you can deploy on Flow.
//
// The HelloWorld contract contains a single string field and a public getter function.
//
// Follow the "Hello, World!" tutorial to learn more: https://docs.onflow.org/cadence/tutorial/02-hello-world/
access(all) contract HelloWorld {
  // Declare a public field of type String.
  //
  // All fields must be initialized in the init() function.
  access(all) var greeting: String

  // Public function that sets our friendly greeting!
  // In your own applications you may want to tighten up this access control.
  access(all) fun changeGreeting(newGreeting: String) {
    self.greeting = newGreeting
  }

  // Public function that returns our friendly greeting!
  access(all) fun hello(): String {
      return self.greeting
  }

  // The init() function is required if the contract contains any fields.
  init() {
    self.greeting = "Hello, World!"
  }
}


import HelloWorld from 0x06

transaction(greeting: String) {

  prepare(acct: &Account) {
    log(acct.address)
  }

  execute {
    HelloWorld.changeGreeting(newGreeting: greeting)
  }
}


import HelloWorld from 0x06

access(all) fun main(): String {
  return HelloWorld.hello()
}

---


/// quickSort is qsort from "The C Programming Language".
///
/// > Our version of quicksort is not the fastest possible,
/// > but it's one of the simplest.
///
access(all) fun quickSort(_ items: &[AnyStruct], isLess: ((Int, Int): Bool)) {

    fun quickSortPart(leftIndex: Int, rightIndex: Int) {

        if leftIndex >= rightIndex {
            return
        }

        let pivotIndex = (leftIndex + rightIndex) / 2

        items[pivotIndex] <-> items[leftIndex]

        var lastIndex = leftIndex
        var index = leftIndex + 1
        while index <= rightIndex {
            if isLess(index, leftIndex) {
                lastIndex = lastIndex + 1
                items[lastIndex] <-> items[index]
            }
            index = index + 1
        }

        items[leftIndex] <-> items[lastIndex]

        quickSortPart(leftIndex: leftIndex, rightIndex: lastIndex - 1)
        quickSortPart(leftIndex: lastIndex + 1, rightIndex: rightIndex)
    }

    quickSortPart(
        leftIndex: 0,
        rightIndex: items.length - 1
    )
}

access(all) fun main() {
    let items = [5, 3, 7, 6, 2, 9]
    quickSort(
        &items as &[AnyStruct],
        isLess: fun (i: Int, j: Int): Bool {
            return items[i] < items[j]
        }
    )
    log(items)
}

---

access(all) 
struct StorageInfo {
    access(all) let capacity: UInt64
    access(all) let used: UInt64
    access(all) let available: UInt64

    init(capacity: UInt64, used: UInt64, available: UInt64) {
        self.capacity = capacity
        self.used = used
        self.available = available
    }
}

access(all) fun main(addr: Address): StorageInfo {
    let acct: &Account = getAccount(addr)
    return StorageInfo(capacity: acct.storage.capacity,
                      used: acct.storage.used,
                      available: acct.storage.capacity - acct.storage.used)
} 

---
import EVM from 0xEVM

// Get the account balance for a COA account
access(all) fun getEVMBalance(_ address: String): UFix64? {
    return EVM.addressFromString(address).balance().inFLOW()
}

// Get the available account balance for a Flow account
access(all) fun getFlowBalance(_ address: String): UFix64? {
    if let account = Address.fromString(address) {
        // Use available balance instead of total balance
        return getAccount(account).availableBalance
    }
    return nil
}

access(all) fun main(addresses: [String]): {String: UFix64?} {
    let res: {String: UFix64?} = {}

    for addr in addresses {
        let hex = addr[1] == "x" ? addr : "0x".concat(addr)
        if let flowBalance = getFlowBalance(hex) {
            res[hex] = flowBalance
        } else {
            if let evmBalance = getEVMBalance(hex) {
                res[hex] = evmBalance
            }
        }
    }
    return res
}

---

import HybridCustody from 0xHybridCustody
import MetadataViews from 0xMetadataViews

access(all) fun main(parent: Address): {Address: AnyStruct} {
    let acct = getAuthAccount<auth(Storage) &Account>(parent)
    let m = acct.storage.borrow<&HybridCustody.Manager>(from: HybridCustody.ManagerStoragePath)

    if m == nil {
        return {}
    } else {
        var data: {Address: AnyStruct} = {}
        for address in m?.getChildAddresses()! {
            let c = m?.getChildAccountDisplay(address: address) 
            data.insert(key: address, c)
        }
        return data
    }
}

import HybridCustody from 0xHybridCustody

access(all) fun main(parent: Address): [Address] {
    let acct = getAuthAccount<auth(Storage) &Account>(parent)
    if let manager = acct.storage.borrow<&HybridCustody.Manager>(from: HybridCustody.ManagerStoragePath) {
        return  manager.getChildAddresses()
    }
    return []
}

---

import EVM from 0xEVM

access(all) fun main(flowAddress: Address): String? {
    if let address: EVM.EVMAddress = getAuthAccount<auth(BorrowValue) &Account>(flowAddress)
        .storage.borrow<&EVM.CadenceOwnedAccount>(from: /storage/evm)?.address() {
        let bytes: [UInt8] = []
        for byte in address.bytes {
            bytes.append(byte)
        }
        return String.encodeHex(bytes)
    }
    return nil
}

import FungibleToken from 0xFungibleToken
import FlowToken from 0xFlowToken
import EVM from 0xEVM

/// Transfers $FLOW from the signer's account Cadence Flow balance to the recipient's hex-encoded EVM address.
/// Note that a COA must have a $FLOW balance in EVM before transferring value to another EVM address.
///
transaction(toEVMAddressHex: String, amount: UFix64, data: [UInt8], gasLimit: UInt64) {

    let coa: auth(EVM.Withdraw, EVM.Call) &EVM.CadenceOwnedAccount
    let recipientEVMAddress: EVM.EVMAddress

    prepare(signer: auth(BorrowValue, SaveValue) &Account) {
        if signer.storage.type(at: /storage/evm) == nil {
            signer.storage.save(<-EVM.createCadenceOwnedAccount(), to: /storage/evm)
        }
        self.coa = signer.storage.borrow<auth(EVM.Withdraw, EVM.Call) &EVM.CadenceOwnedAccount>(from: /storage/evm)
            ?? panic("Could not borrow reference to the signer's bridged account")

        self.recipientEVMAddress = EVM.addressFromString(toEVMAddressHex)
    }

    execute {
        if self.recipientEVMAddress.bytes == self.coa.address().bytes {
            return
        }
        let valueBalance = EVM.Balance(attoflow: 0)
        valueBalance.setFLOW(flow: amount)
        let txResult = self.coa.call(
            to: self.recipientEVMAddress,
            data: data,
            gasLimit: gasLimit,
            value: valueBalance
        )
        assert(
            txResult.status == EVM.Status.failed || txResult.status == EVM.Status.successful,
            message: "evm_error=".concat(txResult.errorMessage).concat("\n")
        )
    }
}


import FungibleToken from 0xFungibleToken
import FlowToken from 0xFlowToken
import EVM from 0xEVM


/// Creates a COA and saves it in the signer's Flow account & passing the given value of Flow into FlowEVM
transaction(amount: UFix64) {
    let sentVault: @FlowToken.Vault
    let auth: auth(IssueStorageCapabilityController, IssueStorageCapabilityController, PublishCapability, SaveValue, UnpublishCapability) &Account

    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue, UnpublishCapability) &Account) {
        let vaultRef = signer.storage.borrow<auth(FungibleToken.Withdraw) &FlowToken.Vault>(
                from: /storage/flowTokenVault
            ) ?? panic("Could not borrow reference to the owner's Vault!")

        self.sentVault <- vaultRef.withdraw(amount: amount) as! @FlowToken.Vault
        self.auth = signer
    }

    execute {
        let coa <- EVM.createCadenceOwnedAccount()
        coa.deposit(from: <-self.sentVault)

        log(coa.balance().inFLOW())
        let storagePath = StoragePath(identifier: "evm")!
        let publicPath = PublicPath(identifier: "evm")!
        self.auth.storage.save<@EVM.CadenceOwnedAccount>(<-coa, to: storagePath)
        let addressableCap = self.auth.capabilities.storage.issue<&EVM.CadenceOwnedAccount>(storagePath)
        self.auth.capabilities.unpublish(publicPath)
        self.auth.capabilities.publish(addressableCap, at: publicPath)
    }
}

---

import FlowStakingCollection from 0xFlowStakingCollection
import FlowIDTableStaking from 0xFlowIDTableStaking
import LockedTokens from 0xLockedTokens
        
access(all) fun main(address: Address): [FlowIDTableStaking.DelegatorInfo]? {
    var res: [FlowIDTableStaking.DelegatorInfo]? = nil

    let inited = FlowStakingCollection.doesAccountHaveStakingCollection(address: address)

    if inited {
        res = FlowStakingCollection.getAllDelegatorInfo(address: address)
    }
    return res
}

---

import FungibleToken from 0xFungibleToken

/// Queries for FT.Vault balance of all FT.Vaults in the specified account.
///
access(all) fun main(address: Address): {String: UFix64} {
    // Get the account
    let account = getAuthAccount<auth(BorrowValue) &Account>(address)
    // Init for return value
    let balances: {String: UFix64} = {}
    // Track seen Types in array
    let seen: [String] = []
    // Assign the type we'll need
    let vaultType: Type = Type<@{FungibleToken.Vault}>()
    // Iterate over all stored items & get the path if the type is what we're looking for
    account.storage.forEachStored(fun (path: StoragePath, type: Type): Bool {
        if !type.isRecovered && (type.isInstance(vaultType) || type.isSubtype(of: vaultType)) {
            // Get a reference to the resource & its balance
            let vaultRef = account.storage.borrow<&{FungibleToken.Balance}>(from: path)!
            // Insert a new values if it's the first time we've seen the type
            if !seen.contains(type.identifier) {
                balances.insert(key: type.identifier, vaultRef.balance)
            } else {
                // Otherwise just update the balance of the vault (unlikely we'll see the same type twice in
                // the same account, but we want to cover the case)
                balances[type.identifier] = balances[type.identifier]! + vaultRef.balance
            }
        }
        return true
    })

    // Add available Flow Token Balance
    balances.insert(key: "availableFlowToken", account.availableBalance)

    return balances
}

---

{
  "testnet": {
    "0xNonFungibleToken": "0x631e88ae7f1d7c20",
    "0xFungibleToken": "0x9a0766d93b6608b7",
    "0xMetadataViews": "0x631e88ae7f1d7c20",
    "0xNFTCatalog": "0x324c34e1c517e4db",
    "0xNFTRetrieval": "0x324c34e1c517e4db",
    "0xFind": "0xa16ab1d0abde3625",
    "0xFlowns": "0xb05b2abb42335e88",
    "0xDomains": "0xb05b2abb42335e88",
    "0xFlowToken": "0x7e60df042a9c0868",
    "0xTransactionGeneration": "0x830c495357676f8b",
    "0xFlowFees": "0x912d5440f7e3769e",
    "0xStringUtils": "0x31ad40c07a2a9788",
    "0xHybridCustody": "0x294e44e1ec6993c6",
    "0xViewResolver": "0x631e88ae7f1d7c20",
    "0xEVM": "0x8c5303eaa26202d6",
    "0xFlowEVMBridge": "0xdfc20aee650fcbdf"
  },
  "mainnet": {
    "0xNonFungibleToken": "0x1d7e57aa55817448",
    "0xFungibleToken": "0xf233dcee88fe0abe",
    "0xMetadataViews": "0x1d7e57aa55817448",
    "0xNFTCatalog": "0x49a7cda3a1eecc29",
    "0xNFTRetrieval": "0x49a7cda3a1eecc29",
    "0xFind": "0x097bafa4e0b48eef",
    "0xFlowns": "0x233eb012d34b0070",
    "0xDomains": "0x233eb012d34b0070",
    "0xFlowFees": "0xf919ee77447b7497",
    "0xFlowToken": "0x1654653399040a61",
    "0xTransactionGeneration": "0xe52522745adf5c34",
    "0xStringUtils": "0xa340dc0a4ec828ab",
    "0xHybridCustody": "0xd8a7e05a7ac670c0",
    "0xViewResolver": "0x1d7e57aa55817448",
    "0xEVM": "0xe467b9dd11fa00df",
    "0xFlowEVMBridge": "0x1e4aa0b87d10b141",
    "0xFlowStakingCollection": "0x8d0e87b65159ae63",
    "0xFlowIDTableStaking": "0x8624b52f9ddcd04a",
    "0xLockedTokens": "0x8d0e87b65159ae63"
  }
}

---

import FlowStakingCollection from 0xFlowStakingCollection
import FlowIDTableStaking from 0xFlowIDTableStaking
import LockedTokens from 0xLockedTokens

 access(all) struct DelegatorInfo {
    access(all) let id: UInt32
    access(all) let nodeID: String
    access(all) let tokensCommitted: UFix64
    access(all) let tokensStaked: UFix64
    access(all) let tokensUnstaking: UFix64
    access(all) let tokensRewarded: UFix64
    access(all) let tokensUnstaked: UFix64
    access(all) let tokensRequestedToUnstake: UFix64
}

access(all) fun main(address: Address): [DelegatorInfo]? {
    var res: [DelegatorInfo]? = nil

    let inited = FlowStakingCollection.doesAccountHaveStakingCollection(address: address)

    if inited {
        let result = FlowStakingCollection.getAllDelegatorInfo(address: address)
        for info in result {
            res.append(DelegatorInfo(id: info.id, nodeID: info.nodeID, tokensCommitted: info.tokensCommitted, tokensStaked: info.tokensStaked, tokensUnstaking: info.tokensUnstaking, tokensRewarded: info.tokensRewarded, tokensUnstaked: info.tokensUnstaked, tokensRequestedToUnstake: info.tokensRequestedToUnstake))
        }
    }
    return res
}

