import UserProfile from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract UserProfile deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}