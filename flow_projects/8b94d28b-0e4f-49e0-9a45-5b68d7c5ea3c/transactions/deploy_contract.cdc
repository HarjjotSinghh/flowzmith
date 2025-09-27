import TestNew from 0x01

transaction() {
    prepare(signer: auth(BorrowValue) &Account) {
        log("Contract TestNew deployed successfully")
    }

    execute {
        log("Executing deployment transaction")
    }
}