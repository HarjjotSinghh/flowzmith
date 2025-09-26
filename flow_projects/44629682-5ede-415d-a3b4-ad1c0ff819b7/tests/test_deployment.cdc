import Test
import Contract from "../contracts/Contract.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "Contract",
        path: "../contracts/Contract.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}