```cadence
// SoftwareTest.cdc

// Import required contracts
import "FlowToken"

// Define the SoftwareTest contract
pub contract SoftwareTest {

    // Define events
    pub event TestCreated(testID: UInt64, testName: String)
    pub event TestUpdated(testID: UInt64, testName: String)
    pub event TestDeleted(testID: UInt64)

    // Define the Test resource interface
    pub resource interface ITest {
        pub let testID: UInt64
        pub var testName: String
        pub var testStatus: Bool

        pub fun updateTestName(newName: String)
        pub fun updateTestStatus(newStatus: Bool)
    }

    // Define the Test resource
    pub resource Test: ITest {
        pub let testID: UInt64
        pub var testName: String
        pub var testStatus: Bool

        init(testID: UInt64, testName: String) {
            self.testID = testID
            self.testName = testName
            self.testStatus = false
        }

        pub fun updateTestName(newName: String) {
            self.testName = newName
            emit TestUpdated(testID: self.testID, testName: newName)
        }

        pub fun updateTestStatus(newStatus: Bool) {
            self.testStatus = newStatus
        }
    }

    // Define a collection to store tests
    pub resource TestCollection {
        pub let owner: Address
        pub var tests: @{UInt64: Test}

        init(owner: Address) {
            self.owner = owner
            self.tests <- {}
        }

        // Function to add a new test
        pub fun addTest(test: Test) {
            let testID = test.testID
            pre {
                self.tests[testID] == nil: "Test with this ID already exists"
            }
            self.tests[testID] <-! test
            emit TestCreated(testID: testID, testName: test.testName)
        }

        // Function to remove a test
        pub fun removeTest(testID: UInt64): Test? {
            pre {
                self.tests[testID] != nil: "Test with this ID does not exist"
            }
            let test <- self.tests.remove(key: testID)!
            emit TestDeleted(testID: testID)
            return <-test
        }

        // Function to get a test
        pub fun getTest(testID: UInt64): &Test? {
            return &self.tests[testID] as &Test?
        }

        // Function to update a test name
        pub fun updateTestName(testID: UInt64, newName: String) {
            pre {
                self.tests[testID] != nil: "Test with this ID does not exist"
            }
            self.tests[testID]?.updateTestName(newName: newName)
        }

        // Function to update a test status
        pub fun updateTestStatus(testID: UInt64, newStatus: Bool) {
            pre {
                self.tests[testID] != nil: "Test with this ID does not exist"
            }
            self.tests[testID]?.updateTestStatus(newStatus: newStatus)
        }

        // Destructor to clean up resources
        destroy() {
            destroy self.tests
        }
    }

    // Function to create a new test collection
    pub fun createTestCollection(): @TestCollection {
        return <-create TestCollection(owner: self.account.address)
    }

    // Initialize the contract
    init() {
        // No initialization needed for this contract
    }
}

// Example transaction to create a new test collection
// transaction {
//     prepare(signer: AuthAccount) {
//         let collection <- SoftwareTest.createTestCollection()
//         signer.save(<-collection, to: /storage/TestCollection)
//         let cap = signer.link<&SoftwareTest.TestCollection>(/public/TestCollection, target: /storage/TestCollection)
//         log(cap)
//     }
// }

// Example transaction to add a new test
// transaction(testName: String) {
//     prepare(signer: AuthAccount) {
//         let collectionRef = signer.borrow<&SoftwareTest.TestCollection>(from: /storage/TestCollection)
//             ?? panic("Could not borrow reference to TestCollection")
//         let test <- create SoftwareTest.Test(testID: 1, testName: testName)
//         collectionRef.addTest(test: <-test)
//     }
// }

// Example script to get a test
// pub fun main(testID: UInt64, address: Address): String? {
//     let publicAccount = getAccount(address)
//     let capability = publicAccount.getCapability<&SoftwareTest.TestCollection>(/public/TestCollection)
//     let collectionRef = capability.borrow()
//         ?? panic("Could not borrow reference to TestCollection")
//     let testRef = collectionRef.getTest(testID: testID)
//     return testRef?.testName
// }
```