import DocumentRWA from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Interacting with contract DocumentRWA")
    }

    execute {
        log("Contract interaction completed")
    }
}