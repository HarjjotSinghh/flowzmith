// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

/**
 * @title UserProfile
 * @dev Manages user profiles for sv3.network
 * Handles user identity, verification, and profile data
 */
contract UserProfile {
    struct Profile {
        address wallet;              // Primary key - user's wallet address
        string username;             // Unique username for display
        string email;                // Optional email for notifications
        string linkedinProfile;       // Optional LinkedIn profile
        bool verified;               // Verification status
        uint256 createdAt;          // Timestamp when profile was created
        mapping(string => string) customData; // Additional profile data
    }

    mapping(address => Profile) public profiles;
    mapping(string => address) public usernameToAddress;

    uint256 public profileCount;

    event ProfileCreated(address indexed wallet, string username);
    event ProfileUpdated(address indexed wallet, string field, string value);
    event ProfileVerified(address indexed wallet);

    error UsernameTaken();
    error ProfileNotFound();
    error Unauthorized();
    error InvalidUsername();
    error InvalidAddress();

    modifier onlyProfileOwner(address wallet) {
        require(profiles[wallet].wallet != address(0), "Profile does not exist");
        require(msg.sender == wallet, "Unauthorized");
        _;
    }

    /**
     * @dev Create a new user profile
     * @param username Display name for the user
     * @param email Optional email address
     */
    function createProfile(string memory username, string memory email) external {
        require(profiles[msg.sender].wallet == address(0), "Profile already exists");
        require(bytes(username).length >= 3 && bytes(username).length <= 30, "Username must be 3-30 characters");
        require(usernameToAddress[username] == address(0), "Username already taken");

        // Check username contains only alphanumeric characters and underscores
        _validateUsername(username);

        Profile storage profile = profiles[msg.sender];
        profile.wallet = msg.sender;
        profile.username = username;
        profile.email = email;
        profile.verified = false;
        profile.createdAt = block.timestamp;

        usernameToAddress[username] = msg.sender;
        profileCount++;

        emit ProfileCreated(msg.sender, username);
    }

    /**
     * @dev Update a profile field
     * @param field Field name to update
     * @param value New value for the field
     */
    function updateProfile(string memory field, string memory value) external onlyProfileOwner(msg.sender) {
        Profile storage profile = profiles[msg.sender];

        if (keccak256(bytes(field)) == keccak256(bytes("username"))) {
            require(usernameToAddress[value] == address(0), "Username already taken");
            require(bytes(value).length >= 3 && bytes(value).length <= 30, "Username must be 3-30 characters");
            _validateUsername(value);

            // Remove old username mapping
            delete usernameToAddress[profile.username];
            profile.username = value;
            usernameToAddress[value] = msg.sender;
        } else if (keccak256(bytes(field)) == keccak256(bytes("email"))) {
            profile.email = value;
        } else if (keccak256(bytes(field)) == keccak256(bytes("linkedinProfile"))) {
            profile.linkedinProfile = value;
        } else {
            // Custom field
            profile.customData[field] = value;
        }

        emit ProfileUpdated(msg.sender, field, value);
    }

    /**
     * @dev Verify a user profile (can be called by authorized verifier)
     */
    function verifyProfile() external onlyProfileOwner(msg.sender) {
        require(!profiles[msg.sender].verified, "Profile already verified");
        profiles[msg.sender].verified = true;
        emit ProfileVerified(msg.sender);
    }

    // Updated getProfile (Solution 1)
function getProfile(address wallet)
    external
    view
    returns (
        address walletAddress,
        string memory username,
        string memory email,
        string memory linkedinProfile,
        bool verified,
        uint256 createdAt
    )
{
    Profile storage profile = profiles[wallet];
    require(profile.wallet != address(0), "Profile not found");

    return (
        profile.wallet,
        profile.username,
        profile.email,
        profile.linkedinProfile,
        profile.verified,
        profile.createdAt
    );
}



    /**
     * @dev Get profile by username
     */
// Also update getProfileByUsername similarly
function getProfileByUsername(string memory username)
    external
    view
    returns (
        address walletAddress,
        string memory email,
        string memory linkedinProfile,
        bool verified,
        uint256 createdAt
    )
{
    address wallet = usernameToAddress[username];
    require(wallet != address(0), "Username not found");

    Profile storage profile = profiles[wallet];
    return (
        profile.wallet,
        profile.email,
        profile.linkedinProfile,
        profile.verified,
        profile.createdAt
    );
}

    /**
     * @dev Check if username is available
     */
    function isUsernameAvailable(string memory username) external view returns (bool) {
        return usernameToAddress[username] == address(0);
    }

    /**
     * @dev Internal function to validate username format
     */
    function _validateUsername(string memory username) internal pure {
        bytes memory usernameBytes = bytes(username);
        for (uint i = 0; i < usernameBytes.length; i++) {
            bytes1 char = usernameBytes[i];
            require(
                (char >= 0x30 && char <= 0x39) || // 0-9
                (char >= 0x41 && char <= 0x5A) || // A-Z
                (char >= 0x61 && char <= 0x7A) || // a-z
                char == 0x5F, // _
                "Invalid username character"
            );
        }
    }

    /**
     * @dev Get custom data field
     */
    function getCustomData(address wallet, string memory field)
    external
    view
        returns (string memory)
    {
        require(profiles[wallet].wallet != address(0), "Profile not found");
        return profiles[wallet].customData[field];
    }

}