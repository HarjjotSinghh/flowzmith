```cadence
// Organization.cdc

pub contract Organization {

    // Events
    pub event OrganizationCreated(id: UInt64, name: String)
    pub event OrganizationUpdated(id: UInt64, name: String)
    pub event OrganizationDeleted(id: UInt64)

    // Resource Interface
    pub resource interface OrganizationInterface {
        pub let id: UInt64
        pub var name: String
        pub var description: String
        pub var website: String?

        pub fun update(name: String, description: String, website: String?)
    }

    // Resource
    pub resource OrganizationResource: OrganizationInterface {
        pub let id: UInt64
        pub var name: String
        pub var description: String
        pub var website: String?

        init(id: UInt64, name: String, description: String, website: String?) {
            self.id = id
            self.name = name
            self.description = description
            self.website = website
        }

        pub fun update(name: String, description: String, website: String?) {
            self.name = name
            self.description = description
            self.website = website
        }
    }

    // Storage Path
    pub let OrganizationStoragePath: StoragePath
    pub let OrganizationPublicPath: PublicPath

    // Mapping of organization ID to organization resource
    pub var organizations: @{UInt64: OrganizationResource}

    init() {
        self.OrganizationStoragePath = /storage/Organization
        self.OrganizationPublicPath = /public/Organization
        self.organizations <- {}

        // Save the organization collection to storage
        self.saveOrganizationCollection()
    }

    // Function to create a new organization
    pub fun createOrganization(id: UInt64, name: String, description: String, website: String?): @OrganizationResource {
        pre {
            !self.organizations.containsKey(id): "Organization with this ID already exists"
        }
        let organization <- create OrganizationResource(id: id, name: name, description: description, website: website)
        self.organizations[id] <-! organization
        emit OrganizationCreated(id: id, name: name)
        return <- self.organizations.remove(key: id)!
    }

    // Function to update an existing organization
    pub fun updateOrganization(id: UInt64, name: String, description: String, website: String?) {
        pre {
            self.organizations.containsKey(id): "Organization with this ID does not exist"
        }
        let organization = self.organizations[id]!
        organization.update(name: name, description: description, website: website)
        emit OrganizationUpdated(id: id, name: name)
    }

    // Function to delete an organization
    pub fun deleteOrganization(id: UInt64) {
        pre {
            self.organizations.containsKey(id): "Organization with this ID does not exist"
        }
        let organization <- self.organizations.remove(key: id)!
        destroy organization
        emit OrganizationDeleted(id: id)
    }

    // Function to save the organization collection to storage
    pub fun saveOrganizationCollection() {
        let collection <- create OrganizationCollection()
        collection.organizations <- self.organizations <- {}
        self.account.save(<- collection, to: self.OrganizationStoragePath)
        self.account.link<&{OrganizationCollectionPublic}>(self.OrganizationPublicPath, target: self.OrganizationStoragePath)
    }

    // Public interface for Organization Collection
    pub struct interface OrganizationCollectionPublic {
        pub fun getOrganization(id: UInt64): &OrganizationResource? {
            post {
                result == nil || result?.id == id: "Returned organization ID does not match the requested ID"
            }
        }
    }

    // Organization Collection Resource
    pub resource OrganizationCollection: OrganizationCollectionPublic {
        pub var organizations: @{UInt64: OrganizationResource}

        init() {
            self.organizations <- {}
        }

        // Function to get an organization by ID
        pub fun getOrganization(id: UInt64): &OrganizationResource? {
            return &self.organizations[id] as &OrganizationResource?
        }

        // Function to borrow an organization by ID
        pub fun borrowOrganization(id: UInt64): &OrganizationResource? {
            return &self.organizations[id] as &OrganizationResource?
        }

        // Function to add an organization to the collection
        pub fun addOrganization(_ organization: @OrganizationResource) {
            let id = organization.id
            self.organizations[id] <-! organization
        }

        // Function to remove an organization from the collection
        pub fun removeOrganization(id: UInt64): @OrganizationResource? {
            return <- self.organizations.remove(key: id)
        }

        destroy() {
            destroy self.organizations
        }
    }
}

// Example transaction to create a new organization
transaction(id: UInt64, name: String, description: String, website: String?) {
    prepare(acct: &Account) {
        let organization <- Organization.createOrganization(id: id, name: name, description: description, website: website)
        acct.save(<- organization, to: /storage/Organization)
    }
}

// Example script to get an organization by ID
pub fun main(id: UInt64): &Organization.OrganizationResource? {
    let collection = getAccount(0x01).getCapability(Organization.OrganizationPublicPath).borrow<&{Organization.OrganizationCollectionPublic}>()
    return collection?.getOrganization(id: id)
}
```