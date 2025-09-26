"use client";

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import ReactFlow, {
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  Controls,
  MiniMap,
  Background,
  Panel,
  ReactFlowProvider,
  useReactFlow,
  Handle,
  Position,
  MarkerType,
  useKeyPress,
  useOnSelectionChange,
  getIncomers,
  getOutgoers,
  getConnectedEdges,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Play, Database, Cloud, Code, Timer, Filter, Terminal,
  X, Zap, ChevronLeft, ChevronRight, Edit, Copy, Trash2,
  Save, Settings, Grid, Lock, Unlock, Download, Upload,
  Eye, EyeOff, Layers, Search, Plus, Minus, Maximize2,
  GitBranch, Cpu, Server, Box, Activity, Bell, Hash,
  Shield, DollarSign, Check, Coins, FileCode, Wallet
} from 'lucide-react';

// Web3 Smart Contract node types
const nodeTypes = {
  // Contract Deployment
  Deploy: { icon: Zap, color: 'from-violet-500 to-purple-600', glow: 'violet', category: 'deployment' },
  Constructor: { icon: Box, color: 'from-blue-500 to-cyan-600', glow: 'blue', category: 'deployment' },

  // Token Operations
  MintToken: { icon: Plus, color: 'from-emerald-500 to-green-600', glow: 'emerald', category: 'token' },
  BurnToken: { icon: Minus, color: 'from-red-500 to-orange-600', glow: 'red', category: 'token' },
  Transfer: { icon: GitBranch, color: 'from-indigo-500 to-blue-600', glow: 'indigo', category: 'token' },
  Approve: { icon: Check, color: 'from-teal-500 to-cyan-600', glow: 'teal', category: 'token' },

  // DeFi Operations
  Swap: { icon: Activity, color: 'from-purple-500 to-pink-600', glow: 'purple', category: 'defi' },
  AddLiquidity: { icon: Layers, color: 'from-blue-500 to-indigo-600', glow: 'blue', category: 'defi' },
  Stake: { icon: Lock, color: 'from-amber-500 to-yellow-600', glow: 'amber', category: 'defi' },
  Withdraw: { icon: Unlock, color: 'from-cyan-500 to-teal-600', glow: 'cyan', category: 'defi' },

  // Smart Contract Logic
  Require: { icon: Filter, color: 'from-rose-500 to-red-600', glow: 'rose', category: 'logic' },
  Modifier: { icon: Shield, color: 'from-slate-500 to-gray-600', glow: 'slate', category: 'logic' },
  Event: { icon: Bell, color: 'from-orange-500 to-amber-600', glow: 'orange', category: 'logic' },

  // Data & Storage
  Mapping: { icon: Database, color: 'from-green-500 to-emerald-600', glow: 'green', category: 'storage' },
  Array: { icon: Server, color: 'from-indigo-500 to-purple-600', glow: 'indigo', category: 'storage' },
  Struct: { icon: Grid, color: 'from-pink-500 to-rose-600', glow: 'pink', category: 'storage' },

  // External Calls
  Oracle: { icon: Cloud, color: 'from-blue-500 to-sky-600', glow: 'blue', category: 'external' },
  Interface: { icon: Code, color: 'from-purple-500 to-indigo-600', glow: 'purple', category: 'external' },
  Payable: { icon: DollarSign, color: 'from-green-500 to-emerald-600', glow: 'green', category: 'external' },
};

// Custom edge styles
const edgeOptions = {
  type: 'smoothstep',
  animated: true,
  style: {
    strokeWidth: 2,
    stroke: '#64748b',
  },
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 20,
    height: 20,
    color: '#64748b',
  },
};

// Initial nodes for smart contract
const initialNodes = [
  {
    id: 'node-1',
    type: 'customNode',
    data: {
      label: 'Deploy Contract',
      type: 'Deploy',
      description: 'Deploy smart contract to blockchain',
      status: 'idle',
      config: {
        network: 'ethereum',
        gasLimit: '3000000'
      }
    },
    position: { x: 100, y: 100 },
  },
  {
    id: 'node-2',
    type: 'customNode',
    data: {
      label: 'Initialize Storage',
      type: 'Constructor',
      description: 'Set initial contract state',
      status: 'idle',
      config: {
        params: ['owner', 'totalSupply']
      }
    },
    position: { x: 400, y: 100 },
  },
];

