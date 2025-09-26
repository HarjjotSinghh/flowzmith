```cadence
// UserProfile.cdc

// Version: 1.0.0

import FungibleToken from 0xFungibleToken // Assuming FungibleToken is deployed at this address
import NonFungibleToken from 0xNonFungibleToken // Assuming NonFungibleToken is deployed at this address

// Event definitions
pub event ProfileCreated(userAddress: Address, profileID: UInt64)
pub event ProfileUpdated(userAddress: Address, profileID: UInt64)
pub event ProfileDeleted(userAddress: Address, profileID: UInt64)

// Resource interface for UserProfile
pub resource interface IUserProfile {
    pub fun getProfileID(): UInt64
    pub fun getUsername(): String
    pub fun getBio(): String
    pub fun updateUsername(newUsername: String)
    pub fun updateBio(newBio: String)
}

// UserProfile resource
pub resource UserProfile: IUserProfile {
    pub let profileID: UInt64
    pub var username: String
    pub var bio: String

    init(username: String, bio: String) {
        self.profileID = UserProfile.nextProfileID
        self.username = username
        self.bio = bio
        UserProfile.nextProfileID = UserProfile.nextProfileID + 1
        emit ProfileCreated(address: self.owner?.address!, profileID: self.profileID)
    }

    pub fun getProfileID(): UInt64 {
        return self.profileID
    }

    pub fun getUsername(): String {
        return self.username
    }

    pub fun getBio(): String {
        return self.bio
    }

    pub fun updateUsername(newUsername: String) {
        pre {
            newUsername.length > 0: "Username cannot be empty"
        }
        self.username = newUsername
        emit ProfileUpdated(userAddress: self.owner?.address!, profileID: self.profileID)
    }

    pub fun updateBio(newBio: String) {
        self.bio = newBio
        emit ProfileUpdated(userAddress: self.owner?.address!, profileID: self.profileID)
    }
}

// UserProfile collection resource
pub resource UserProfileCollection {
    pub let profiles: @{UInt64: UserProfile}

    init() {
        self.profiles <- {}
    }

    pub fun createProfile(username: String, bio: String) {
        let newProfile <- create UserProfile(username: username, bio: bio)
        let profileID = newProfile.getProfileID()
        self.profiles[profileID] <-! newProfile
    }

    pub fun getProfile(profileID: UInt64): &UserProfile? {
        return &self.profiles[profileID] as &UserProfile?
    }

    pub fun updateProfile(profileID: UInt64, newUsername: String?, newBio: String?) {
        if let profile = &self.profiles[profileID] {
            if let newUsername = newUsername {
                profile.updateUsername(newUsername: newUsername)
            }
            if let newBio = newBio {
                profile.updateBio(newBio: newBio)
            }
        } else {
            panic("Profile not found")
        }
    }

    pub fun deleteProfile(profileID: UInt64) {
        if let profile <- self.profiles.remove(key: profileID) {
            destroy profile
            emit ProfileDeleted(userAddress: self.owner?.address!, profileID: profileID)
        } else {
            panic("Profile not found")
        }
    }

    destroy() {
        destroy self.profiles
    }
}

// Contract definition
pub contract UserProfile {
    pub var nextProfileID: UInt64
    pub let profileCollectionStoragePath: StoragePath
    pub let profileCollectionPublicPath: PublicPath

    init() {
        self.nextProfileID = 0
        self.profileCollectionStoragePath = /storage/UserProfileCollection
        self.profileCollectionPublicPath = /public/UserProfileCollection
        self.account.save(<- create UserProfileCollection(), to: self.profileCollectionStoragePath)
        self.account.link<&UserProfileCollection>(UserProfileCollectionPublic, target: self.profileCollectionStoragePath, to: self.profileCollectionPublicPath)
    }

    // Public interface to access UserProfileCollection
    pub struct UserProfileCollectionPublic {
        pub let collection: Capability<&UserProfileCollection>

        init(collection: Capability<&UserProfileCollection>) {
            self.collection = collection
        }

        pub fun getProfile(profileID: UInt64): &UserProfile? {
            return self.collection.borrow()!.getProfile(profileID: profileID)
        }
    }

    // Function to create a new UserProfileCollection
    pub fun createUserProfileCollection(): @UserProfileCollection {
        return <- create UserProfileCollection()
    }

    // Transaction to create a new profile
    pub transaction(username: String, bio: String) {
        prepare(acct: AuthAccount) {
            if !acct.contains(self.profileCollectionStoragePath) {
                acct.save(<- create UserProfileCollection(), to: self.profileCollectionStoragePath)
                acct.link<&UserProfileCollection>(UserProfileCollectionPublic, target: self.profileCollectionStoragePath, to: self.profileCollectionPublicPath)
            }
            let collection = acct.borrow<&UserProfileCollection>(from: self.profileCollectionStoragePath)!
            collection.createProfile(username: username, bio: bio)
        }
    }

    // Transaction to update a profile
    pub transaction(profileID: UInt64, newUsername: String?, newBio: String?) {
        prepare(acct: AuthAccount) {
            let collection = acct.borrow<&UserProfileCollection>(from: self.profileCollectionStoragePath)!
            collection.updateProfile(profileID: profileID, newUsername: newUsername, newBio: newBio)
        }
    }

    // Transaction to delete a profile
    pub transaction(profileID: UInt64) {
        prepare(acct: AuthAccount) {
            let collection = acct.borrow<&UserProfileCollection>(from: self.profileCollectionStoragePath)!
            collection.deleteProfile(profileID: profileID)
        }
    }

    // Script to get a profile
    pub fun getProfile(userAddress: Address, profileID: UInt64): &UserProfile? {
        let publicAccount = getAccount(userAddress)
        let capability = publicAccount.getCapability<&UserProfileCollection>(self.profileCollectionPublicPath)
        if let collection = capability.borrow() {
            return collection.getProfile(profileID: profileID)
        } else {
            return nil
        }
    }
}
```