import Test
import UserProfile from "../contracts/UserProfile.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "UserProfile",
        path: "../contracts/UserProfile.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}