// Generate unique IDs
let nodeIdCounter = 3;
const getNodeId = () => `node-${nodeIdCounter++}`;

// Custom Node Component with enhanced UI and animations
const CustomNode = React.memo(({ id, data, selected, isConnectable }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const [localData, setLocalData] = useState(data);
  const actionTimeout = useRef(null);

  const nodeType = nodeTypes[data.type] || nodeTypes.Function;
  const Icon = nodeType.icon;

  const { setNodes, setEdges, getNode, getNodes, getEdges } = useReactFlow();

  // Handle hover with delay
  const handleMouseEnter = () => {
    setIsHovered(true);
    if (actionTimeout.current) clearTimeout(actionTimeout.current);
    actionTimeout.current = setTimeout(() => {
      setShowActions(true);
    }, 300);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    if (actionTimeout.current) clearTimeout(actionTimeout.current);
    actionTimeout.current = setTimeout(() => {
      setShowActions(false);
    }, 200);
  };

  useEffect(() => {
    return () => {
      if (actionTimeout.current) clearTimeout(actionTimeout.current);
    };
  }, []);

  // Node action handlers
  const handleEdit = (e) => {
    e.stopPropagation();
    const newLabel = prompt('Edit node label:', localData.label);
    if (newLabel && newLabel !== localData.label) {
      setNodes((nodes) =>
        nodes.map((node) =>
          node.id === id
            ? { ...node, data: { ...node.data, label: newLabel } }
            : node
        )
      );
      setLocalData({ ...localData, label: newLabel });
    }
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this node?')) {
      setNodes((nodes) => nodes.filter((node) => node.id !== id));
      setEdges((edges) => edges.filter((edge) => edge.source !== id && edge.target !== id));
    }
  };

  const handleDuplicate = (e) => {
    e.stopPropagation();
    const currentNode = getNode(id);
    if (currentNode) {
      const newNode = {
        ...currentNode,
        id: getNodeId(),
        position: {
          x: currentNode.position.x + 50,
          y: currentNode.position.y + 50,
        },
        data: {
          ...currentNode.data,
          label: `${currentNode.data.label} (Copy)`,
        },
      };
      setNodes((nodes) => [...nodes, newNode]);
    }
  };

  const statusColors = {
    idle: 'bg-gray-500',
    running: 'bg-yellow-500 animate-pulse',
    success: 'bg-green-500',
    error: 'bg-red-500',
  };

  return (
    <div
      className={`
        relative group transition-all duration-300 ease-out
        ${selected ? 'scale-105' : isHovered ? 'scale-102' : 'scale-100'}
        ${selected ? 'z-50' : isHovered ? 'z-40' : 'z-30'}
      `}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Glow effect */}
      {(selected || isHovered) && (
        <div className={`
          absolute inset-0 rounded-2xl bg-gradient-to-r ${nodeType.color}
          blur-xl opacity-30 -z-10 transition-all duration-300
          ${selected ? 'scale-110' : 'scale-105'}
        `} />
      )}

      {/* Main node container */}
      <div className={`
        relative bg-gray-900/90 backdrop-blur-xl rounded-2xl
        border-2 transition-all duration-300 min-w-[220px]
        ${selected
          ? `border-transparent bg-gradient-to-r ${nodeType.color} p-[2px]`
          : isHovered
            ? 'border-gray-600 shadow-2xl'
            : 'border-gray-700 shadow-lg'
        }
      `}>
        <div className={`
          bg-gray-900/95 rounded-2xl p-4
          ${selected ? '' : ''}
        `}>
          {/* Status indicator */}
          <div className="absolute top-2 right-2">
            <div className={`w-2 h-2 rounded-full ${statusColors[data.status || 'idle']}`} />
          </div>

          {/* Node content */}
          <div className="flex items-start space-x-3">
            <div className={`
              p-2.5 rounded-xl bg-gradient-to-br ${nodeType.color}
              shadow-lg flex-shrink-0 transform transition-transform duration-200
              ${isHovered ? 'rotate-3 scale-110' : ''}
            `}>
              <Icon className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-white text-sm truncate pr-4">
                {localData.label}
              </h3>
              <p className="text-xs text-gray-400 mt-0.5">{data.type}</p>
              {data.description && (
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                  {data.description}
                </p>
              )}
            </div>
          </div>

          {/* Hover actions */}
          {showActions && (
            <div className={`
              absolute -top-12 left-1/2 transform -translate-x-1/2
              flex items-center space-x-1 bg-gray-800/95 backdrop-blur-xl
              px-2 py-1.5 rounded-full shadow-2xl border border-gray-700
              transition-all duration-300 ease-out
              ${showActions ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-75 -translate-y-2'}
            `}>
              <button
                onClick={handleEdit}
                className="p-1.5 rounded-full bg-blue-500/20 hover:bg-blue-500/40 
                         text-blue-400 transition-all duration-200 hover:scale-110"
                title="Edit"
              >
                <Edit className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleDuplicate}
                className="p-1.5 rounded-full bg-green-500/20 hover:bg-green-500/40 
                         text-green-400 transition-all duration-200 hover:scale-110"
                title="Duplicate"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleDelete}
                className="p-1.5 rounded-full bg-red-500/20 hover:bg-red-500/40 
                         text-red-400 transition-all duration-200 hover:scale-110"
                title="Delete"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>

        {/* Connection handles */}
        <Handle
          type="target"
          position={Position.Left}
          isConnectable={isConnectable}
          className={`
            !w-3 !h-3 !bg-gray-600 !border-2 !border-gray-900
            transition-all duration-200
            ${isHovered ? '!w-4 !h-4 !bg-blue-500' : ''}
          `}
        />
        <Handle
          type="source"
          position={Position.Right}
          isConnectable={isConnectable}
          className={`
            !w-3 !h-3 !bg-gray-600 !border-2 !border-gray-900
            transition-all duration-200
            ${isHovered ? '!w-4 !h-4 !bg-green-500' : ''}
          `}
        />
      </div>
    </div>
  );
});

