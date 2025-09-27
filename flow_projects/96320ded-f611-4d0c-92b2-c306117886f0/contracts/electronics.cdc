```cadence
// electronics.cdc

// Import required contracts
import "FungibleToken"
import "MetadataViews"

// Define the Electronics contract
pub contract Electronics {
    // Define the ElectronicsMetadata struct
    pub struct ElectronicsMetadata {
        pub let name: String
        pub let description: String
        pub let image: String

        init(name: String, description: String, image: String) {
            self.name = name
            self.description = description
            self.image = image
        }
    }

    // Define the ElectronicDevice resource
    pub resource ElectronicDevice {
        pub let id: UInt64
        pub let metadata: ElectronicsMetadata

        init(id: UInt64, metadata: ElectronicsMetadata) {
            self.id = id
            self.metadata = metadata
        }
    }

    // Define the ElectronicDeviceCollection resource
    pub resource ElectronicDeviceCollection {
        pub var devices: @{UInt64: ElectronicDevice}

        init() {
            self.devices <- {}
        }

        // Destroy the collection and its devices
        destroy() {
            destroy self.devices
        }

        // Add a device to the collection
        pub fun addDevice(device: ElectronicDevice) {
            self.devices[device.id] <-! device
        }

        // Remove a device from the collection
        pub fun removeDevice(id: UInt64): ElectronicDevice? {
            return <-self.devices.remove(key: id)
        }

        // Get a device from the collection
        pub fun getDevice(id: UInt64): ElectronicDevice? {
            return self.devices[id]
        }
    }

    // Define the ElectronicDeviceCollectionPublic interface
    pub resource interface ElectronicDeviceCollectionPublic {
        pub fun getDevice(id: UInt64): ElectronicDevice?
    }

    // Create a new ElectronicDevice
    pub fun createElectronicDevice(id: UInt64, metadata: ElectronicsMetadata): @ElectronicDevice {
        return <-create ElectronicDevice(id: id, metadata: metadata)
    }

    // Event emitted when a device is added to a collection
    pub event DeviceAdded(deviceId: UInt64, owner: Address)

    // Event emitted when a device is removed from a collection
    pub event DeviceRemoved(deviceId: UInt64, owner: Address)

    // Initialize the contract
    init() {
        // Create a new ElectronicDeviceCollection for the contract
        let collection <- create ElectronicDeviceCollection()
        self.account.save(<-collection, to: /storage/ElectronicDeviceCollection)

        // Create a public capability for the collection
        self.account.link<&{ElectronicDeviceCollectionPublic}>(/public/ElectronicDeviceCollection, target: /storage/ElectronicDeviceCollection)
    }
}

// Example transaction to add a device to a collection
transaction(deviceId: UInt64, metadata: Electronics.ElectronicsMetadata) {
    let collectionRef: &{Electronics.ElectronicDeviceCollectionPublic}

    prepare(acct: AuthAccount) {
        self.collectionRef = acct.borrow<&{Electronics.ElectronicDeviceCollectionPublic}>(from: /public/ElectronicDeviceCollection)
            ?? panic("Could not borrow a reference to the collection")
    }

    execute {
        let device <- Electronics.createElectronicDevice(id: deviceId, metadata: metadata)
        self.collectionRef.addDevice(device: <-device)
        emit Electronics.DeviceAdded(deviceId: deviceId, owner: acct.address)
    }
}

// Example script to get a device from a collection
pub fun getDevice(owner: Address, deviceId: UInt64): Electronics.ElectronicDevice? {
    let collectionRef = getAccount(owner).getCapability(/public/ElectronicDeviceCollection).borrow<&{Electronics.ElectronicDeviceCollectionPublic}>()
        ?? panic("Could not borrow a reference to the collection")
    return collectionRef.getDevice(id: deviceId)
}
```