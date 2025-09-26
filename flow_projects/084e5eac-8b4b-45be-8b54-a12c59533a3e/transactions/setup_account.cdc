import FungibleToken from 0xFungibleToken
import APITestToken from 0x01

transaction {
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {
        if signer.storage.borrow<&APITestToken.Vault>(from: APITestToken.VaultStoragePath) == nil {
            signer.storage.save(<-APITestToken.createEmptyVault(vaultType: Type<@APITestToken.Vault>()), to: APITestToken.VaultStoragePath)

            let receiverCap = signer.capabilities.storage.issue<&{FungibleToken.Receiver}>(APITestToken.VaultStoragePath)
            signer.capabilities.publish(receiverCap, at: APITestToken.ReceiverPublicPath)

            let balanceCap = signer.capabilities.storage.issue<&{FungibleToken.Balance}>(APITestToken.VaultStoragePath)
            signer.capabilities.publish(balanceCap, at: APITestToken.BalancePublicPath)
        }
    }
}