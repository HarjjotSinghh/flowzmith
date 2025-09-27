// Organization.cdc - Cadence 1.0 Compatible Version

access(all) contract Organization {

    // Events
    access(all) event OrganizationCreated(id: UInt64, name: String)
    access(all) event OrganizationUpdated(id: UInt64, name: String)
    access(all) event OrganizationDeleted(id: UInt64)

    // Resource Interface
    access(all) resource interface OrganizationInterface {
        access(all) let id: UInt64
        access(all) var name: String
        access(all) var description: String
        access(all) var website: String?

        access(all) fun update(name: String, description: String, website: String?)
    }

    // Resource
    access(all) resource OrganizationResource: OrganizationInterface {
        access(all) let id: UInt64
        access(all) var name: String
        access(all) var description: String
        access(all) var website: String?

        init(id: UInt64, name: String, description: String, website: String?) {
            self.id = id
            self.name = name
            self.description = description
            self.website = website
        }

        access(all) fun update(name: String, description: String, website: String?) {
            self.name = name
            self.description = description
            self.website = website
        }
    }

    // Storage Path
    access(all) let OrganizationStoragePath: StoragePath
    access(all) let OrganizationPublicPath: PublicPath

    // Mapping of organization ID to organization resource
    access(self) var organizations: @{UInt64: OrganizationResource}

    init() {
        self.OrganizationStoragePath = /storage/Organization
        self.OrganizationPublicPath = /public/Organization
        self.organizations <- {}

        // Save the organization collection to storage
        self.saveOrganizationCollection()
    }

    // Function to create a new organization
    access(all) fun createOrganization(id: UInt64, name: String, description: String, website: String?): @OrganizationResource {
        pre {
            !self.organizations.containsKey(id): "Organization with this ID already exists"
        }
        let organization <- create OrganizationResource(id: id, name: name, description: description, website: website)
        self.organizations[id] <-! organization
        emit OrganizationCreated(id: id, name: name)
        return <- self.organizations.remove(key: id)!
    }

    // Function to update an existing organization
    access(all) fun updateOrganization(id: UInt64, name: String, description: String, website: String?) {
        pre {
            self.organizations.containsKey(id): "Organization with this ID does not exist"
        }
        let organization = &self.organizations[id] as &OrganizationResource?
        organization?.update(name: name, description: description, website: website)
        emit OrganizationUpdated(id: id, name: name)
    }

    // Function to delete an organization
    access(all) fun deleteOrganization(id: UInt64) {
        pre {
            self.organizations.containsKey(id): "Organization with this ID does not exist"
        }
        let organization <- self.organizations.remove(key: id)!
        destroy organization
        emit OrganizationDeleted(id: id)
    }

    // Function to save the organization collection to storage
    access(all) fun saveOrganizationCollection() {
        let collection <- create OrganizationCollection()
        // Move organizations to the collection
        let orgs <- self.organizations <- {}
        collection.setOrganizations(<- orgs)
        self.account.storage.save(<- collection, to: self.OrganizationStoragePath)
        
        // Create capability
        let capability = self.account.capabilities.storage.issue<&{OrganizationCollectionPublic}>(self.OrganizationStoragePath)
        self.account.capabilities.publish(capability, at: self.OrganizationPublicPath)
    }

    // Public interface for Organization Collection
    access(all) resource interface OrganizationCollectionPublic {
        access(all) fun getOrganization(id: UInt64): &OrganizationResource? {
            post {
                result == nil || result?.id == id: "Returned organization ID does not match the requested ID"
            }
        }
    }

    // Organization Collection Resource
    access(all) resource OrganizationCollection: OrganizationCollectionPublic {
        access(self) var organizations: @{UInt64: OrganizationResource}

        init() {
            self.organizations <- {}
        }

        // Function to set organizations (used during initialization)
        access(contract) fun setOrganizations(_ organizations: @{UInt64: OrganizationResource}) {
            // Clean up any existing organizations first
            let oldOrganizations <- self.organizations <- organizations
            destroy oldOrganizations
        }

        // Function to clean up organizations (replaces custom destructor)
        access(all) fun cleanupOrganizations() {
            let oldOrganizations <- self.organizations <- {}
            destroy oldOrganizations
        }

        // Function to get an organization by ID
        access(all) fun getOrganization(id: UInt64): &OrganizationResource? {
            return &self.organizations[id] as &OrganizationResource?
        }

        // Function to borrow an organization by ID
        access(all) fun borrowOrganization(id: UInt64): &OrganizationResource? {
            return &self.organizations[id] as &OrganizationResource?
        }

        // Function to add an organization to the collection
        access(all) fun addOrganization(_ organization: @OrganizationResource) {
            let id = organization.id
            self.organizations[id] <-! organization
        }

        // Function to remove an organization from the collection
        access(all) fun removeOrganization(id: UInt64): @OrganizationResource? {
            return <- self.organizations.remove(key: id)
        }
    }
}