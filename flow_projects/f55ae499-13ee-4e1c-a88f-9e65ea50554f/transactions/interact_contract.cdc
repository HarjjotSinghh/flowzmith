import WalletManager from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract WalletManager")
    }

    execute {
        log("Contract interaction completed")
    }
}