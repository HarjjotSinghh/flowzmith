import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Code, 
  Copy, 
  ExternalLink, 
  Play, 
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Clock,
  Hash
} from "lucide-react";

export default function ContractView({ params }) {
  const { id } = params;
  const [selectedTab, setSelectedTab] = useState('info');
  const [testInput, setTestInput] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [copiedAddress, setCopiedAddress] = useState(false);

  // Fetch contract details
  const { data: contract, isLoading } = useQuery({
    queryKey: ['contract', id],
    queryFn: async () => {
      const response = await fetch(`/api/contracts/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch contract');
      }
      return response.json();
    },
  });

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedAddress(true);
    setTimeout(() => setCopiedAddress(false), 2000);
  };

  const formatAddress = (address) => {
    if (!address) return 'Not deployed';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const handleTest = () => {
    if (!testInput.trim()) return;
    
    // Simulate a test transaction
    const newResult = {
      id: Date.now(),
      input: testInput,
      output: `Transaction successful: ${Math.random().toString(16).substr(2, 8)}`,
      timestamp: new Date().toLocaleTimeString(),
      status: 'success'
    };
    
    setTestResults([newResult, ...testResults]);
    setTestInput('');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F3F3F3] dark:bg-[#0A0A0A] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black dark:border-white mb-4"></div>
          <p className="text-[#6F6F6F] dark:text-[#AAAAAA]">Loading contract...</p>
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="min-h-screen bg-[#F3F3F3] dark:bg-[#0A0A0A] flex items-center justify-center">
        <div className="text-center">
          <AlertCircle size={48} className="mx-auto text-[#DC2626] mb-4" />
          <h2 className="text-xl font-semibold text-black dark:text-white mb-2">Contract Not Found</h2>
          <p className="text-[#6F6F6F] dark:text-[#AAAAAA] mb-4">The contract you're looking for doesn't exist.</p>
          <a href="/" className="text-[#6366F1] hover:underline">Back to Dashboard</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F3F3F3] dark:bg-[#0A0A0A]">
      {/* Header */}
      <div className="bg-white dark:bg-[#1E1E1E] border-b border-[#E6E6E6] dark:border-[#333333]">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-6">
          <div className="flex items-center gap-4 mb-4">
            <a 
              href="/"
              className="flex items-center gap-2 text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-black dark:hover:text-white transition-colors"
            >
              <ArrowLeft size={20} />
              Back to Dashboard
            </a>
          </div>
          
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-black dark:text-white font-sora mb-2">
                {contract.name}
              </h1>
              <p className="text-[#6F6F6F] dark:text-[#AAAAAA] font-opensans">
                {contract.description || 'Smart contract deployment'}
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <span 
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  contract.status === 'deployed' 
                    ? 'bg-[#DCFCE7] dark:bg-[rgba(64,214,119,0.15)] text-[#16A34A] dark:text-[#40D677] border border-[#22C55E] dark:border-[#40D677]'
                    : 'bg-[#FEF3C7] dark:bg-[rgba(252,211,77,0.15)] text-[#D97706] dark:text-[#FCD34D] border border-[#F59E0B] dark:border-[#FCD34D]'
                }`}
              >
                {contract.status}
              </span>
              
              <a
                href={`/builder/${contract.id}`}
                className="flex items-center gap-2 px-4 py-2 bg-[#F5F5F5] dark:bg-[#333333] text-black dark:text-white rounded-lg transition-all duration-150 hover:bg-[#EEEEEE] dark:hover:bg-[#404040] active:scale-95"
              >
                <Code size={16} />
                Edit Contract
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Contract Info */}
            <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6 mb-6">
              <h2 className="text-xl font-semibold text-black dark:text-white mb-4 font-bricolage">
                Contract Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Contract Address
                  </label>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 px-3 py-2 bg-[#F8F8F8] dark:bg-[#0F0F0F] rounded-lg text-sm font-mono text-black dark:text-white">
                      {contract.deployed_address || 'Not deployed'}
                    </code>
                    {contract.deployed_address && (
                      <button
                        onClick={() => copyToClipboard(contract.deployed_address)}
                        className="p-2 text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-black dark:hover:text-white rounded-lg transition-colors"
                      >
                        {copiedAddress ? <CheckCircle size={16} className="text-green-500" /> : <Copy size={16} />}
                      </button>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Network
                  </label>
                  <div className="px-3 py-2 bg-[#F8F8F8] dark:bg-[#0F0F0F] rounded-lg text-sm text-black dark:text-white">
                    {contract.network || 'localhost'}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Created
                  </label>
                  <div className="px-3 py-2 bg-[#F8F8F8] dark:bg-[#0F0F0F] rounded-lg text-sm text-black dark:text-white">
                    {new Date(contract.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Last Updated
                  </label>
                  <div className="px-3 py-2 bg-[#F8F8F8] dark:bg-[#0F0F0F] rounded-lg text-sm text-black dark:text-white">
                    {new Date(contract.updated_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Contract Code */}
            <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-black dark:text-white font-bricolage">
                  Contract Code
                </h2>
                <button
                  onClick={() => copyToClipboard(contract.contract_code || '')}
                  className="flex items-center gap-2 px-3 py-2 text-sm text-[#6F6F6F] dark:text-[#AAAAAA] hover:text-black dark:hover:text-white rounded-lg transition-colors"
                >
                  <Copy size={14} />
                  Copy Code
                </button>
              </div>
              
              <pre className="bg-[#F8F8F8] dark:bg-[#0F0F0F] p-4 rounded-lg text-sm font-mono text-black dark:text-white overflow-auto max-h-96">
                {contract.contract_code || '// No contract code available'}
              </pre>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6">
              <h3 className="text-lg font-semibold text-black dark:text-white mb-4 font-bricolage">
                Quick Actions
              </h3>
              
              <div className="space-y-3">
                {contract.deployed_address && (
                  <button className="w-full flex items-center gap-3 p-3 text-left rounded-lg bg-[#F8F8F8] dark:bg-[#262626] hover:bg-[#F0F0F0] dark:hover:bg-[#2A2A2A] transition-colors">
                    <ExternalLink size={18} className="text-[#6366F1]" />
                    <div>
                      <div className="font-medium text-sm text-black dark:text-white">View on Etherscan</div>
                      <div className="text-xs text-[#6F6F6F] dark:text-[#AAAAAA]">Open in block explorer</div>
                    </div>
                  </button>
                )}
                
                <button className="w-full flex items-center gap-3 p-3 text-left rounded-lg bg-[#F8F8F8] dark:bg-[#262626] hover:bg-[#F0F0F0] dark:hover:bg-[#2A2A2A] transition-colors">
                  <Hash size={18} className="text-[#6366F1]" />
                  <div>
                    <div className="font-medium text-sm text-black dark:text-white">Verify Contract</div>
                    <div className="text-xs text-[#6F6F6F] dark:text-[#AAAAAA]">Verify source code</div>
                  </div>
                </button>
                
                <a
                  href={`/builder/${contract.id}`}
                  className="w-full flex items-center gap-3 p-3 text-left rounded-lg bg-[#F8F8F8] dark:bg-[#262626] hover:bg-[#F0F0F0] dark:hover:bg-[#2A2A2A] transition-colors"
                >
                  <Code size={18} className="text-[#6366F1]" />
                  <div>
                    <div className="font-medium text-sm text-black dark:text-white">Edit Contract</div>
                    <div className="text-xs text-[#6F6F6F] dark:text-[#AAAAAA]">Modify and redeploy</div>
                  </div>
                </a>
              </div>
            </div>

            {/* Testing */}
            {contract.status === 'deployed' && (
              <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6">
                <h3 className="text-lg font-semibold text-black dark:text-white mb-4 font-bricolage">
                  Test Contract
                </h3>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                    Function Input
                  </label>
                  <input
                    type="text"
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    placeholder="Enter test parameters..."
                    className="w-full px-3 py-2 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] text-sm"
                  />
                </div>
                
                <button
                  onClick={handleTest}
                  disabled={!testInput.trim()}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-b from-[#6366F1] to-[#4F46E5] text-white rounded-lg transition-all duration-150 hover:from-[#5B5FE7] hover:to-[#4338CA] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play size={16} />
                  Execute
                </button>
                
                {testResults.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                      Recent Tests
                    </h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {testResults.slice(0, 3).map((result) => (
                        <div key={result.id} className="p-2 bg-[#F8F8F8] dark:bg-[#262626] rounded text-xs">
                          <div className="flex items-center gap-2 mb-1">
                            <CheckCircle size={12} className="text-green-500" />
                            <span className="text-[#6F6F6F] dark:text-[#AAAAAA]">{result.timestamp}</span>
                          </div>
                          <div className="text-black dark:text-white font-mono">
                            {result.output}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}