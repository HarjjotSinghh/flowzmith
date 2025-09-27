import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Plus, 
  Code, 
  Coins,
  Shield,
  Database,
  Pause,
  Users,
  Search,
  Filter,
  Edit,
  Trash2,
  Copy,
  Eye
} from "lucide-react";
import Sidebar from "../../components/Sidebar";
import Header from "../../components/Header";

export default function ComponentsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [showCodeModal, setShowCodeModal] = useState(false);
  
  const [newComponent, setNewComponent] = useState({
    name: '',
    category: 'tokens',
    description: '',
    solidity_template: '',
    properties: '{}'
  });

  const queryClient = useQueryClient();

  // Fetch components
  const { data: components = [], isLoading } = useQuery({
    queryKey: ['components'],
    queryFn: async () => {
      const response = await fetch('/api/components');
      if (!response.ok) {
        throw new Error('Failed to fetch components');
      }
      return response.json();
    },
  });

  // Create component mutation
  const createComponentMutation = useMutation({
    mutationFn: async (componentData) => {
      const response = await fetch('/api/components', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(componentData),
      });
      if (!response.ok) {
        throw new Error('Failed to create component');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['components'] });
      setShowCreateModal(false);
      setNewComponent({
        name: '',
        category: 'tokens',
        description: '',
        solidity_template: '',
        properties: '{}'
      });
    },
  });

  const handleCreateComponent = (e) => {
    e.preventDefault();
    if (newComponent.name.trim() && newComponent.solidity_template.trim()) {
      let parsedProperties = {};
      try {
        parsedProperties = JSON.parse(newComponent.properties);
      } catch (e) {
        alert('Invalid JSON in properties field');
        return;
      }

      createComponentMutation.mutate({
        ...newComponent,
        properties: parsedProperties
      });
    }
  };

  // Filter components
  const filteredComponents = components.filter((component) => {
    const matchesSearch = component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (component.description && component.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = categoryFilter === 'all' || component.category === categoryFilter;
    
    return matchesSearch && matchesCategory;
  });

  const getIconForCategory = (category) => {
    switch (category) {
      case 'tokens':
        return Coins;
      case 'access':
        return Shield;
      case 'storage':
        return Database;
      case 'security':
        return Pause;
      case 'defi':
        return Users;
      default:
        return Code;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'tokens':
        return 'border-[#F59E0B] dark:border-[#FCD34D] bg-[#FEF3C7] dark:bg-[rgba(252,211,77,0.15)] text-[#D97706] dark:text-[#FCD34D]';
      case 'access':
        return 'border-[#EF4444] dark:border-[#F87171] bg-[#FEF2F2] dark:bg-[rgba(248,113,113,0.15)] text-[#DC2626] dark:text-[#F87171]';
      case 'storage':
        return 'border-[#6366F1] dark:border-[#A5B4FC] bg-[#EEF2FF] dark:bg-[rgba(165,180,252,0.15)] text-[#4F46E5] dark:text-[#A5B4FC]';
      case 'security':
        return 'border-[#8B5CF6] dark:border-[#C4B5FD] bg-[#F3E8FF] dark:bg-[rgba(196,181,253,0.15)] text-[#7C3AED] dark:text-[#C4B5FD]';
      case 'defi':
        return 'border-[#22C55E] dark:border-[#40D677] bg-[#DCFCE7] dark:bg-[rgba(64,214,119,0.15)] text-[#16A34A] dark:text-[#40D677]';
      default:
        return 'border-[#6B7280] dark:border-[#9CA3AF] bg-[#F3F4F6] dark:bg-[rgba(156,163,175,0.15)] text-[#374151] dark:text-[#9CA3AF]';
    }
  };

  const componentsByCategory = filteredComponents.reduce((acc, component) => {
    if (!acc[component.category]) {
      acc[component.category] = [];
    }
    acc[component.category].push(component);
    return acc;
  }, {});

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
                  Component Library
                </h1>
                <p className="text-[#6F6F6F] dark:text-[#AAAAAA] font-opensans">
                  Reusable smart contract building blocks
                </p>
              </div>
              
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 h-11 px-6 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95 font-inter"
              >
                <Plus size={18} />
                New Component
              </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              {/* Search */}
              <div className="relative flex-1">
                <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#6F6F6F] dark:text-[#AAAAAA]" />
                <input
                  type="text"
                  placeholder="Search components..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors"
                />
              </div>

              {/* Category Filter */}
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white focus:border-black dark:focus:border-white transition-colors"
              >
                <option value="all">All Categories</option>
                <option value="tokens">Tokens</option>
                <option value="access">Access Control</option>
                <option value="storage">Storage</option>
                <option value="security">Security</option>
                <option value="defi">DeFi</option>
              </select>
            </div>
          </div>

          {/* Components Grid */}
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black dark:border-white"></div>
                <p className="mt-4 text-[#6F6F6F] dark:text-[#AAAAAA]">Loading components...</p>
              </div>
            ) : Object.keys(componentsByCategory).length === 0 ? (
              <div className="text-center py-12">
                <Code size={48} className="mx-auto text-[#CCCCCC] dark:text-[#444444] mb-4" />
                <h3 className="text-lg font-semibold text-black dark:text-white mb-2">
                  {searchQuery || categoryFilter !== 'all' 
                    ? 'No components match your filters' 
                    : 'No components yet'
                  }
                </h3>
                <p className="text-[#6F6F6F] dark:text-[#AAAAAA] mb-6">
                  {searchQuery || categoryFilter !== 'all'
                    ? 'Try adjusting your search or filters'
                    : 'Create your first component to get started'
                  }
                </p>
                {!searchQuery && categoryFilter === 'all' && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95"
                  >
                    <Plus size={18} />
                    Create First Component
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-8">
                {Object.entries(componentsByCategory).map(([category, categoryComponents]) => (
                  <div key={category}>
                    <h3 className="text-lg font-semibold text-black dark:text-white mb-4 font-bricolage capitalize">
                      {category} ({categoryComponents.length})
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {categoryComponents.map((component) => {
                        const IconComponent = getIconForCategory(component.category);
                        return (
                          <div
                            key={component.id}
                            className="border border-[#E4E4E7] dark:border-[#333333] rounded-xl p-6 bg-white dark:bg-[#262626] transition-all duration-150 hover:border-[#D1D5DB] dark:hover:border-[#505050] hover:shadow-sm"
                          >
                            <div className="flex items-start justify-between mb-4">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-[#F8F8F8] dark:bg-[#333333] rounded-lg flex items-center justify-center">
                                  <IconComponent size={20} className="text-[#6366F1]" />
                                </div>
                                <div>
                                  <h4 className="font-semibold text-black dark:text-white font-poppins">
                                    {component.name}
                                  </h4>
                                  <span
                                    className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(component.category)} font-montserrat`}
                                  >
                                    {component.category}
                                  </span>
                                </div>
                              </div>
                            </div>

                            <p className="text-sm text-[#6F6F6F] dark:text-[#AAAAAA] mb-4 line-clamp-2">
                              {component.description || 'No description provided'}
                            </p>

                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => {
                                  setSelectedComponent(component);
                                  setShowCodeModal(true);
                                }}
                                className="flex items-center gap-1 px-3 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white text-sm rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95"
                              >
                                <Eye size={14} />
                                View Code
                              </button>
                              
                              <button
                                onClick={() => navigator.clipboard.writeText(component.solidity_template)}
                                className="flex items-center gap-1 px-3 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white text-sm rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95"
                              >
                                <Copy size={14} />
                                Copy
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Component Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold text-black dark:text-white mb-4 font-bricolage">
              Create New Component
            </h3>
            
            <form onSubmit={handleCreateComponent} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Component Name
                  </label>
                  <input
                    type="text"
                    value={newComponent.name}
                    onChange={(e) => setNewComponent({...newComponent, name: e.target.value})}
                    placeholder="ERC20 Token"
                    className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Category
                  </label>
                  <select
                    value={newComponent.category}
                    onChange={(e) => setNewComponent({...newComponent, category: e.target.value})}
                    className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white focus:border-black dark:focus:border-white transition-colors"
                  >
                    <option value="tokens">Tokens</option>
                    <option value="access">Access Control</option>
                    <option value="storage">Storage</option>
                    <option value="security">Security</option>
                    <option value="defi">DeFi</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                  Description
                </label>
                <textarea
                  value={newComponent.description}
                  onChange={(e) => setNewComponent({...newComponent, description: e.target.value})}
                  placeholder="Describe what this component does..."
                  rows={3}
                  className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                  Solidity Template
                </label>
                <textarea
                  value={newComponent.solidity_template}
                  onChange={(e) => setNewComponent({...newComponent, solidity_template: e.target.value})}
                  placeholder="contract {{name}} { ... }"
                  rows={6}
                  className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors font-mono text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                  Properties (JSON)
                </label>
                <textarea
                  value={newComponent.properties}
                  onChange={(e) => setNewComponent({...newComponent, properties: e.target.value})}
                  placeholder='{"tokenName": {"type": "text", "label": "Token Name", "default": "MyToken"}}'
                  rows={4}
                  className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-black dark:focus:border-white transition-colors font-mono text-sm"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] text-[#4D4D4D] dark:text-[#B0B0B0] rounded-lg transition-all duration-150 hover:bg-[#F5F5F5] dark:hover:bg-[#333333] active:scale-95"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createComponentMutation.isLoading}
                  className="flex-1 px-4 py-3 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createComponentMutation.isLoading ? 'Creating...' : 'Create Component'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Code View Modal */}
      {showCodeModal && selectedComponent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] w-full max-w-4xl h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-[#E6E6E6] dark:border-[#333333]">
              <h3 className="text-xl font-semibold text-black dark:text-white font-bricolage">
                {selectedComponent.name} - Code
              </h3>
              <button
                onClick={() => setShowCodeModal(false)}
                className="p-2 text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-black dark:hover:text-white rounded-lg"
              >
                ×
              </button>
            </div>
            
            <div className="flex-1 p-6 overflow-auto">
              <pre className="bg-[#F8F8F8] dark:bg-[#0F0F0F] p-4 rounded-lg text-sm font-mono text-black dark:text-white overflow-auto">
                {selectedComponent.solidity_template}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}