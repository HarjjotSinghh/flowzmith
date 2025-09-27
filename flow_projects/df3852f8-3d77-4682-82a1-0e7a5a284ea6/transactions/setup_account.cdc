import FungibleToken from 0xFungibleToken
import AutoToken from 0x01

transaction {
    prepare(signer: auth(BorrowValue, IssueStorageCapabilityController, PublishCapability, SaveValue) &Account) {
        if signer.storage.borrow<&AutoToken.Vault>(from: AutoToken.VaultStoragePath) == nil {
            signer.storage.save(<-AutoToken.createEmptyVault(vaultType: Type<@AutoToken.Vault>()), to: AutoToken.VaultStoragePath)

            let receiverCap = signer.capabilities.storage.issue<&{FungibleToken.Receiver}>(AutoToken.VaultStoragePath)
            signer.capabilities.publish(receiverCap, at: AutoToken.ReceiverPublicPath)

            let balanceCap = signer.capabilities.storage.issue<&{FungibleToken.Balance}>(AutoToken.VaultStoragePath)
            signer.capabilities.publish(balanceCap, at: AutoToken.BalancePublicPath)
        }
    }
}