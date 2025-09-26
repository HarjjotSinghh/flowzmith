import NonFungibleToken from 0xNonFungibleToken
import TestNFTCollection from 0x01

transaction(recipient: Address, name: String, description: String, thumbnail: String) {
    let minter: &TestNFTCollection.NFTMinter

    prepare(signer: auth(BorrowValue) &Account) {
        self.minter = signer.storage.borrow<&TestNFTCollection.NFTMinter>(
            from: TestNFTCollection.MinterStoragePath
        ) ?? panic("Could not borrow a reference to the NFT minter")
    }

    execute {
        let recipient = getAccount(recipient)
        let receiver = recipient
            .capabilities.borrow<&{NonFungibleToken.CollectionPublic}>(TestNFTCollection.CollectionPublicPath)
            ?? panic("Could not get receiver reference to the NFT Collection")

        self.minter.mintNFT(
            recipient: receiver,
            name: name,
            description: description,
            thumbnail: thumbnail
        )
    }
}