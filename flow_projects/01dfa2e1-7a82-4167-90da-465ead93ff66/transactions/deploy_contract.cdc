import Organization from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract Organization deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}