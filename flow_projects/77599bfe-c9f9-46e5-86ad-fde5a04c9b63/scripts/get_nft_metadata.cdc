import NonFungibleToken from 0xNonFungibleToken
import TestNFTCollection from 0x01

access(all) fun main(account: Address, itemID: UInt64): {String: String} {
    let collection = getAccount(account)
        .capabilities.borrow<&{NonFungibleToken.CollectionPublic}>(TestNFTCollection.CollectionPublicPath)
        ?? panic("Could not borrow a reference to the collection")

    let nft = collection.borrowNFT(itemID)
    return nft.getMetadata()
}