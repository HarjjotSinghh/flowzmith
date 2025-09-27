import Test
import NewTest from "../contracts/NewTest.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "NewTest",
        path: "../contracts/NewTest.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}