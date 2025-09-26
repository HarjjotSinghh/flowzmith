import Test
import TestNFTCollection from "../contracts/TestNFTCollection.cdc"

access(all) fun testContractDeployment() {
    let account = Test.createAccount()
    let err = Test.deployContract(
        name: "TestNFTCollection",
        path: "../contracts/TestNFTCollection.cdc",
        arguments: []
    )
    Test.expect(err, Test.beNil())
}

access(all) fun testInitialSupply() {
    let supply = TestNFTCollection.totalSupply
    Test.expect(supply, Test.equal(0 as UInt64))
}