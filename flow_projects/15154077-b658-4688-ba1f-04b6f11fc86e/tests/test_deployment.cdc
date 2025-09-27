import Test
import electronics from "../contracts/electronics.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "electronics",
        path: "../contracts/electronics.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}