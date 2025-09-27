import WalletManager from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract WalletManager deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}