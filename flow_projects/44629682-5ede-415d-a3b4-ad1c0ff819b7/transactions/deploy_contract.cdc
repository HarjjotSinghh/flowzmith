import Contract from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract Contract deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}