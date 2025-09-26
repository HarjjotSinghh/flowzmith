import NonFungibleToken from 0xNonFungibleToken
import TestNFTCollection from 0x01

access(all) fun main(account: Address): [UInt64] {
    let collection = getAccount(account)
        .capabilities.borrow<&{NonFungibleToken.CollectionPublic}>(TestNFTCollection.CollectionPublicPath)
        ?? panic("Could not borrow a reference to the collection")

    return collection.getIDs()
}