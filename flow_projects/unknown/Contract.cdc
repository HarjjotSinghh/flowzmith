```cadence
// Property.cdc

import FungibleToken from 0x9a0766d93b6608b7
import NonFungibleToken from 0x631e88ae7f3c7c27

pub contract Property: NonFungibleToken.INFT {
    // Events
    pub event ContractInitialized()
    pub event Withdraw(id: UInt64, from: Address?)
    pub event Deposit(id: UInt64, to: Address?)

    // NFT Resource Interface
    pub resource interface INFT {
        pub let id: UInt64
        pub let owner: Address?
        pub let metadata: {String: String}

        pub fun transfer(to: Capability<&{NonFungibleToken.Receiver}>)
    }

    // Property NFT Resource
    pub resource PropertyNFT: INFT {
        pub let id: UInt64
        pub let owner: Address?
        pub let metadata: {String: String}

        init(id: UInt64, metadata: {String: String}) {
            self.id = id
            self.owner = nil
            self.metadata = metadata
        }

        pub fun transfer(to: Capability<&{NonFungibleToken.Receiver}>) {
            // Check if the recipient is valid
            let receiver = to.borrow()!
            receiver.deposit(token: <-self)
        }
    }

    // Collection Resource
    pub resource Collection: NonFungibleToken.Receiver, NonFungibleToken.Provider {
        pub var ownedNFTs: @{UInt64: NonFungibleToken.NFT}

        init() {
            self.ownedNFTs <- {}
        }

        // Receiver Implementation
        pub fun deposit(token: <-NonFungibleToken.NFT) {
            let token <- token as! PropertyNFT
            let id = token.id
            let oldToken <- self.ownedNFTs[id] <- token
            destroy oldToken
            emit Deposit(id: id, to: self.owner?.address)
        }

        // Provider Implementation
        pub fun withdraw(withdrawID: UInt64): <-NonFungibleToken.NFT {
            let token <- self.ownedNFTs.remove(key: withdrawID)!
            emit Withdraw(id: withdrawID, from: self.owner?.address)
            return <-token
        }

        // Get IDs
        pub fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        // Borrow NFT
        pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
            return (&self.ownedNFTs[id] as &NonFungibleToken.NFT?)!
        }

        // Borrow PropertyNFT
        pub fun borrowPropertyNFT(id: UInt64): &PropertyNFT {
            return (&self.ownedNFTs[id] as! &PropertyNFT?)!
        }

        destroy() {
            destroy self.ownedNFTs
        }
    }

    // Public Functions
    pub fun createEmptyCollection(): <-NonFungibleToken.Collection {
        return <-create Collection()
    }

    // Initialize the contract
    init() {
        // Initialize the NFT ID counter
        self.account.save(<-create PropertyNFT(id: 0, metadata: {}), to: /storage/PropertyNFT0)

        // Save an empty collection to storage
        self.account.save(<-create Collection(), to: /storage/PropertyCollection)

        // Link the collection capability
        self.account.link<&{NonFungibleToken.Receiver, NonFungibleToken.Provider, NonFungibleToken.CollectionPublic}>(
            /public/PropertyCollection,
            target: /storage/PropertyCollection
        )

        emit ContractInitialized()
    }
}

// Example Transaction: Create a new Property NFT
transaction(metadata: {String: String}) {
    prepare(acct: &Account) {
        let collection = acct.getCapability(/public/PropertyCollection)
            .borrow<&{NonFungibleToken.Receiver}>()
            ?? panic("Could not borrow collection reference")

        let nft <- Property.createPropertyNFT(metadata: metadata)
        collection.deposit(token: <-nft)
    }
}

// Example Script: Get Property NFT IDs
pub fun main(address: Address): [UInt64] {
    let collection = getAccount(address)
        .getCapability(/public/PropertyCollection)
        .borrow<&{NonFungibleToken.CollectionPublic}>()
        ?? panic("Could not borrow collection reference")

    return collection.getIDs()
}
```