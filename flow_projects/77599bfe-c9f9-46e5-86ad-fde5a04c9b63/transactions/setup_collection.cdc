import NonFungibleToken from 0xNonFungibleToken
import TestNFTCollection from 0x01

transaction {
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {
        if signer.storage.borrow<&TestNFTCollection.Collection>(from: TestNFTCollection.CollectionStoragePath) == nil {
            let collection <- TestNFTCollection.createEmptyCollection(nftType: Type<@TestNFTCollection.NFT>())
            signer.storage.save(<-collection, to: TestNFTCollection.CollectionStoragePath)

            let collectionCap = signer.capabilities.storage.issue<&{NonFungibleToken.CollectionPublic}>(TestNFTCollection.CollectionStoragePath)
            signer.capabilities.publish(collectionCap, at: TestNFTCollection.CollectionPublicPath)
        }
    }
}