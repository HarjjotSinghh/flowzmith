import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Plus, 
  Code, 
  Rocket, 
  Edit, 
  Trash2, 
  Eye, 
  Filter,
  Search,
  Calendar,
  Network
} from "lucide-react";
import Sidebar from "../../components/Sidebar";
import Header from "../../components/Header";

export default function ContractsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [networkFilter, setNetworkFilter] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newContractName, setNewContractName] = useState("");
  const queryClient = useQueryClient();

  // Fetch contracts
  const { data: contracts = [], isLoading } = useQuery({
    queryKey: ['contracts'],
    queryFn: async () => {
      const response = await fetch('/api/contracts');
      if (!response.ok) {
        throw new Error('Failed to fetch contracts');
      }
      return response.json();
    },
  });

  // Create contract mutation
  const createContractMutation = useMutation({
    mutationFn: async (contractData) => {
      const response = await fetch('/api/contracts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contractData),
      });
      if (!response.ok) {
        throw new Error('Failed to create contract');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      setShowCreateModal(false);
      setNewContractName('');
    },
  });

  // Delete contract mutation
  const deleteContractMutation = useMutation({
    mutationFn: async (contractId) => {
      const response = await fetch(`/api/contracts/${contractId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete contract');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });

  const handleCreateContract = (e) => {
    e.preventDefault();
    if (newContractName.trim()) {
      createContractMutation.mutate({
        name: newContractName.trim(),
        description: `Smart contract: ${newContractName.trim()}`
      });
    }
  };

  // Filter contracts
  const filteredContracts = contracts.filter((contract) => {
    const matchesSearch = contract.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (contract.description && contract.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || contract.status === statusFilter;
    const matchesNetwork = networkFilter === 'all' || contract.network === networkFilter;
    
    return matchesSearch && matchesStatus && matchesNetwork;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'deployed':
        return 'border-[#22C55E] dark:border-[#40D677] bg-[#DCFCE7] dark:bg-[rgba(64,214,119,0.15)] text-[#16A34A] dark:text-[#40D677]';
      case 'draft':
        return 'border-[#F59E0B] dark:border-[#FCD34D] bg-[#FEF3C7] dark:bg-[rgba(252,211,77,0.15)] text-[#D97706] dark:text-[#FCD34D]';
      default:
        return 'border-[#6B7280] dark:border-[#9CA3AF] bg-[#F3F4F6] dark:bg-[rgba(156,163,175,0.15)] text-[#374151] dark:text-[#9CA3AF]';
    }
  };

  return (
    <div className="flex h-screen bg-[#F3F3F3] dark:bg-[#0A0A0A]">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
        fixed lg:static inset-y-0 left-0 z-50 lg:z-auto
        transform ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
        lg:translate-x-0 transition-transform duration-300 ease-in-out
      `}
      >
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(true)} />

        {/* Content area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white font-sora mb-2">
                  Smart Contracts
                </h1>
                <p className="text-[#6F6F6F] dark:text-[#AAAAAA] font-opensans">
                  Manage and deploy your smart contracts
                </p>
              </div>
              
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 h-11 px-6 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95 font-inter"
              >
                <Plus size={18} />
                New Contract
              </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              {/* Search */}
              <div className="relative flex-1">
                <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#6F6F6F] dark:text-[#AAAAAA]" />
                <input
                  type="text"
                  placeholder="Search contracts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors"
                />
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white focus:border-black dark:focus:border-white transition-colors"
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="deployed">Deployed</option>
              </select>

              {/* Network Filter */}
              <select
                value={networkFilter}
                onChange={(e) => setNetworkFilter(e.target.value)}
                className="px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white focus:border-black dark:focus:border-white transition-colors"
              >
                <option value="all">All Networks</option>
                <option value="localhost">Localhost</option>
                <option value="sepolia">Sepolia</option>
                <option value="mainnet">Mainnet</option>
              </select>
            </div>
          </div>

          {/* Contracts List */}
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black dark:border-white"></div>
                <p className="mt-4 text-[#6F6F6F] dark:text-[#AAAAAA]">Loading contracts...</p>
              </div>
            ) : filteredContracts.length === 0 ? (
              <div className="text-center py-12">
                <Code size={48} className="mx-auto text-[#CCCCCC] dark:text-[#444444] mb-4" />
                <h3 className="text-lg font-semibold text-black dark:text-white mb-2">
                  {searchQuery || statusFilter !== 'all' || networkFilter !== 'all' 
                    ? 'No contracts match your filters' 
                    : 'No contracts yet'
                  }
                </h3>
                <p className="text-[#6F6F6F] dark:text-[#AAAAAA] mb-6">
                  {searchQuery || statusFilter !== 'all' || networkFilter !== 'all'
                    ? 'Try adjusting your search or filters'
                    : 'Create your first smart contract to get started'
                  }
                </p>
                {!searchQuery && statusFilter === 'all' && networkFilter === 'all' && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95"
                  >
                    <Plus size={18} />
                    Create First Contract
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredContracts.map((contract) => (
                  <div
                    key={contract.id}
                    className="border border-[#E4E4E7] dark:border-[#333333] rounded-xl p-6 bg-white dark:bg-[#262626] transition-all duration-150 hover:border-[#D1D5DB] dark:hover:border-[#505050] hover:shadow-sm"
                  >
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-lg text-black dark:text-white font-poppins">
                            {contract.name}
                          </h3>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(contract.status)} font-montserrat`}
                          >
                            {contract.status}
                          </span>
                        </div>

                        <p className="text-sm text-[#6F6F6F] dark:text-[#AAAAAA] mb-3">
                          {contract.description || 'No description provided'}
                        </p>

                        <div className="flex items-center gap-4 text-xs text-[#999999] dark:text-[#666666]">
                          <div className="flex items-center gap-1">
                            <Calendar size={12} />
                            Created {new Date(contract.created_at).toLocaleDateString()}
                          </div>
                          {contract.network && (
                            <div className="flex items-center gap-1">
                              <Network size={12} />
                              {contract.network}
                            </div>
                          )}
                          {contract.deployed_address && (
                            <div className="flex items-center gap-1">
                              <Code size={12} />
                              {contract.deployed_address.slice(0, 8)}...
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <a
                          href={`/builder/${contract.id}`}
                          className="flex items-center gap-1 px-3 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white text-sm rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95"
                        >
                          <Edit size={14} />
                          Edit
                        </a>
                        
                        {contract.status === 'deployed' && (
                          <a
                            href={`/contracts/${contract.id}/view`}
                            className="flex items-center gap-1 px-3 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white text-sm rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95"
                          >
                            <Eye size={14} />
                            View
                          </a>
                        )}
                        
                        <button
                          onClick={() => deleteContractMutation.mutate(contract.id)}
                          className="flex items-center gap-1 px-3 py-2 bg-[#FEF2F2] dark:bg-[#4C1D1D] text-[#DC2626] dark:text-[#F87171] text-sm rounded-lg transition-all duration-150 hover:bg-[#FEE2E2] dark:hover:bg-[#5B2121] active:scale-95"
                        >
                          <Trash2 size={14} />
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Contract Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-black dark:text-white mb-4 font-bricolage">
              Create New Contract
            </h3>
            
            <form onSubmit={handleCreateContract}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                  Contract Name
                </label>
                <input
                  type="text"
                  value={newContractName}
                  onChange={(e) => setNewContractName(e.target.value)}
                  placeholder="My Awesome Contract"
                  className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors"
                  autoFocus
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] text-[#4D4D4D] dark:text-[#B0B0B0] rounded-lg transition-all duration-150 hover:bg-[#F5F5F5] dark:hover:bg-[#333333] active:scale-95"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newContractName.trim() || createContractMutation.isLoading}
                  className="flex-1 px-4 py-3 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createContractMutation.isLoading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}