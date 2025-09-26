// DigitalArtNFT.cdc

import FungibleToken from 0xFungibleToken
import NonFungibleToken from 0xNonFungibleToken

pub contract DigitalArtNFT: NonFungibleToken {

    // Events
    pub event ContractInitialized()
    pub event Withdraw(id: UInt64, from: Address?)
    pub event Deposit(id: UInt64, to: Address?)

    // NFT Resource
    pub resource NFT: NonFungibleToken.INFT {
        pub let id: UInt64
        pub let metadata: {String: String}

        init(id: UInt64, metadata: {String: String}) {
            self.id = id
            self.metadata = metadata
        }
    }

    // Collection Resource
    pub resource Collection: NonFungibleToken.Provider, NonFungibleToken.Receiver, NonFungibleToken.CollectionPublic {
        pub var ownedNFTs: @{UInt64: NonFungibleToken.NFT}

        init() {
            self.ownedNFTs <- {}
        }

        // Destroy the collection and withdraw all NFTs
        destroy() {
            destroy self.ownedNFTs
        }

        // Withdraw an NFT from the collection
        pub fun withdraw(withdrawID: UInt64): @NFT {
            let token <- self.ownedNFTs[withdrawID] ?? panic("NFT not found in collection")
            self.ownedNFTs.remove(key: withdrawID)
            emit Withdraw(id: token.id, from: self.owner?.address)
            return <- token as! @DigitalArtNFT.NFT
        }

        // Deposit an NFT into the collection
        pub fun deposit(token: @NonFungibleToken.NFT) {
            let token <- token as! @DigitalArtNFT.NFT
            let id = token.id
            if self.ownedNFTs[id] != nil {
                panic("NFT already exists in collection")
            }
            self.ownedNFTs[id] <-! token
            emit Deposit(id: id, to: self.owner?.address)
        }

        // Get the IDs of the NFTs in the collection
        pub fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        // Get a reference to an NFT in the collection
        pub fun borrowNFT(id: UInt64): &NFT {
            return (&self.ownedNFTs[id] as &NFT?) ?? panic("NFT not found in collection")
        }

        // Borrow a reference to an NFT
        pub fun borrow(id: UInt64): &NFT {
            return (&self.ownedNFTs[id] as &NFT?) ?? panic("NFT not found in collection")
        }
    }

    // Create a new empty collection
    pub fun createEmptyCollection(): @Collection {
        return <- create Collection()
    }

    // Mint a new NFT
    pub fun mintNFT(recipient: &{NonFungibleToken.CollectionPublic}, metadata: {String: String}) {
        let token <- create NFT(id: DigitalArtNFT.nextNFTID, metadata: metadata)
        recipient.deposit(token: <- token)
    }

    // Total supply of NFTs
    pub var totalSupply: UInt64

    // Next available NFT ID
    pub var nextNFTID: UInt64

    init() {
        self.totalSupply = 0
        self.nextNFTID = 0
        // Store the collection in the contract storage
        self.account.save(<- create Collection(), to: /storage/NFTCollection)
        self.account.link<&{NonFungibleToken.CollectionPublic}>(/public/NFTCollection, target: /storage/NFTCollection)
        emit ContractInitialized()
    }
}

// Example transaction to mint an NFT
// transaction {
//     let recipient: &{NonFungibleToken.CollectionPublic}
//     prepare(signer: AuthAccount) {
//         self.recipient = signer.getCapability(/public/NFTCollection)
//             .borrow<&{NonFungibleToken.CollectionPublic}>()!
//     }
//     execute {
//         DigitalArtNFT.mintNFT(recipient: self.recipient, metadata: {"name": "My NFT", "description": "This is my NFT"})
//     }
// }

// Example script to get the IDs of NFTs in a collection
// pub fun main(address: Address): [UInt64] {
//     let collection = getAccount(address).getCapability(/public/NFTCollection)
//         .borrow<&{NonFungibleToken.CollectionPublic}>()!
//     return collection.getIDs()
// }