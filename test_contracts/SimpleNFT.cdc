// SimpleNFT.cdc - A basic NFT contract for testing MCP generation

import NonFungibleToken from 0x1d7e57aa55817448
import MetadataViews from 0x1d7e57aa55817448

/// SimpleNFT contract for testing MCP server generation
/// This contract demonstrates basic NFT functionality with events and view functions
pub contract SimpleNFT: NonFungibleToken {
    
    /// Total supply of NFTs in existence
    pub var totalSupply: UInt64
    
    /// Event emitted when the contract is initialized
    pub event ContractInitialized()
    
    /// Event emitted when an NFT is withdrawn from a collection
    pub event Withdraw(id: UInt64, from: Address?)
    
    /// Event emitted when an NFT is deposited to a collection
    pub event Deposit(id: UInt64, to: Address?)
    
    /// Event emitted when an NFT is minted
    pub event Minted(id: UInt64, recipient: Address, metadata: {String: String})
    
    /// Storage and Public Paths
    pub let CollectionStoragePath: StoragePath
    pub let CollectionPublicPath: PublicPath
    pub let MinterStoragePath: StoragePath
    
    /// The core resource that represents a Non Fungible Token
    pub resource NFT: NonFungibleToken.INFT, MetadataViews.Resolver {
        /// The unique ID that each NFT has
        pub let id: UInt64
        
        /// Metadata stored as key-value pairs
        pub let metadata: {String: String}
        
        /// The date this NFT was created
        pub let dateCreated: UFix64
        
        init(
            id: UInt64,
            metadata: {String: String}
        ) {
            self.id = id
            self.metadata = metadata
            self.dateCreated = getCurrentBlock().timestamp
        }
        
        /// Function that returns all the Metadata Views implemented by a Non Fungible Token
        pub fun getViews(): [Type] {
            return [
                Type<MetadataViews.Display>()
            ]
        }
        
        /// Function that resolves a metadata view for this token
        pub fun resolveView(_ view: Type): AnyStruct? {
            switch view {
                case Type<MetadataViews.Display>():
                    return MetadataViews.Display(
                        name: self.metadata["name"] ?? "SimpleNFT",
                        description: self.metadata["description"] ?? "A simple NFT",
                        thumbnail: MetadataViews.HTTPFile(
                            url: self.metadata["image"] ?? ""
                        )
                    )
            }
            return nil
        }
    }
    
    /// Defines the methods that are particular to this NFT contract collection
    pub resource interface SimpleNFTCollectionPublic {
        pub fun deposit(token: @NonFungibleToken.NFT)
        pub fun getIDs(): [UInt64]
        pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
        pub fun borrowSimpleNFT(id: UInt64): &SimpleNFT.NFT? {
            post {
                (result == nil) || (result?.id == id):
                    "Cannot borrow SimpleNFT reference: the ID of the returned reference is incorrect"
            }
        }
    }
    
    /// The resource that will be holding the NFTs inside any account
    pub resource Collection: SimpleNFTCollectionPublic, NonFungibleToken.Provider, NonFungibleToken.Receiver, NonFungibleToken.CollectionPublic, MetadataViews.ResolverCollection {
        /// Dictionary of NFT conforming tokens
        pub var ownedNFTs: @{UInt64: NonFungibleToken.NFT}
        
        init () {
            self.ownedNFTs <- {}
        }
        
        /// Removes an NFT from the collection and moves it to the caller
        pub fun withdraw(withdrawID: UInt64): @NonFungibleToken.NFT {
            let token <- self.ownedNFTs.remove(key: withdrawID) ?? panic("missing NFT")
            
            emit Withdraw(id: token.id, from: self.owner?.address)
            
            return <-token
        }
        
        /// Adds an NFT to the collections dictionary and adds the ID to the id array
        pub fun deposit(token: @NonFungibleToken.NFT) {
            let token <- token as! @SimpleNFT.NFT
            
            let id: UInt64 = token.id
            
            // Add the new token to the dictionary which removes the old one
            let oldToken <- self.ownedNFTs[id] <- token
            
            emit Deposit(id: id, to: self.owner?.address)
            
            destroy oldToken
        }
        
        /// Helper method for getting the collection IDs
        pub fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }
        
        /// Gets a reference to an NFT in the collection so that 
        /// the caller can read its metadata and call its methods
        pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
            return (&self.ownedNFTs[id] as &NonFungibleToken.NFT?)!
        }
        
        /// Gets a reference to an NFT in the collection as a SimpleNFT,
        /// This is safe as there are no functions that can be called on the SimpleNFT
        pub fun borrowSimpleNFT(id: UInt64): &SimpleNFT.NFT? {
            if self.ownedNFTs[id] != nil {
                // Create an authorized reference to allow downcasting
                let ref = (&self.ownedNFTs[id] as auth &NonFungibleToken.NFT?)!
                return ref as! &SimpleNFT.NFT
            }
            
            return nil
        }
        
        /// Gets a reference to the NFT only conforming to the `{MetadataViews.Resolver}`
        /// interface so that the caller can retrieve the views that the NFT
        /// is implementing and resolve them
        pub fun borrowViewResolver(id: UInt64): &AnyResource{MetadataViews.Resolver} {
            let nft = (&self.ownedNFTs[id] as auth &NonFungibleToken.NFT?)!
            let simpleNFT = nft as! &SimpleNFT.NFT
            return simpleNFT as &AnyResource{MetadataViews.Resolver}
        }
        
        destroy() {
            destroy self.ownedNFTs
        }
    }
    
    /// Allows anyone to create a new empty collection
    pub fun createEmptyCollection(): @NonFungibleToken.Collection {
        return <- create Collection()
    }
    
    /// Resource that an admin or something similar would own to be
    /// able to mint new NFTs
    pub resource NFTMinter {
        
        /// Mints a new NFT with a new ID and deposit it in the
        /// recipients collection using their collection reference
        pub fun mintNFT(
            recipient: &{NonFungibleToken.CollectionPublic},
            metadata: {String: String}
        ): UInt64 {
            
            // Create a new NFT
            var newNFT <- create NFT(
                id: SimpleNFT.totalSupply,
                metadata: metadata
            )
            
            let mintedID = newNFT.id
            
            // Deposit it in the recipient's account using their reference
            recipient.deposit(token: <-newNFT)
            
            SimpleNFT.totalSupply = SimpleNFT.totalSupply + UInt64(1)
            
            emit Minted(
                id: mintedID,
                recipient: recipient.owner!.address,
                metadata: metadata
            )
            
            return mintedID
        }
    }
    
    /// Function that resolves a metadata view for this contract
    pub fun resolveView(_ view: Type): AnyStruct? {
        switch view {
            case Type<MetadataViews.NFTCollectionData>():
                return MetadataViews.NFTCollectionData(
                    storagePath: SimpleNFT.CollectionStoragePath,
                    publicPath: SimpleNFT.CollectionPublicPath,
                    providerPath: /private/simpleNFTCollection,
                    publicCollection: Type<&SimpleNFT.Collection{SimpleNFT.SimpleNFTCollectionPublic}>(),
                    publicLinkedType: Type<&SimpleNFT.Collection{SimpleNFT.SimpleNFTCollectionPublic,NonFungibleToken.CollectionPublic,NonFungibleToken.Receiver,MetadataViews.ResolverCollection}>(),
                    providerLinkedType: Type<&SimpleNFT.Collection{SimpleNFT.SimpleNFTCollectionPublic,NonFungibleToken.CollectionPublic,NonFungibleToken.Provider,MetadataViews.ResolverCollection}>(),
                    createEmptyCollectionFunction: (fun (): @NonFungibleToken.Collection {
                        return <-SimpleNFT.createEmptyCollection()
                    })
                )
        }
        return nil
    }
    
    /// Function that returns all the Metadata Views implemented by a Non Fungible Token
    pub fun getViews(): [Type] {
        return [
            Type<MetadataViews.NFTCollectionData>()
        ]
    }
    
    /// Get the total supply of NFTs
    pub fun getTotalSupply(): UInt64 {
        return self.totalSupply
    }
    
    /// Get contract information
    pub fun getContractInfo(): {String: AnyStruct} {
        return {
            "name": "SimpleNFT",
            "totalSupply": self.totalSupply,
            "version": "1.0.0",
            "description": "A simple NFT contract for testing MCP generation"
        }
    }
    
    init() {
        // Initialize the total supply
        self.totalSupply = 0
        
        // Set the named paths
        self.CollectionStoragePath = /storage/simpleNFTCollection
        self.CollectionPublicPath = /public/simpleNFTCollection
        self.MinterStoragePath = /storage/simpleNFTMinter
        
        // Create a Collection resource and save it to storage
        let collection <- create Collection()
        self.account.save(<-collection, to: self.CollectionStoragePath)
        
        // Create a public capability for the collection
        self.account.link<&SimpleNFT.Collection{NonFungibleToken.CollectionPublic, SimpleNFT.SimpleNFTCollectionPublic, MetadataViews.ResolverCollection}>(
            self.CollectionPublicPath,
            target: self.CollectionStoragePath
        )
        
        // Create a Minter resource and save it to storage
        let minter <- create NFTMinter()
        self.account.save(<-minter, to: self.MinterStoragePath)
        
        emit ContractInitialized()
    }
}