import NonFungibleToken from 0xNonFungibleToken
import TestNFTCollection from 0x01

transaction(recipient: Address, withdrawID: UInt64) {
    let withdrawRef: auth(NonFungibleToken.Withdraw) &TestNFTCollection.Collection

    prepare(signer: auth(BorrowValue) &Account) {
        self.withdrawRef = signer.storage.borrow<auth(NonFungibleToken.Withdraw) &TestNFTCollection.Collection>(
            from: TestNFTCollection.CollectionStoragePath
        ) ?? panic("Could not borrow a reference to the owner's collection")
    }

    execute {
        let recipient = getAccount(recipient)
        let depositRef = recipient
            .capabilities.borrow<&{NonFungibleToken.CollectionPublic}>(TestNFTCollection.CollectionPublicPath)
            ?? panic("Could not borrow a reference to the recipient's collection")

        let nft <- self.withdrawRef.withdraw(withdrawID: withdrawID)
        depositRef.deposit(token: <-nft)
    }
}