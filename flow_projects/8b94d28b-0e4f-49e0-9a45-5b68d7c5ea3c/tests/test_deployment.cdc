import Test
import TestNew from "../contracts/TestNew.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "TestNew",
        path: "../contracts/TestNew.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}