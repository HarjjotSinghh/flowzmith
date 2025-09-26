```cadence
// Organization2.cdc

// Import required contracts
import FungibleToken from 0x9a0766d93b6608b7
import NonFungibleToken from 0x631e88ae7f3c7c27

// Define the Organization struct
pub struct Organization {
    pub let id: UInt64
    pub let name: String
    pub let description: String
    pub let owner: Address

    init(id: UInt64, name: String, description: String, owner: Address) {
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner
    }
}

// Define the OrganizationManager resource
pub resource OrganizationManager {
    // Mapping of organization IDs to Organization structs
    pub var organizations: @{UInt64: Organization}

    // Event emitted when a new organization is created
    pub event OrganizationCreated(id: UInt64, name: String, owner: Address)

    // Event emitted when an organization is updated
    pub event OrganizationUpdated(id: UInt64, name: String)

    init() {
        self.organizations <- {}
    }

    // Function to create a new organization
    pub fun createOrganization(id: UInt64, name: String, description: String) {
        pre {
            self.organizations[id] == nil: "Organization with this ID already exists"
        }
        let newOrganization = Organization(id: id, name: name, description: description, owner: self.owner)
        self.organizations[id] <- newOrganization
        emit OrganizationCreated(id: id, name: name, owner: self.owner)
    }

    // Function to update an existing organization
    pub fun updateOrganization(id: UInt64, name: String) {
        pre {
            self.organizations[id] != nil: "Organization with this ID does not exist"
        }
        let organization <- self.organizations.remove(key: id)!
        let updatedOrganization = Organization(id: id, name: name, description: organization.description, owner: organization.owner)
        self.organizations[id] <- updatedOrganization
        emit OrganizationUpdated(id: id, name: name)
    }

    // Function to get an organization's details
    pub fun getOrganization(id: UInt64): Organization? {
        return self.organizations[id]
    }

    // Function to destroy an organization
    pub fun destroyOrganization(id: UInt64) {
        pre {
            self.organizations[id] != nil: "Organization with this ID does not exist"
        }
        let organization <- self.organizations.remove(key: id)!
        destroy organization
    }

    destroy() {
        destroy self.organizations
    }
}

// Define the OrganizationManager capability
pub fun createOrganizationManager(): @OrganizationManager {
    return <- create OrganizationManager()
}

// Public function to create a new organization
pub fun createNewOrganization(id: UInt64, name: String, description: String, authAccount: AuthAccount) {
    let organizationManager <- authAccount.load<@OrganizationManager>(from: /storage/OrganizationManager)
    if organizationManager == nil {
        organizationManager <- create OrganizationManager()
        authAccount.save(<-organizationManager, to: /storage/OrganizationManager)
    }
    organizationManager!.createOrganization(id: id, name: name, description: description)
    authAccount.save(<-organizationManager, to: /storage/OrganizationManager)
}

// Public function to update an existing organization
pub fun updateExistingOrganization(id: UInt64, name: String, authAccount: AuthAccount) {
    let organizationManager = authAccount.borrow<&OrganizationManager>(from: /storage/OrganizationManager)
    ?? panic("OrganizationManager not found in storage")
    organizationManager.updateOrganization(id: id, name: name)
}

// Public function to get an organization's details
pub fun getOrganizationDetails(id: UInt64, authAccount: AuthAccount): Organization? {
    let organizationManager = authAccount.borrow<&OrganizationManager>(from: /storage/OrganizationManager)
    ?? panic("OrganizationManager not found in storage")
    return organizationManager.getOrganization(id: id)
}

// Public function to destroy an organization
pub fun destroyExistingOrganization(id: UInt64, authAccount: AuthAccount) {
    let organizationManager <- authAccount.load<@OrganizationManager>(from: /storage/OrganizationManager)
    ?? panic("OrganizationManager not found in storage")
    organizationManager.destroyOrganization(id: id)
    authAccount.save(<-organizationManager, to: /storage/OrganizationManager)
}

// Example transaction to create a new organization
transaction {
    prepare(authAccount: AuthAccount) {
        createNewOrganization(id: 1, name: "Test Organization", description: "This is a test organization", authAccount: authAccount)
    }
}

// Example script to get an organization's details
pub fun main(account: Address): Organization? {
    let publicAccount = getAccount(account)
    let organizationManager = publicAccount.getCapability(/public/OrganizationManager).borrow<&OrganizationManager>()
    ?? panic("OrganizationManager not found in storage")
    return organizationManager.getOrganization(id: 1)
}
```