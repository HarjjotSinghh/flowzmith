
        import NonFungibleToken from 0x1d7e57aa55817448
        import MetadataViews from 0x1d7e57aa55817448

        pub contract TestNFTCollection: NonFungibleToken {
            pub var totalSupply: UInt64
            
            pub event ContractInitialized()
            pub event Withdraw(id: UInt64, from: Address?)
            pub event Deposit(id: UInt64, to: Address?)
            
            pub let CollectionStoragePath: StoragePath
            pub let CollectionPublicPath: PublicPath
            
            pub resource NFT: NonFungibleToken.INFT, MetadataViews.Resolver {
                pub let id: UInt64
                pub let name: String
                pub let description: String
                
                init(id: UInt64, name: String, description: String) {
                    self.id = id
                    self.name = name
                    self.description = description
                }
                
                pub fun getViews(): [Type] {
                    return [Type<MetadataViews.Display>()]
                }
                
                pub fun resolveView(_ view: Type): AnyStruct? {
                    switch view {
                        case Type<MetadataViews.Display>():
                            return MetadataViews.Display(
                                name: self.name,
                                description: self.description,
                                thumbnail: MetadataViews.HTTPFile(url: "")
                            )
                    }
                    return nil
                }
            }
            
            pub resource Collection: NonFungibleToken.Provider, NonFungibleToken.Receiver, NonFungibleToken.CollectionPublic, MetadataViews.ResolverCollection {
                pub var ownedNFTs: @{UInt64: NonFungibleToken.NFT}
                
                init() {
                    self.ownedNFTs <- {}
                }
                
                pub fun withdraw(withdrawID: UInt64): @NonFungibleToken.NFT {
                    let token <- self.ownedNFTs.remove(key: withdrawID) ?? panic("missing NFT")
                    emit Withdraw(id: token.id, from: self.owner?.address)
                    return <-token
                }
                
                pub fun deposit(token: @NonFungibleToken.NFT) {
                    let token <- token as! @TestNFTCollection.NFT
                    let id: UInt64 = token.id
                    let oldToken <- self.ownedNFTs[id] <- token
                    emit Deposit(id: id, to: self.owner?.address)
                    destroy oldToken
                }
                
                pub fun getIDs(): [UInt64] {
                    return self.ownedNFTs.keys
                }
                
                pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT {
                    return (&self.ownedNFTs[id] as &NonFungibleToken.NFT?)!
                }
                
                pub fun borrowViewResolver(id: UInt64): &AnyResource{MetadataViews.Resolver} {
                    let nft = (&self.ownedNFTs[id] as auth &NonFungibleToken.NFT?)!
                    let testNFT = nft as! &TestNFTCollection.NFT
                    return testNFT as &AnyResource{MetadataViews.Resolver}
                }
                
                destroy() {
                    destroy self.ownedNFTs
                }
            }
            
            pub fun createEmptyCollection(): @NonFungibleToken.Collection {
                return <- create Collection()
            }
            
            pub fun mintNFT(recipient: &{NonFungibleToken.CollectionPublic}, name: String, description: String) {
                let newNFT <- create NFT(id: TestNFTCollection.totalSupply, name: name, description: description)
                recipient.deposit(token: <-newNFT)
                TestNFTCollection.totalSupply = TestNFTCollection.totalSupply + 1
            }
            
            init() {
                self.totalSupply = 0
                self.CollectionStoragePath = /storage/TestNFTCollection
                self.CollectionPublicPath = /public/TestNFTCollection
                
                let collection <- create Collection()
                self.account.save(<-collection, to: self.CollectionStoragePath)
                self.account.link<&TestNFTCollection.Collection{NonFungibleToken.CollectionPublic, MetadataViews.ResolverCollection}>(
                    self.CollectionPublicPath,
                    target: self.CollectionStoragePath
                )
                
                emit ContractInitialized()
            }
        }
        