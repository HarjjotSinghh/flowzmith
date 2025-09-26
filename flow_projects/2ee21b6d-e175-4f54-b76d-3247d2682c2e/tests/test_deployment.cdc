import Test
import Test2 from "../contracts/Test2.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "Test2",
        path: "../contracts/Test2.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}