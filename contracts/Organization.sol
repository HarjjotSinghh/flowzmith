// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

/**
 * @title Organization
 * @dev Manages organizations for sv3.network
 * Handles team structures, member management, and role-based access control
 */
contract Organization {
    struct Org {
        uint256 id;                    // Unique organization ID
        address owner;                // Creator/owner wallet address
        string name;                  // Organization display name
        string description;           // Organization description
        address[] members;             // List of member addresses
        mapping(address => uint256) memberRoles; // Role mapping (0=owner, 1=admin, 2=member)
        uint256 createdAt;            // Creation timestamp
        bool isActive;                // Organization status
    }

    mapping(uint256 => Org) public organizations;
    mapping(address => uint256[]) public userOrganizations;

    uint256 public organizationCount;

    event OrganizationCreated(uint256 indexed orgId, address indexed owner, string name);
    event OrganizationUpdated(uint256 indexed orgId, string field, string value);
    event MemberAdded(uint256 indexed orgId, address indexed member, uint256 role);
    event MemberRemoved(uint256 indexed orgId, address indexed member);
    event MemberRoleChanged(uint256 indexed orgId, address indexed member, uint256 newRole);
    event OrganizationDeleted(uint256 indexed orgId);

    error OrganizationNotFound();
    error Unauthorized();
    error InvalidOrganizationName();
    error InvalidRole();
    error AlreadyMember();
    error NotMember();
    error OnlyOwner();

    // Role definitions
    uint256 public constant ROLE_OWNER = 0;
    uint256 public constant ROLE_ADMIN = 1;
    uint256 public constant ROLE_MEMBER = 2;

    modifier onlyOrgOwner(uint256 orgId) {
        require(organizations[orgId].owner == msg.sender, "Only owner");
        _;
    }

    modifier onlyOrgAdmin(uint256 orgId) {
        require(organizations[orgId].memberRoles[msg.sender] <= ROLE_ADMIN, "Only admin or owner");
        _;
    }

    modifier onlyOrgMember(uint256 orgId) {
        require(organizations[orgId].memberRoles[msg.sender] <= ROLE_MEMBER, "Only member");
        _;
    }

    modifier orgExists(uint256 orgId) {
        require(organizations[orgId].id != 0, "Organization not found");
        _;
    }

    /**
     * @dev Create a new organization
     * @param name Organization display name
     * @param description Organization description
     */
    function createOrganization(string memory name, string memory description) external {
        require(bytes(name).length >= 3 && bytes(name).length <= 50, "Name must be 3-50 characters");
        require(bytes(description).length <= 500, "Description too long");

        organizationCount++;
        uint256 orgId = organizationCount;

        Org storage org = organizations[orgId];
        org.id = orgId;
        org.owner = msg.sender;
        org.name = name;
        org.description = description;
        org.createdAt = block.timestamp;
        org.isActive = true;

        // Add creator as owner
        org.members.push(msg.sender);
        org.memberRoles[msg.sender] = ROLE_OWNER;

        // Add to user's organization list
        userOrganizations[msg.sender].push(orgId);

        emit OrganizationCreated(orgId, msg.sender, name);
    }

    /**
     * @dev Update organization details
     * @param orgId Organization ID
     * @param field Field to update ("name" or "description")
     * @param value New value
     */
    function updateOrganization(uint256 orgId, string memory field, string memory value) external
        onlyOrgOwner(orgId)
        orgExists(orgId)
    {
        Org storage org = organizations[orgId];

        if (keccak256(bytes(field)) == keccak256(bytes("name"))) {
            require(bytes(value).length >= 3 && bytes(value).length <= 50, "Name must be 3-50 characters");
            org.name = value;
        } else if (keccak256(bytes(field)) == keccak256(bytes("description"))) {
            require(bytes(value).length <= 500, "Description too long");
            org.description = value;
        } else {
            revert("Invalid field");
        }

        emit OrganizationUpdated(orgId, field, value);
    }

    /**
     * @dev Add a member to the organization
     * @param orgId Organization ID
     * @param member Member wallet address
     * @param role Member role (0=owner, 1=admin, 2=member)
     */
    function addMember(uint256 orgId, address member, uint256 role) external
        onlyOrgAdmin(orgId)
        orgExists(orgId)
    {
        require(role <= ROLE_MEMBER, "Invalid role");
        require(member != address(0), "Invalid address");
        require(organizations[orgId].memberRoles[member] > ROLE_MEMBER, "Already a member");

        Org storage org = organizations[orgId];
        org.members.push(member);
        org.memberRoles[member] = role;

        // Add to user's organization list
        userOrganizations[member].push(orgId);

        emit MemberAdded(orgId, member, role);
    }

    /**
     * @dev Remove a member from the organization
     * @param orgId Organization ID
     * @param member Member wallet address
     */
    function removeMember(uint256 orgId, address member) external
        onlyOrgAdmin(orgId)
        orgExists(orgId)
    {
        require(member != organizations[orgId].owner, "Cannot remove owner");
        require(organizations[orgId].memberRoles[member] <= ROLE_MEMBER, "Not a member");

        Org storage org = organizations[orgId];

        // Remove from members array
        for (uint i = 0; i < org.members.length; i++) {
            if (org.members[i] == member) {
                org.members[i] = org.members[org.members.length - 1];
                org.members.pop();
                break;
            }
        }

        // Remove role mapping
        delete org.memberRoles[member];

        // Remove from user's organization list
        _removeFromUserOrganizations(member, orgId);

        emit MemberRemoved(orgId, member);
    }

    /**
     * @dev Change member role
     * @param orgId Organization ID
     * @param member Member wallet address
     * @param newRole New role
     */
    function changeMemberRole(uint256 orgId, address member, uint256 newRole) external
        onlyOrgOwner(orgId)
        orgExists(orgId)
    {
        require(newRole <= ROLE_MEMBER, "Invalid role");
        require(organizations[orgId].memberRoles[member] <= ROLE_MEMBER, "Not a member");
        require(member != organizations[orgId].owner, "Cannot change owner role");

        organizations[orgId].memberRoles[member] = newRole;
        emit MemberRoleChanged(orgId, member, newRole);
    }

    /**
     * @dev Delete organization (owner only)
     * @param orgId Organization ID
     */
    function deleteOrganization(uint256 orgId) external onlyOrgOwner(orgId) orgExists(orgId) {
        Org storage org = organizations[orgId];

        // Remove all members from user organizations
        for (uint i = 0; i < org.members.length; i++) {
            _removeFromUserOrganizations(org.members[i], orgId);
        }

        org.isActive = false;
        emit OrganizationDeleted(orgId);
    }

    /**
     * @dev Get organization details
     */
    // Move memberRoles outside the Org struct
mapping(uint256 => mapping(address => uint256)) public orgMemberRoles;


// Updated getOrganization (Solution 1)
function getOrganization(uint256 orgId)
    external
    view
    orgExists(orgId)
    returns (
        uint256 id,
        address owner,
        string memory name,
        string memory description,
        address[] memory members,
        uint256 createdAt,
        bool isActive
    )
{
    Org storage org = organizations[orgId];
    return (
        org.id,
        org.owner,
        org.name,
        org.description,
        org.members,
        org.createdAt,
        org.isActive
    );
}

// Keep existing role-checking functions
function getMemberRole(uint256 orgId, address member)
    external
    view
    orgExists(orgId)
    returns (uint256)
{
    return organizations[orgId].memberRoles[member];
}

function isMember(uint256 orgId, address member)
    external
    view
    orgExists(orgId)
    returns (bool)
{
    return organizations[orgId].memberRoles[member] <= ROLE_MEMBER;
}

    /**
     * @dev Get user's organizations
     */
    function getUserOrganizations(address user) external view returns (uint256[] memory) {
        return userOrganizations[user];
    }

    /**
     * @dev Get organization members
     */
    function getOrganizationMembers(uint256 orgId) external view orgExists(orgId) returns (address[] memory) {
        return organizations[orgId].members;
    }

    /**
     * @dev Internal function to remove organization from user's list
     */
    function _removeFromUserOrganizations(address user, uint256 orgId) internal {
        uint256[] storage userOrgs = userOrganizations[user];
        for (uint i = 0; i < userOrgs.length; i++) {
            if (userOrgs[i] == orgId) {
                userOrgs[i] = userOrgs[userOrgs.length - 1];
                userOrgs.pop();
                break;
            }
        }
    }

    /**
     * @dev Get active organizations count
     */
    function getActiveOrganizationCount() external view returns (uint256) {
        return organizationCount;
    }

    /**
     * @dev Transfer ownership (only current owner)
     */
    function transferOwnership(uint256 orgId, address newOwner) external onlyOrgOwner(orgId) orgExists(orgId) {
        require(newOwner != address(0), "Invalid address");
        require(newOwner != organizations[orgId].owner, "Already owner");

        address oldOwner = organizations[orgId].owner;
        organizations[orgId].owner = newOwner;

        // Update roles
        organizations[orgId].memberRoles[oldOwner] = ROLE_ADMIN;
        organizations[orgId].memberRoles[newOwner] = ROLE_OWNER;

        emit MemberRoleChanged(orgId, oldOwner, ROLE_ADMIN);
        emit MemberRoleChanged(orgId, newOwner, ROLE_OWNER);
    }
}