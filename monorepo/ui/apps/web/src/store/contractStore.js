import { create } from 'zustand';

const useContractStore = create((set, get) => ({
  // State
  contracts: [],
  components: [],
  currentContract: null,
  selectedComponents: [],
  canvasElements: [],
  
  // Actions
  setContracts: (contracts) => set({ contracts }),
  setComponents: (components) => set({ components }),
  setCurrentContract: (contract) => set({ currentContract: contract }),
  
  addCanvasElement: (element) => set((state) => ({
    canvasElements: [...state.canvasElements, {
      ...element,
      id: Date.now(),
      x: element.x || 100,
      y: element.y || 100
    }]
  })),
  
  updateCanvasElement: (id, updates) => set((state) => ({
    canvasElements: state.canvasElements.map(el => 
      el.id === id ? { ...el, ...updates } : el
    )
  })),
  
  removeCanvasElement: (id) => set((state) => ({
    canvasElements: state.canvasElements.filter(el => el.id !== id)
  })),
  
  clearCanvas: () => set({ canvasElements: [] }),
  
  generateContractCode: () => {
    const { canvasElements, components } = get();
    
    if (canvasElements.length === 0) {
      return '';
    }
    
    let contractCode = '// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n\n';
    
    // Add imports based on components
    const imports = new Set();
    canvasElements.forEach(element => {
      const component = components.find(c => c.id === element.componentId);
      if (component) {
        if (component.category === 'tokens' && component.name.includes('ERC20')) {
          imports.add('import "@openzeppelin/contracts/token/ERC20/ERC20.sol";');
        }
        if (component.category === 'tokens' && component.name.includes('ERC721')) {
          imports.add('import "@openzeppelin/contracts/token/ERC721/ERC721.sol";');
        }
        if (component.category === 'access') {
          imports.add('import "@openzeppelin/contracts/access/Ownable.sol";');
        }
        if (component.category === 'security') {
          imports.add('import "@openzeppelin/contracts/utils/Pausable.sol";');
        }
      }
    });
    
    contractCode += Array.from(imports).join('\n') + '\n\n';
    
    // Generate contract
    contractCode += `contract GeneratedContract {\n`;
    
    canvasElements.forEach(element => {
      const component = components.find(c => c.id === element.componentId);
      if (component) {
        let template = component.solidity_template;
        
        // Replace template variables
        template = template.replace(/\{\{name\}\}/g, 'GeneratedContract');
        
        if (element.properties) {
          Object.entries(element.properties).forEach(([key, value]) => {
            template = template.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value);
          });
        }
        
        contractCode += `\n    // ${component.name}\n`;
        contractCode += template.split('\n').map(line => `    ${line}`).join('\n') + '\n';
      }
    });
    
    contractCode += '\n}';
    
    return contractCode;
  }
}));

export default useContractStore;