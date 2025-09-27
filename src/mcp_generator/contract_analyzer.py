"""
Contract Analyzer for Cadence Smart Contracts

This module analyzes Cadence smart contracts to extract:
- Functions (public, access-controlled)
- Events
- Resources and Structures
- Interfaces
- Contract metadata

Used for generating custom MCP servers based on contract functionality.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class AccessLevel(Enum):
    """Access levels in Cadence."""
    ALL = "all"
    ACCOUNT = "account"
    CONTRACT = "contract"
    SELF = "self"


@dataclass
class Parameter:
    """Function parameter information."""
    name: str
    type: str
    label: Optional[str] = None


@dataclass
class Function:
    """Function information extracted from contract."""
    name: str
    access_level: AccessLevel
    parameters: List[Parameter]
    return_type: Optional[str]
    is_view: bool = False
    is_init: bool = False
    documentation: Optional[str] = None
    line_number: int = 0


@dataclass
class Event:
    """Event information extracted from contract."""
    name: str
    parameters: List[Parameter]
    documentation: Optional[str] = None
    line_number: int = 0


@dataclass
class Resource:
    """Resource information extracted from contract."""
    name: str
    functions: List[Function]
    documentation: Optional[str] = None
    line_number: int = 0


@dataclass
class Structure:
    """Struct information extracted from contract."""
    name: str
    fields: List[Parameter]
    functions: List[Function]
    documentation: Optional[str] = None
    line_number: int = 0


@dataclass
class Interface:
    """Interface information extracted from contract."""
    name: str
    functions: List[Function]
    documentation: Optional[str] = None
    line_number: int = 0


@dataclass
class ContractAnalysis:
    """Complete contract analysis result."""
    contract_name: str
    functions: List[Function]
    events: List[Event]
    resources: List[Resource]
    structures: List[Structure]
    interfaces: List[Interface]
    imports: List[str]
    contract_documentation: Optional[str] = None
    file_path: Optional[str] = None


class CadenceContractAnalyzer:
    """Analyzer for Cadence smart contracts."""
    
    def __init__(self):
        self.current_line = 0
        self.lines = []
    
    def analyze_contract_file(self, file_path: Path) -> ContractAnalysis:
        """Analyze a Cadence contract file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Contract file not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8')
        return self.analyze_contract_content(content, str(file_path))
    
    def analyze_contract(self, contract_content: str, file_path: Optional[str] = None) -> ContractAnalysis:
        """Analyze a Cadence contract (alias for analyze_contract_content).
        
        Args:
            contract_content: The contract source code
            file_path: Optional path to the contract file
            
        Returns:
            ContractAnalysis object with extracted information
        """
        return self.analyze_contract_content(contract_content, file_path)
    
    def analyze_contract_content(self, content: str, file_path: Optional[str] = None) -> ContractAnalysis:
        """Analyze Cadence contract content."""
        self.lines = content.split('\n')
        self.current_line = 0
        
        # Extract contract name
        contract_name = self._extract_contract_name(content)
        
        # Extract various components
        functions = self._extract_functions(content)
        events = self._extract_events(content)
        resources = self._extract_resources(content)
        structures = self._extract_structures(content)
        interfaces = self._extract_interfaces(content)
        imports = self._extract_imports(content)
        documentation = self._extract_contract_documentation(content)
        
        return ContractAnalysis(
            contract_name=contract_name,
            functions=functions,
            events=events,
            resources=resources,
            structures=structures,
            interfaces=interfaces,
            imports=imports,
            contract_documentation=documentation,
            file_path=file_path
        )
    
    def _extract_contract_name(self, content: str) -> str:
        """Extract the contract name from the content."""
        # Match: access(all) contract ContractName {
        pattern = r'access\([^)]+\)\s+contract\s+(\w+)\s*[:{]'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        
        # Match: pub contract ContractName {
        pattern = r'pub\s+contract\s+(\w+)\s*[:{]'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        
        # Fallback: contract ContractName {
        pattern = r'contract\s+(\w+)\s*[:{]'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        
        return "UnknownContract"
    
    def _extract_functions(self, content: str) -> List[Function]:
        """Extract functions from the contract."""
        functions = []
        
        # Pattern for function definitions with access() syntax
        # access(level) fun functionName(param: Type): ReturnType {
        access_pattern = r'access\(([^)]+)\)\s+fun\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{]+))?\s*\{'
        
        for match in re.finditer(access_pattern, content, re.MULTILINE):
            access_str = match.group(1).strip()
            func_name = match.group(2)
            params_str = match.group(3).strip()
            return_type = match.group(4).strip() if match.group(4) else None
            # Normalize return type to the first line and strip inline comments
            if return_type:
                return_type = return_type.splitlines()[0].strip()
                return_type = re.split(r"//|/\*", return_type)[0].strip()
            
            # Parse access level
            try:
                access_level = AccessLevel(access_str)
            except ValueError:
                access_level = AccessLevel.ALL  # Default
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Check if it's a view function (no state changes)
            is_view = self._is_view_function(content, match.start())
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_function_documentation(content, match.start())
            
            functions.append(Function(
                name=func_name,
                access_level=access_level,
                parameters=parameters,
                return_type=return_type,
                is_view=is_view,
                is_init=(func_name == "init"),
                documentation=documentation,
                line_number=line_number
            ))
        
        # Pattern for pub function definitions (legacy syntax)
        # pub fun functionName(param: Type): ReturnType {
        pub_pattern = r'pub\s+fun\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{]+))?\s*\{'
        
        for match in re.finditer(pub_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            params_str = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None
            # Normalize return type to the first line and strip inline comments
            if return_type:
                return_type = return_type.splitlines()[0].strip()
                return_type = re.split(r"//|/\*", return_type)[0].strip()
            
            # Check if this function was already found with access() syntax
            if any(f.name == func_name for f in functions):
                continue
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Check if it's a view function (no state changes)
            is_view = self._is_view_function(content, match.start())
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_function_documentation(content, match.start())
            
            functions.append(Function(
                name=func_name,
                access_level=AccessLevel.ALL,  # pub functions are public
                parameters=parameters,
                return_type=return_type,
                is_view=is_view,
                is_init=(func_name == "init"),
                documentation=documentation,
                line_number=line_number
            ))
        
        return functions
    
    def _extract_events(self, content: str) -> List[Event]:
        """Extract events from the contract."""
        events = []
        
        # Pattern for event definitions with access() syntax
        # access(all) event EventName(param: Type, param2: Type)
        access_pattern = r'access\([^)]+\)\s+event\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(access_pattern, content, re.MULTILINE):
            event_name = match.group(1)
            params_str = match.group(2).strip()
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_documentation_before(content, match.start())
            
            events.append(Event(
                name=event_name,
                parameters=parameters,
                documentation=documentation,
                line_number=line_number
            ))
        
        # Pattern for pub event definitions (legacy syntax)
        # pub event EventName(param: Type, param2: Type)
        pub_pattern = r'pub\s+event\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(pub_pattern, content, re.MULTILINE):
            event_name = match.group(1)
            params_str = match.group(2).strip()
            
            # Check if this event was already found with access() syntax
            if any(e.name == event_name for e in events):
                continue
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_documentation_before(content, match.start())
            
            events.append(Event(
                name=event_name,
                parameters=parameters,
                documentation=documentation,
                line_number=line_number
            ))
        
        return events
    
    def _extract_resources(self, content: str) -> List[Resource]:
        """Extract resources from the contract."""
        resources = []
        
        # Pattern for resource definitions
        # access(all) resource ResourceName {
        pattern = r'access\([^)]+\)\s+resource\s+(\w+)\s*\{'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            resource_name = match.group(1)
            
            # Extract functions within this resource
            resource_start = match.end()
            resource_end = self._find_matching_brace(content, match.end() - 1)
            resource_content = content[resource_start:resource_end]
            
            resource_functions = self._extract_functions(resource_content)
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_documentation_before(content, match.start())
            
            resources.append(Resource(
                name=resource_name,
                functions=resource_functions,
                documentation=documentation,
                line_number=line_number
            ))
        
        return resources
    
    def _extract_structures(self, content: str) -> List[Structure]:
        """Extract structures from the contract."""
        structures = []
        
        # Pattern for struct definitions
        # access(all) struct StructName {
        pattern = r'access\([^)]+\)\s+struct\s+(\w+)\s*\{'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            struct_name = match.group(1)
            
            # Extract content within this struct
            struct_start = match.end()
            struct_end = self._find_matching_brace(content, match.end() - 1)
            struct_content = content[struct_start:struct_end]
            
            # Extract fields and functions
            fields = self._extract_struct_fields(struct_content)
            struct_functions = self._extract_functions(struct_content)
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_documentation_before(content, match.start())
            
            structures.append(Structure(
                name=struct_name,
                fields=fields,
                functions=struct_functions,
                documentation=documentation,
                line_number=line_number
            ))
        
        return structures
    
    def _extract_interfaces(self, content: str) -> List[Interface]:
        """Extract interfaces from the contract."""
        interfaces = []
        
        # Pattern for interface definitions
        # access(all) resource interface InterfaceName {
        pattern = r'access\([^)]+\)\s+(?:resource\s+)?interface\s+(\w+)\s*\{'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            interface_name = match.group(1)
            
            # Extract functions within this interface
            interface_start = match.end()
            interface_end = self._find_matching_brace(content, match.end() - 1)
            interface_content = content[interface_start:interface_end]
            
            interface_functions = self._extract_functions(interface_content)
            
            # Get line number
            line_number = content[:match.start()].count('\n') + 1
            
            # Extract documentation
            documentation = self._extract_documentation_before(content, match.start())
            
            interfaces.append(Interface(
                name=interface_name,
                functions=interface_functions,
                documentation=documentation,
                line_number=line_number
            ))
        
        return interfaces
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from the contract."""
        imports = []
        
        # Pattern for import statements
        # import ContractName from 0x123456789abcdef
        pattern = r'import\s+(\w+)\s+from\s+(0x[a-fA-F0-9]+|"[^"]+"|\'[^\']+\')'
        
        for match in re.finditer(pattern, content):
            import_name = match.group(1)
            import_address = match.group(2)
            imports.append(f"{import_name} from {import_address}")
        
        return imports
    
    def _parse_parameters(self, params_str: str) -> List[Parameter]:
        """Parse function parameters from parameter string."""
        parameters = []
        
        if not params_str.strip():
            return parameters
        
        # Split by comma, but be careful of nested types
        param_parts = self._split_parameters(params_str)
        
        for param_part in param_parts:
            param_part = param_part.strip()
            if not param_part:
                continue
            
            # Parse: label name: Type or name: Type
            if ':' in param_part:
                name_part, type_part = param_part.split(':', 1)
                name_part = name_part.strip()
                type_part = type_part.strip()
                
                # Check if there's a label
                name_parts = name_part.split()
                if len(name_parts) == 2:
                    label, name = name_parts
                    parameters.append(Parameter(name=name, type=type_part, label=label))
                else:
                    parameters.append(Parameter(name=name_part, type=type_part))
        
        return parameters
    
    def _split_parameters(self, params_str: str) -> List[str]:
        """Split parameters by comma, handling nested types."""
        parts = []
        current_part = ""
        paren_depth = 0
        bracket_depth = 0
        
        for char in params_str:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == ',' and paren_depth == 0 and bracket_depth == 0:
                parts.append(current_part)
                current_part = ""
                continue
            
            current_part += char
        
        if current_part.strip():
            parts.append(current_part)
        
        return parts
    
    def _extract_struct_fields(self, struct_content: str) -> List[Parameter]:
        """Extract fields from struct content."""
        fields = []
        
        # Pattern for field definitions
        # access(all) var fieldName: Type
        pattern = r'access\([^)]+\)\s+var\s+(\w+)\s*:\s*([^=\n]+)'
        
        for match in re.finditer(pattern, struct_content):
            field_name = match.group(1)
            field_type = match.group(2).strip()
            
            fields.append(Parameter(name=field_name, type=field_type))
        
        return fields
    
    def _find_matching_brace(self, content: str, start_pos: int) -> int:
        """Find the matching closing brace for an opening brace."""
        brace_count = 1
        pos = start_pos + 1
        
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return pos
    
    def _is_view_function(self, content: str, func_start: int) -> bool:
        """Determine if a function is a view function (doesn't modify state)."""
        # Extract function body
        func_end = self._find_matching_brace(content, content.find('{', func_start))
        func_body = content[func_start:func_end]
        
        # Check for state-modifying keywords
        state_modifying_keywords = [
            'self.', 'emit ', 'destroy ', 'create ', 'save(', 'load(',
            'borrow(', 'link(', 'unlink(', 'getCapability('
        ]
        
        for keyword in state_modifying_keywords:
            if keyword in func_body:
                return False
        
        return True
    
    def _extract_function_documentation(self, content: str, func_start: int) -> Optional[str]:
        """Extract documentation comment before a function."""
        return self._extract_documentation_before(content, func_start)
    
    def _extract_documentation_before(self, content: str, position: int) -> Optional[str]:
        """Extract documentation comment before a given position."""
        lines_before_pos = content[:position].split('\n')
        
        # Look for comment lines immediately before
        doc_lines = []
        for line in reversed(lines_before_pos[:-1]):  # Exclude the current line
            line = line.strip()
            if line.startswith('//'):
                doc_lines.insert(0, line[2:].strip())
            elif line.startswith('/*') and line.endswith('*/'):
                doc_lines.insert(0, line[2:-2].strip())
            elif line == '':
                continue  # Skip empty lines
            else:
                break  # Stop at non-comment line
        
        return '\n'.join(doc_lines) if doc_lines else None
    
    def _extract_contract_documentation(self, content: str) -> Optional[str]:
        """Extract contract-level documentation."""
        lines = content.split('\n')
        doc_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('//'):
                doc_lines.append(line[2:].strip())
            elif line.startswith('/*') and line.endswith('*/'):
                doc_lines.append(line[2:-2].strip())
            elif line.startswith('access(') and 'contract' in line:
                break  # Reached contract declaration
            elif line and not line.startswith('import'):
                break  # Reached non-comment, non-import line
        
        return '\n'.join(doc_lines) if doc_lines else None
    
    def to_dict(self, analysis: ContractAnalysis) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return asdict(analysis)
    
    def to_json(self, analysis: ContractAnalysis, indent: int = 2) -> str:
        """Convert analysis result to JSON string."""
        return json.dumps(self.to_dict(analysis), indent=indent, default=str)