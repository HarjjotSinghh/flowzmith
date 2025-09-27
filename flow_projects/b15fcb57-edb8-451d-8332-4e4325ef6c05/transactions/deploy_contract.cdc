import WalletManager2 from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract WalletManager2 deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}