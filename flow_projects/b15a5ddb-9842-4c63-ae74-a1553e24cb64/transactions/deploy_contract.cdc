import NewTest from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract NewTest deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}