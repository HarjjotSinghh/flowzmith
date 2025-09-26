```cadence
// UserProfile.cdc

// Version: 1.0.0

import FungibleToken from 0xFungibleToken // Assuming FungibleToken is deployed at 0xFungibleToken

pub contract UserProfile {
    // Events
    pub event ProfileCreated(user: Address, profileID: UInt64)
    pub event ProfileUpdated(user: Address, profileID: UInt64)
    pub event ProfileDeleted(user: Address, profileID: UInt64)

    // Resource Interface
    pub resource interface IUserProfile {
        pub fun getProfileID(): UInt64
        pub fun getUsername(): String
        pub fun getBio(): String
        pub fun updateUsername(newUsername: String)
        pub fun updateBio(newBio: String)
    }

    // Resource
    pub resource UserProfile: IUserProfile {
        pub let profileID: UInt64
        pub var username: String
        pub var bio: String

        init(username: String, bio: String) {
            self.profileID = UserProfile.nextProfileID
            self.username = username
            self.bio = bio
            UserProfile.nextProfileID = UserProfile.nextProfileID + 1
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
            self.username = newUsername
        }

        pub fun updateBio(newBio: String) {
            self.bio = newBio
        }
    }

    // Collection Resource Interface
    pub resource interface IUserProfileCollection {
        pub fun createProfile(username: String, bio: String)
        pub fun updateProfile(profileID: UInt64, newUsername: String?, newBio: String?)
        pub fun deleteProfile(profileID: UInt64)
        pub fun getProfile(profileID: UInt64): &UserProfile? 
    }

    // Collection Resource
    pub resource UserProfileCollection: IUserProfileCollection {
        pub let profiles: @{UInt64: UserProfile}

        init() {
            self.profiles <- {}
        }

        pub fun createProfile(username: String, bio: String) {
            let newProfile <- create UserProfile(username: username, bio: bio)
            let profileID = newProfile.getProfileID()
            self.profiles[profileID] <-! newProfile
            emit ProfileCreated(user: self.owner?.address!, profileID: profileID)
        }

        pub fun updateProfile(profileID: UInt64, newUsername: String?, newBio: String?) {
            pre {
                self.profiles[profileID] != nil: "Profile not found"
            }
            let profile = &self.profiles[profileID] as &UserProfile
            if let newUsername = newUsername {
                profile.updateUsername(newUsername: newUsername)
            }
            if let newBio = newBio {
                profile.updateBio(newBio: newBio)
            }
            emit ProfileUpdated(user: self.owner?.address!, profileID: profileID)
        }

        pub fun deleteProfile(profileID: UInt64) {
            pre {
                self.profiles[profileID] != nil: "Profile not found"
            }
            let profile <- self.profiles.remove(key: profileID)!
            destroy profile
            emit ProfileDeleted(user: self.owner?.address!, profileID: profileID)
        }

        pub fun getProfile(profileID: UInt64): &UserProfile? {
            if let profile = self.profiles[profileID] {
                return &profile as &UserProfile
            } else {
                return nil
            }
        }

        destroy() {
            destroy self.profiles
        }
    }

    // Public Functions
    pub fun createUserProfileCollection(): @UserProfileCollection {
        return <- create UserProfileCollection()
    }

    // Storage Paths
    pub let UserProfileCollectionStoragePath: StoragePath
    pub let UserProfileCollectionPublicPath: PublicPath

    // State Variables
    pub var nextProfileID: UInt64

    init() {
        self.nextProfileID = 0
        self.UserProfileCollectionStoragePath = /storage/UserProfileCollection
        self.UserProfileCollectionPublicPath = /public/UserProfileCollection
        self.account.save(<- create UserProfileCollection(), to: self.UserProfileCollectionStoragePath)
        self.account.link<&UserProfileCollection{IUserProfileCollection}>(
            self.UserProfileCollectionPublicPath,
            target: self.UserProfileCollectionStoragePath
        )
    }
}

// Example Transaction: Create Profile
transaction(username: String, bio: String) {
    let userProfileCollection: &UserProfile.UserProfileCollection{IUserProfileCollection}

    prepare(acct: AuthAccount) {
        self.userProfileCollection = acct.borrow<&UserProfile.UserProfileCollection{IUserProfileCollection}>(
            from: UserProfile.UserProfileCollectionStoragePath
        )!
    }

    execute {
        self.userProfileCollection.createProfile(username: username, bio: bio)
    }
}

// Example Script: Get Profile
pub fun main(address: Address, profileID: UInt64): String? {
    let userProfileCollection = getAccount(address).getCapability(UserProfile.UserProfileCollectionPublicPath)
        .borrow<&UserProfile.UserProfileCollection{IUserProfileCollection}>()
        ?? panic("Could not borrow UserProfileCollection")
    let profile = userProfileCollection.getProfile(profileID: profileID)
    if let profile = profile {
        return "Username: ".concat(profile.getUsername()).concat(", Bio: ").concat(profile.getBio())
    } else {
        return nil
    }
}
```