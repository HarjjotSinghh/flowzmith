import DocumentRWA from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract DocumentRWA deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}