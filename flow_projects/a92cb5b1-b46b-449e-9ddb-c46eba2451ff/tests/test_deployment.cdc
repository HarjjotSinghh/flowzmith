import Test
import Organzation2 from "../contracts/Organzation2.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "Organzation2",
        path: "../contracts/Organzation2.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}