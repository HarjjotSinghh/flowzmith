import { useState, useEffect, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Code, 
  Play, 
  Save, 
  Rocket, 
  TestTube, 
  Eye, 
  Settings, 
  X, 
  Plus,
  Coins,
  Shield,
  Database,
  Pause,
  Users,
  Image
} from "lucide-react";
import useContractStore from "../../../store/contractStore";

export default function ContractBuilder({ params }) {
  const { id } = params;
  const [selectedTab, setSelectedTab] = useState('design');
  const [draggedComponent, setDraggedComponent] = useState(null);
  const [selectedElement, setSelectedElement] = useState(null);
  const [showCodePreview, setShowCodePreview] = useState(false);
  const [showDeployModal, setShowDeployModal] = useState(false);
  
  const queryClient = useQueryClient();
  
  const {
    currentContract,
    setCurrentContract,
    components,
    setComponents,
    canvasElements,
    addCanvasElement,
    updateCanvasElement,
    removeCanvasElement,
    generateContractCode
  } = useContractStore();

  // Fetch contract details
  const { data: contract } = useQuery({
    queryKey: ['contract', id],
    queryFn: async () => {
      const response = await fetch(`/api/contracts/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch contract');
      }
      return response.json();
    },
    onSuccess: (data) => {
      setCurrentContract(data);
    }
  });

  // Fetch components
  const { data: componentsList = [] } = useQuery({
    queryKey: ['components'],
    queryFn: async () => {
      const response = await fetch('/api/components');
      if (!response.ok) {
        throw new Error('Failed to fetch components');
      }
      return response.json();
    },
    onSuccess: (data) => {
      setComponents(data);
    }
  });

  // Save contract mutation
  const saveContractMutation = useMutation({
    mutationFn: async (updates) => {
      const response = await fetch(`/api/contracts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (!response.ok) {
        throw new Error('Failed to save contract');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contract', id] });
    },
  });

  // Deploy contract mutation
  const deployContractMutation = useMutation({
    mutationFn: async (deployData) => {
      const response = await fetch(`/api/contracts/${id}/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deployData),
      });
      if (!response.ok) {
        throw new Error('Failed to deploy contract');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contract', id] });
      setShowDeployModal(false);
    },
  });

  const handleSave = () => {
    const contractCode = generateContractCode();
    saveContractMutation.mutate({
      contract_code: contractCode
    });
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    if (!draggedComponent) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    addCanvasElement({
      componentId: draggedComponent.id,
      x,
      y,
      properties: {}
    });

    setDraggedComponent(null);
  }, [draggedComponent, addCanvasElement]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

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

  const componentsByCategory = componentsList.reduce((acc, component) => {
    if (!acc[component.category]) {
      acc[component.category] = [];
    }
    acc[component.category].push(component);
    return acc;
  }, {});

  return (
    <div className="flex h-screen bg-[#F3F3F3] dark:bg-[#0A0A0A]">
      {/* Left Sidebar - Component Library */}
      <div className="w-80 bg-white dark:bg-[#1E1E1E] border-r border-[#E6E6E6] dark:border-[#333333] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-[#E6E6E6] dark:border-[#333333]">
          <h2 className="text-lg font-semibold text-black dark:text-white font-bricolage mb-2">
            Component Library
          </h2>
          <p className="text-sm text-[#6F6F6F] dark:text-[#AAAAAA]">
            Drag components to the canvas to build your contract
          </p>
        </div>

        {/* Components */}
        <div className="flex-1 overflow-y-auto p-4">
          {Object.entries(componentsByCategory).map(([category, categoryComponents]) => (
            <div key={category} className="mb-6">
              <h3 className="text-sm font-semibold text-[#4D4D4D] dark:text-[#B0B0B0] uppercase tracking-wide mb-3">
                {category}
              </h3>
              <div className="space-y-2">
                {categoryComponents.map((component) => {
                  const IconComponent = getIconForCategory(component.category);
                  return (
                    <div
                      key={component.id}
                      draggable
                      onDragStart={() => setDraggedComponent(component)}
                      className="p-3 bg-[#F8F8F8] dark:bg-[#262626] rounded-lg border border-[#E6E6E6] dark:border-[#333333] cursor-grab active:cursor-grabbing transition-all duration-150 hover:bg-[#F0F0F0] dark:hover:bg-[#2A2A2A] hover:border-[#D1D5DB] dark:hover:border-[#404040]"
                    >
                      <div className="flex items-center gap-3">
                        <IconComponent size={18} className="text-[#6366F1]" />
                        <div>
                          <div className="font-medium text-sm text-black dark:text-white">
                            {component.name}
                          </div>
                          <div className="text-xs text-[#6F6F6F] dark:text-[#AAAAAA]">
                            {component.description}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Toolbar */}
        <div className="h-16 bg-white dark:bg-[#1E1E1E] border-b border-[#E6E6E6] dark:border-[#333333] flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <a href="/" className="text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-black dark:hover:text-white">
              ← Back to Dashboard
            </a>
            <div className="h-6 w-px bg-[#E6E6E6] dark:bg-[#333333]"></div>
            <h1 className="text-lg font-semibold text-black dark:text-white">
              {contract?.name || 'Contract Builder'}
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleSave}
              disabled={saveContractMutation.isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95 disabled:opacity-50"
            >
              <Save size={16} />
              {saveContractMutation.isLoading ? 'Saving...' : 'Save'}
            </button>

            <button
              onClick={() => setShowCodePreview(true)}
              className="flex items-center gap-2 px-4 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95"
            >
              <Code size={16} />
              Preview Code
            </button>

            <button
              onClick={() => setShowDeployModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-b from-[#6366F1] to-[#4F46E5] text-white rounded-lg transition-all duration-150 hover:from-[#5B5FE7] hover:to-[#4338CA] active:scale-95"
            >
              <Rocket size={16} />
              Deploy
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div
          className="flex-1 relative bg-[#FAFAFA] dark:bg-[#0F0F0F] overflow-auto"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {/* Grid Background */}
          <div
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage: `
                linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px'
            }}
          />

          {/* Canvas Elements */}
          {canvasElements.map((element) => {
            const component = components.find(c => c.id === element.componentId);
            if (!component) return null;

            const IconComponent = getIconForCategory(component.category);

            return (
              <div
                key={element.id}
                className={`absolute p-4 bg-white dark:bg-[#1E1E1E] rounded-lg border-2 transition-all duration-150 cursor-pointer ${
                  selectedElement === element.id
                    ? 'border-[#6366F1] shadow-lg'
                    : 'border-[#E6E6E6] dark:border-[#333333] hover:border-[#D1D5DB] dark:hover:border-[#404040]'
                }`}
                style={{ left: element.x, top: element.y }}
                onClick={() => setSelectedElement(element.id)}
              >
                <div className="flex items-center gap-3 mb-2">
                  <IconComponent size={20} className="text-[#6366F1]" />
                  <span className="font-medium text-black dark:text-white">
                    {component.name}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeCanvasElement(element.id);
                    }}
                    className="ml-auto p-1 text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-[#DC2626] dark:hover:text-[#F87171] rounded"
                  >
                    <X size={14} />
                  </button>
                </div>
                <p className="text-xs text-[#6F6F6F] dark:text-[#AAAAAA]">
                  {component.description}
                </p>
              </div>
            );
          })}

          {/* Empty State */}
          {canvasElements.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Code size={48} className="mx-auto text-[#CCCCCC] dark:text-[#444444] mb-4" />
                <h3 className="text-lg font-semibold text-black dark:text-white mb-2">
                  Start Building Your Contract
                </h3>
                <p className="text-[#6F6F6F] dark:text-[#AAAAAA] mb-4">
                  Drag components from the left sidebar to get started
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Properties */}
      {selectedElement && (
        <div className="w-80 bg-white dark:bg-[#1E1E1E] border-l border-[#E6E6E6] dark:border-[#333333] p-6">
          <h3 className="text-lg font-semibold text-black dark:text-white mb-4">
            Properties
          </h3>
          
          {(() => {
            const element = canvasElements.find(el => el.id === selectedElement);
            const component = components.find(c => c.id === element?.componentId);
            
            if (!component || !component.properties) {
              return <p className="text-[#6F6F6F] dark:text-[#AAAAAA]">No properties available</p>;
            }

            const properties = JSON.parse(component.properties);
            
            return (
              <div className="space-y-4">
                {Object.entries(properties).map(([key, config]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                      {config.label || key}
                    </label>
                    
                    {config.type === 'select' ? (
                      <select
                        value={element.properties?.[key] || config.default || ''}
                        onChange={(e) => updateCanvasElement(selectedElement, {
                          properties: { ...element.properties, [key]: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white"
                      >
                        {config.options.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    ) : config.type === 'number' ? (
                      <input
                        type="number"
                        value={element.properties?.[key] || config.default || ''}
                        onChange={(e) => updateCanvasElement(selectedElement, {
                          properties: { ...element.properties, [key]: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white"
                      />
                    ) : (
                      <input
                        type="text"
                        value={element.properties?.[key] || config.default || ''}
                        onChange={(e) => updateCanvasElement(selectedElement, {
                          properties: { ...element.properties, [key]: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white"
                      />
                    )}
                  </div>
                ))}
              </div>
            );
          })()}
        </div>
      )}

      {/* Code Preview Modal */}
      {showCodePreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] w-full max-w-4xl h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-[#E6E6E6] dark:border-[#333333]">
              <h3 className="text-xl font-semibold text-black dark:text-white font-bricolage">
                Generated Contract Code
              </h3>
              <button
                onClick={() => setShowCodePreview(false)}
                className="p-2 text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-black dark:hover:text-white rounded-lg"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="flex-1 p-6 overflow-auto">
              <pre className="bg-[#F8F8F8] dark:bg-[#0F0F0F] p-4 rounded-lg text-sm font-mono text-black dark:text-white overflow-auto">
                {generateContractCode() || '// No components added yet'}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Deploy Modal */}
      {showDeployModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-black dark:text-white mb-4 font-bricolage">
              Deploy Contract
            </h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                Network
              </label>
              <select className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white">
                <option>Localhost</option>
                <option>Sepolia Testnet</option>
                <option>Ethereum Mainnet</option>
              </select>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowDeployModal(false)}
                className="flex-1 px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] text-[#4D4D4D] dark:text-[#B0B0B0] rounded-lg transition-all duration-150 hover:bg-[#F5F5F5] dark:hover:bg-[#333333] active:scale-95"
              >
                Cancel
              </button>
              <button
                onClick={() => deployContractMutation.mutate({ network: 'localhost' })}
                disabled={deployContractMutation.isLoading}
                className="flex-1 px-4 py-3 bg-gradient-to-b from-[#6366F1] to-[#4F46E5] text-white rounded-lg transition-all duration-150 hover:from-[#5B5FE7] hover:to-[#4338CA] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deployContractMutation.isLoading ? 'Deploying...' : 'Deploy'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}