// Enhanced Sidebar Component
const Sidebar = ({ isExpanded, toggle }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = {
    all: 'All Nodes',
    deployment: 'Deployment',
    token: 'Token Ops',
    defi: 'DeFi',
    logic: 'Logic',
    storage: 'Storage',
    external: 'External',
  };

  const nodeCategories = {
    deployment: ['Deploy', 'Constructor'],
    token: ['MintToken', 'BurnToken', 'Transfer', 'Approve'],
    defi: ['Swap', 'AddLiquidity', 'Stake', 'Withdraw'],
    logic: ['Require', 'Modifier', 'Event'],
    storage: ['Mapping', 'Array', 'Struct'],
    external: ['Oracle', 'Interface', 'Payable'],
  };

  const filteredNodes = Object.entries(nodeTypes).filter(([type, _]) => {
    const matchesSearch = type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' ||
      nodeCategories[selectedCategory]?.includes(type);
    return matchesSearch && matchesCategory;
  });

  const onDragStart = (event, nodeType) => {
    const nodeData = {
      type: 'customNode',
      label: `New ${nodeType}`,
      nodeType: nodeType,
    };
    event.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className={`
      ${isExpanded ? 'w-80' : 'w-16'}
      bg-gray-950 border-r border-gray-800 flex flex-col
      transition-all duration-300 ease-in-out shadow-2xl
      relative overflow-hidden
    `}>
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-purple-900/10 to-transparent pointer-events-none" />

      {/* Header */}
      <div className="relative p-4 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <h2 className={`
            font-bold text-transparent bg-clip-text bg-gradient-to-r 
            from-purple-400 to-pink-400 transition-all duration-300 pointer-events-none
            ${isExpanded ? 'text-xl' : 'text-xs w-0 opacity-0'}
          `}>
            Contract Blocks
          </h2>
          <button
            onClick={toggle}
            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 cursor-pointer
                     text-gray-400 hover:text-white transition-all duration-200"
          >
            {isExpanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>

        {/* Search and filters */}
        {isExpanded && (
          <div className="mt-4 space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search nodes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 bg-gray-900 border border-gray-800 
                         rounded-lg text-sm text-white placeholder-gray-500
                         focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            <div className="flex flex-wrap gap-2">
              {Object.entries(categories).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setSelectedCategory(key)}
                  className={`
                    px-3 py-1 rounded-full text-xs font-medium transition-all
                    ${selectedCategory === key
                      ? 'bg-purple-500 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                    }
                  `}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Node list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
        {filteredNodes.map(([type, config]) => {
          const Icon = config.icon;
          return (
            <div
              key={type}
              draggable
              onDragStart={(e) => onDragStart(e, type)}
              className={`
                relative group cursor-move transition-all duration-200
                ${isExpanded
                  ? 'p-3 bg-gray-900 hover:bg-gray-800 rounded-xl border border-gray-800 hover:border-gray-700'
                  : 'p-2 hover:bg-gray-800 rounded-lg'
                }
              `}
            >
              {/* Hover glow */}
              <div className={`
                absolute inset-0 rounded-xl bg-gradient-to-r ${config.color}
                opacity-0 group-hover:opacity-20 transition-opacity duration-300 blur-xl
              `} />

              <div className={`
                relative flex items-center
                ${isExpanded ? 'space-x-3' : 'justify-center'}
              `}>
                <div className={`
                  p-2 rounded-lg bg-gradient-to-r ${config.color}
                  shadow-lg flex-shrink-0 transform transition-transform
                  group-hover:scale-110 group-hover:rotate-3
                `}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                {isExpanded && (
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-white">{type}</h3>
                    <p className="text-xs text-gray-500">
                      {nodeCategories.deployment?.includes(type) && 'Deploy'}
                      {nodeCategories.token?.includes(type) && 'Token'}
                      {nodeCategories.defi?.includes(type) && 'DeFi'}
                      {nodeCategories.logic?.includes(type) && 'Logic'}
                      {nodeCategories.storage?.includes(type) && 'Storage'}
                      {nodeCategories.external?.includes(type) && 'External'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer stats */}
      {isExpanded && (
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{filteredNodes.length} nodes available</span>
            <span className="flex items-center space-x-1">
              <Grid className="w-3 h-3" />
              <span>Grid: On</span>
            </span>
          </div>
        </div>
      )}
    </aside>
  );
};

// Toolbar Component
const Toolbar = ({ onSave, onLoad, onClear, onExport }) => {
  return (
    <Panel position="top-center" className="bg-gray-900/95 backdrop-blur-xl rounded-full px-6 py-3 shadow-2xl border border-gray-800">
      <div className="flex items-center space-x-2">
        <button
          onClick={onSave}
          className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-all"
          title="Save Workflow"
        >
          <Save className="w-4 h-4" />
        </button>
        <button
          onClick={onLoad}
          className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-all"
          title="Load Workflow"
        >
          <Upload className="w-4 h-4" />
        </button>
        <button
          onClick={onExport}
          className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-all"
          title="Export"
        >
          <Download className="w-4 h-4" />
        </button>
        <div className="w-px h-6 bg-gray-700 mx-2" />
        <button
          onClick={onClear}
          className="p-2 rounded-lg bg-gray-800 hover:bg-red-900 text-gray-400 hover:text-red-400 transition-all"
          title="Clear Canvas"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </Panel>
  );
};

// Main Flow Component
const Flow = () => {
  const { screenToFlowPosition, getNodes, getEdges, fitView, zoomIn, zoomOut } = useReactFlow();
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState([]);
  const [selectedNodes, setSelectedNodes] = useState([]);

  // Keyboard shortcuts
  const deleteKey = useKeyPress(['Delete', 'Backspace']);

  useEffect(() => {
    if (deleteKey && selectedNodes.length > 0) {
      setNodes((nds) => nds.filter((node) => !selectedNodes.includes(node.id)));
      setEdges((eds) => eds.filter((edge) =>
        !selectedNodes.includes(edge.source) && !selectedNodes.includes(edge.target)
      ));
      setSelectedNodes([]);
    }
  }, [deleteKey, selectedNodes]);

  // Selection change handler
  useOnSelectionChange({
    onChange: ({ nodes }) => {
      setSelectedNodes(nodes.map(n => n.id));
    },
  });

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (connection) => {
      const edge = {
        ...connection,
        ...edgeOptions,
        id: `edge-${connection.source}-${connection.target}`,
      };
      setEdges((eds) => addEdge(edge, eds));
    },
    []
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const data = event.dataTransfer.getData('application/reactflow');
      if (!data) return;

      const { label, nodeType } = JSON.parse(data);
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode = {
        id: getNodeId(),
        type: 'customNode',
        position,
        data: {
          label,
          type: nodeType,
          description: `${nodeType} node`,
          status: 'idle',
          config: {},
        },
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [screenToFlowPosition]
  );

  // Workflow management functions
  const handleSave = () => {
    const workflow = {
      nodes: getNodes(),
      edges: getEdges(),
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('workflow', JSON.stringify(workflow));
    alert('Workflow saved!');
  };

  const handleLoad = () => {
    const saved = localStorage.getItem('workflow');
    if (saved) {
      const { nodes: savedNodes, edges: savedEdges } = JSON.parse(saved);
      setNodes(savedNodes || []);
      setEdges(savedEdges || []);
      setTimeout(() => fitView(), 100);
    }
  };

  const handleClear = () => {
    if (confirm('Clear all nodes and connections?')) {
      setNodes([]);
      setEdges([]);
    }
  };

  const handleExport = () => {
    const workflow = {
      nodes: getNodes(),
      edges: getEdges(),
      contractType: 'ERC-20', // or detect from nodes
      network: 'ethereum',
    };
    const dataStr = JSON.stringify(workflow, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

    const exportFileDefaultName = `smart-contract-${Date.now()}.json`;
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();

    // You could also add export to Solidity/.sol file functionality here
    alert('Contract structure exported! Next: Generate Solidity/Cadence code');
  };

  const nodeTypesMemo = useMemo(() => ({
    customNode: CustomNode,
  }), []);

  return (
    <div className="flex-1 h-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypesMemo}
        defaultEdgeOptions={edgeOptions}
        fitView
        className="bg-gray-950"
        proOptions={{ hideAttribution: true }}
        deleteKeyCode={['Delete', 'Backspace']}
        multiSelectionKeyCode={['Meta', 'Control']}
      >
        {/* Grid Background */}
        <Background
          variant="dots"
          gap={20}
          size={1.5}
          color="#374151"
        />

        {/* Mini Map */}
        <MiniMap
          className="!bg-gray-900 !border-gray-800 rounded-xl shadow-2xl"
          maskColor="rgba(0, 0, 0, 0.8)"
          position='top-right'
          nodeColor={(node) => {
            const type = nodeTypes[node.data?.type];
            return type ? '#6366f1' : '#374151';
          }}
          nodeStrokeWidth={3}
          pannable
          zoomable
        />

        {/* Controls */}
        <Controls
          className="!bg-gray-900 !border-gray-800 !rounded-xl !shadow-2xl"
          showInteractive={false}
        />

        {/* Header */}
        <Panel position="top-left" className="bg-gray-900/95 backdrop-blur-xl rounded-2xl p-5 shadow-2xl border border-gray-800">
          <div>
            <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400">
              Smart Contract Builder
            </h1>
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-2">
              <Wallet className="w-3 h-3" />
              Visual Web3 Development Platform
            </p>
          </div>
        </Panel>

        {/* Toolbar */}
        <Toolbar
          onSave={handleSave}
          onLoad={handleLoad}
          onClear={handleClear}
          onExport={handleExport}
        />

        {/* Stats Panel */}
        {/* <Panel position="bottom-left" className="bg-gray-900/95 backdrop-blur-xl rounded-xl px-4 py-2 ml-[100px] shadow-xl border border-gray-800">
          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-2 text-gray-400">
              <Box className="w-3 h-3" />
              <span>{nodes.length} nodes</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-400">
              <GitBranch className="w-3 h-3" />
              <span>{edges.length} connections</span>
            </div>
            {selectedNodes.length > 0 && (
              <div className="flex items-center space-x-2 text-purple-400">
                <Activity className="w-3 h-3" />
                <span>{selectedNodes.length} selected</span>
              </div>
            )}
          </div>
        </Panel> */}

        {/* Help Panel */}
        <Panel position="bottom-right" className="bg-gray-900/95 backdrop-blur-xl rounded-xl px-4 py-2 shadow-xl border border-gray-800 max-w-xs">
          <div className="text-xs text-gray-500 space-y-1">
            <p>• Drag contract blocks from sidebar</p>
            <p>• Connect to build contract flow</p>
            <p>• Export as Solidity/Cadence</p>
            <p>• Test on local blockchain</p>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

// Main Application Component
const WorkflowWhiteboard = () => {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);

  return (
    <ReactFlowProvider>
      <div className="flex h-screen w-full bg-gray-950 overflow-hidden">
        <Sidebar
          isExpanded={isSidebarExpanded}
          toggle={() => setIsSidebarExpanded(!isSidebarExpanded)}
        />
        <Flow />
      </div>
    </ReactFlowProvider>
  );
};

export default WorkflowWhiteboard;