"""
MCP Server Generator for Cadence Smart Contracts

This module generates custom MCP servers based on analyzed Cadence contracts.
It creates tools for each contract function, events, and provides contract interaction capabilities.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict

from .contract_analyzer import (
    CadenceContractAnalyzer, 
    ContractAnalysis, 
    Function, 
    Event, 
    AccessLevel
)
from .system_prompt import get_mcp_generation_system_prompt, get_contract_analysis_prompt


class MCPServerGenerator:
    """Generator for custom MCP servers based on contract analysis."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the generator with templates directory."""
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.analyzer = CadenceContractAnalyzer()
    
    def generate_mcp_server(
        self,
        contract_analysis: ContractAnalysis,
        contract_address: str,
        network: str = "testnet",
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """
        Generate MCP server files based on contract analysis.
        
        Returns:
            Dict with file paths as keys and generated content as values
        """
        if output_dir is None:
            output_dir = Path.cwd() / "generated_mcp"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate server file
        server_content = self._generate_server_content(
            contract_analysis, contract_address, network
        )
        
        # Generate client file
        client_content = self._generate_client_content(
            contract_analysis, contract_address, network
        )
        
        # Generate configuration file
        config_content = self._generate_config_content(
            contract_analysis, contract_address, network
        )
        
        # Generate README
        readme_content = self._generate_readme_content(
            contract_analysis, contract_address, network
        )
        
        # Write files
        files = {
            f"{contract_analysis.contract_name.lower()}_mcp_server.py": server_content,
            f"{contract_analysis.contract_name.lower()}_mcp_client.py": client_content,
            f"{contract_analysis.contract_name.lower()}_mcp_config.json": config_content,
            f"{contract_analysis.contract_name.lower()}_README.md": readme_content
        }
        
        for filename, content in files.items():
            file_path = output_dir / filename
            file_path.write_text(content, encoding='utf-8')
        
        return {str(output_dir / filename): content for filename, content in files.items()}
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for AI-powered MCP generation."""
        return get_mcp_generation_system_prompt()

    def get_contract_analysis_prompt(self, contract_content: str) -> str:
        """Get the contract analysis prompt for AI-powered analysis."""
        return get_contract_analysis_prompt(contract_content)

    async def generate_mcp_server_with_ai(self, contract_file: str, output_dir: str,
                                        contract_name: str, contract_address: str, network: str,
                                        ai_client=None) -> None:
        """
        Generate MCP server using AI assistance for enhanced analysis and generation.
        
        Args:
            contract_file: Path to the contract file
            output_dir: Output directory for generated files
            contract_name: Name of the contract
            contract_address: Contract address
            network: Network (testnet, mainnet, etc.)
            ai_client: Optional AI client for enhanced generation
        """
        # Read contract content
        with open(contract_file, 'r') as f:
            contract_content = f.read()
        
        # If AI client is provided, use it for enhanced analysis
        if ai_client:
            try:
                # Get AI analysis of the contract
                analysis_prompt = self.get_contract_analysis_prompt(contract_content)
                ai_analysis = await ai_client.analyze_contract(analysis_prompt)
                
                # Use AI analysis to enhance the generation
                # This would integrate with your existing AI client
                print(f"AI Analysis available for enhanced generation: {len(ai_analysis)} characters")
            except Exception as e:
                print(f"AI analysis failed, falling back to standard analysis: {e}")
        
        # Fall back to standard generation
        await self.generate_mcp_server(contract_file, output_dir, contract_name, contract_address, network)
    
    def _generate_server_content(
        self, 
        analysis: ContractAnalysis, 
        contract_address: str, 
        network: str
    ) -> str:
        """Generate the MCP server Python file content."""
        template_path = self.templates_dir / "mcp_server_template.py"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Server template not found: {template_path}")
        
        template = template_path.read_text(encoding='utf-8')
        
        # Generate replacements
        replacements = {
            "{{CONTRACT_NAME}}": analysis.contract_name,
            "{{CONTRACT_ADDRESS}}": contract_address,
            "{{NETWORK}}": network,
            "{{GENERATION_DATE}}": datetime.now().isoformat(),
            "{{CONTRACT_DOCUMENTATION}}": analysis.contract_documentation or f"MCP Server for {analysis.contract_name} contract",
            "{{PYDANTIC_MODELS}}": self._generate_pydantic_models(analysis),
            "{{CONTRACT_FUNCTIONS}}": self._generate_contract_functions_code(analysis),
            "{{CONTRACT_EVENTS}}": self._generate_contract_events_code(analysis),
            "{{GENERATED_TOOLS}}": self._generate_tools_code(analysis, contract_address, network),
            "{{GENERATED_RESOURCES}}": self._generate_resources_code(analysis),
            "{{CONTRACT_ANALYSIS_JSON}}": json.dumps(asdict(analysis), indent=2, default=str)
        }
        
        # Apply replacements
        content = template
        for placeholder, replacement in replacements.items():
            content = content.replace(placeholder, replacement)
        
        return content
    
    def _generate_client_content(
        self, 
        analysis: ContractAnalysis, 
        contract_address: str, 
        network: str
    ) -> str:
        """Generate the MCP client Python file content."""
        template_path = self.templates_dir / "mcp_client_template.py"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Client template not found: {template_path}")
        
        template = template_path.read_text(encoding='utf-8')
        
        # Generate replacements
        replacements = {
            "{{CONTRACT_NAME}}": analysis.contract_name,
            "{{CONTRACT_ADDRESS}}": contract_address,
            "{{NETWORK}}": network,
            "{{GENERATION_DATE}}": datetime.now().isoformat(),
            "{{CLIENT_METHODS}}": self._generate_client_methods(analysis)
        }
        
        # Apply replacements
        content = template
        for placeholder, replacement in replacements.items():
            content = content.replace(placeholder, replacement)
        
        return content
    
    def _generate_config_content(
        self, 
        analysis: ContractAnalysis, 
        contract_address: str, 
        network: str
    ) -> str:
        """Generate the MCP configuration JSON content."""
        config = {
            "mcpServers": {
                f"{analysis.contract_name.lower()}_mcp": {
                    "command": "python",
                    "args": [f"{analysis.contract_name.lower()}_mcp_server.py"],
                    "env": {
                        "CONTRACT_ADDRESS": contract_address,
                        "NETWORK": network
                    }
                }
            }
        }
        
        return json.dumps(config, indent=2)
    
    def _generate_readme_content(
        self, 
        analysis: ContractAnalysis, 
        contract_address: str, 
        network: str
    ) -> str:
        """Generate README documentation for the MCP server."""
        content = f"""# {analysis.contract_name} MCP Server

Generated MCP server for the {analysis.contract_name} smart contract.

## Contract Information

- **Contract Name**: {analysis.contract_name}
- **Contract Address**: {contract_address}
- **Network**: {network}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Description

{analysis.contract_documentation or f"MCP server providing tools to interact with the {analysis.contract_name} smart contract."}

## Available Tools

### Contract Functions
"""
        
        # Add function documentation
        for func in analysis.functions:
            if func.access_level == AccessLevel.ALL:
                content += f"\n#### `call_{func.name}`\n"
                if func.documentation:
                    content += f"{func.documentation}\n"
                
                content += f"- **Access Level**: {func.access_level.value}\n"
                content += f"- **Return Type**: {func.return_type or 'Void'}\n"
                content += f"- **View Function**: {'Yes' if func.is_view else 'No'}\n"
                
                if func.parameters:
                    content += "- **Parameters**:\n"
                    for param in func.parameters:
                        label_str = f" (label: {param.label})" if param.label else ""
                        content += f"  - `{param.name}`: {param.type}{label_str}\n"
                content += "\n"
        
        # Add events documentation
        if analysis.events:
            content += "\n### Contract Events\n"
            for event in analysis.events:
                content += f"\n#### `{event.name}`\n"
                if event.documentation:
                    content += f"{event.documentation}\n"
                
                if event.parameters:
                    content += "- **Parameters**:\n"
                    for param in event.parameters:
                        content += f"  - `{param.name}`: {param.type}\n"
                content += "\n"
        
        # Add general tools
        content += """
### General Tools

#### `view_contract_info`
Get general information about the contract.

#### `view_contract_code`
View the contract source code.

#### `get_contract_events`
Get recent events emitted by the contract.

## Usage

### Starting the Server

```bash
python {contract_name}_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{config_content}
```

### Example Client Usage

```python
from {contract_name}_mcp_client import ContractMCPClient

async def main():
    client = ContractMCPClient()
    await client.connect()
    
    # View contract info
    info = await client.view_contract_info()
    print(info)
    
    # Call contract functions
    # (Add specific examples based on your contract)
    
    await client.disconnect()
```

## Requirements

- Python 3.8+
- mcp package
- flow-cli (for Flow blockchain interaction)

## Installation

```bash
pip install mcp
# Install Flow CLI: https://developers.flow.com/tools/flow-cli/install
```
""".format(
            contract_name=analysis.contract_name.lower(),
            config_content=self._generate_config_content(analysis, contract_address, network)
        )
        
        return content
    
    def _sanitize_field_name(self, field_name: str) -> tuple[str, str]:
        """
        Sanitize field name to avoid Python keywords and return (field_name, field_definition).
        Returns a tuple of (sanitized_name, field_definition_with_alias_if_needed).
        """
        python_keywords = {
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with',
            'yield', 'True', 'False', 'None'
        }
        
        if field_name in python_keywords:
            sanitized_name = f"{field_name}_"
            field_def = f'{sanitized_name}: {{type}} = Field(alias="{field_name}")'
            return sanitized_name, field_def
        else:
            return field_name, f"{field_name}: {{type}}"

    def _generate_pydantic_models(self, analysis: ContractAnalysis) -> str:
        """Generate Pydantic models for contract parameters."""
        models = []
        
        # Generate models for function parameters
        for func in analysis.functions:
            if func.parameters and func.access_level == AccessLevel.ALL:
                model_name = f"{func.name.title()}Params"
                model_fields = []
                
                for param in func.parameters:
                    # Convert Cadence types to Python types
                    python_type = self._cadence_to_python_type(param.type)
                    sanitized_name, field_template = self._sanitize_field_name(param.name)
                    field_def = f"    {field_template.format(type=python_type)}"
                    
                    if param.label:
                        field_def += f"  # Label: {param.label}"
                    
                    model_fields.append(field_def)
                
                model = f"""
class {model_name}(BaseModel):
    \"\"\"Parameters for {func.name} function.\"\"\"
{chr(10).join(model_fields)}
"""
                models.append(model)
        
        # Generate models for events
        for event in analysis.events:
            if event.parameters:
                model_name = f"{event.name}Event"
                model_fields = []
                
                for param in event.parameters:
                    python_type = self._cadence_to_python_type(param.type)
                    sanitized_name, field_template = self._sanitize_field_name(param.name)
                    field_def = f"    {field_template.format(type=python_type)}"
                    model_fields.append(field_def)
                
                model = f"""
class {model_name}(BaseModel):
    \"\"\"Event data for {event.name}.\"\"\"
{chr(10).join(model_fields)}
"""
                models.append(model)
        
        return "\n".join(models)
    
    def _generate_contract_functions_code(self, analysis: ContractAnalysis) -> str:
        """Generate JSON data for contract function definitions."""
        functions_data = []
        
        for func in analysis.functions:
            if func.access_level == AccessLevel.ALL and not func.is_init:
                func_data = {
                    "name": func.name,
                    "parameters": [{"name": p.name, "type": p.type} for p in func.parameters],
                    "return_type": func.return_type,
                    "documentation": func.documentation or f'Call {func.name} function on the contract.',
                    "is_view": func.is_view
                }
                functions_data.append(func_data)
        
        return json.dumps(functions_data, indent=2)
    
    def _generate_contract_events_code(self, analysis: ContractAnalysis) -> str:
        """Generate JSON data for contract event definitions."""
        events_data = []
        
        for event in analysis.events:
            event_data = {
                "name": event.name,
                "parameters": [{"name": p.name, "type": p.type} for p in event.parameters],
                "documentation": event.documentation or f'{event.name} event from the contract.'
            }
            events_data.append(event_data)
        
        return json.dumps(events_data, indent=2)
    
    def _generate_tools_code(self, analysis: ContractAnalysis, contract_address: str, network: str) -> str:
        """Generate MCP tools code for contract functions."""
        tools = []
        
        # Generate tools for each public function
        for func in analysis.functions:
            if func.access_level == AccessLevel.ALL and not func.is_init:
                tool_code = self._generate_function_tool(func, analysis.contract_name, contract_address, network)
                tools.append(tool_code)
        
        # Generate event monitoring tool
        if analysis.events:
            event_tool = self._generate_events_tool(analysis, contract_address, network)
            tools.append(event_tool)
        
        return "\n".join(tools)
    
    def _generate_function_tool(self, func: Function, contract_name: str, contract_address: str, network: str) -> str:
        """Generate MCP tool for a specific function."""
        tool_name = f"call_{func.name}"
        
        # Generate parameter schema
        if func.parameters:
            param_properties = {}
            required_params = []
            
            for param in func.parameters:
                python_type = self._cadence_to_python_type(param.type)
                param_properties[param.name] = {
                    "type": self._python_to_json_type(python_type),
                    "description": f"Parameter {param.name} of type {param.type}"
                }
                required_params.append(param.name)
            
            schema = {
                "type": "object",
                "properties": param_properties,
                "required": required_params
            }
        else:
            schema = {"type": "object", "properties": {}}
        
        # Generate function call parameters
        if func.parameters:
            call_params = ", ".join([f'arguments.get("{p.name}")' for p in func.parameters])
        else:
            call_params = ""
        
        # Generate Cadence code separately to avoid f-string nesting issues
        param_list = ', '.join([f'{p.name}: {p.type}' for p in func.parameters])
        param_names = ', '.join([p.name for p in func.parameters])
        arg_list = ', '.join([f'"--arg", "String:{p.name}"' for p in func.parameters])
        
        if func.is_view:
            cadence_code = f'''
                import {contract_name} from {contract_address}
                
                access(all) fun main({param_list}): {func.return_type or 'Void'} {{
                    return {contract_name}.{func.name}({param_names})
                }}
                '''
        else:
            cadence_code = f'''
                import {contract_name} from {contract_address}
                
                transaction({param_list}) {{
                    prepare(signer: AuthAccount) {{
                        // Transaction logic here
                    }}
                    
                    execute {{
                        {contract_name}.{func.name}({param_names})
                    }}
                }}
                '''
        
        tool_code = f'''
@mcp.tool()
async def {tool_name}(arguments: dict) -> str:
    """
    {func.documentation or f'Call {func.name} function on the {contract_name} contract.'}
    
    Access Level: {func.access_level.value}
    Return Type: {func.return_type or 'Void'}
    View Function: {'Yes' if func.is_view else 'No'}
    """
    try:
        # Extract parameters
{self._generate_parameter_extraction(func.parameters)}
        
        # Build Flow CLI command
        if {str(func.is_view)}:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "{network}",
                "--code", """{cadence_code}""",
                {arg_list}
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "{network}",
                "--signer", "default",
                "--code", """{cadence_code}""",
                {arg_list}
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({{
            "success": True,
            "result": result,
            "function": "{func.name}",
            "parameters": arguments
        }}, indent=2)
        
    except Exception as e:
        return json.dumps({{
            "success": False,
            "error": str(e),
            "function": "{func.name}",
            "parameters": arguments
        }}, indent=2)
'''
        
        return tool_code
    
    def _generate_parameter_extraction(self, parameters: List) -> str:
        """Generate parameter extraction code."""
        if not parameters:
            return "        # No parameters"
        
        extractions = []
        for param in parameters:
            extractions.append(f'        {param.name} = arguments.get("{param.name}")')
        
        return "\n".join(extractions)
    
    def _generate_events_tool(self, analysis: ContractAnalysis, contract_address: str, network: str) -> str:
        """Generate tool for monitoring contract events."""
        event_names = [event.name for event in analysis.events]
        
        tool_code = f'''
@mcp.tool()
async def get_contract_events(arguments: dict) -> str:
    """
    Get recent events emitted by the {analysis.contract_name} contract.
    
    Available events: {', '.join(event_names)}
    """
    try:
        limit = arguments.get("limit", 10)
        event_type = arguments.get("event_type", "all")
        
        cmd = [
            "flow", "events", "get",
            "--network", "{network}",
            "--start", "latest",
            "--end", "latest",
            f"{analysis.contract_name}.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({{
            "success": True,
            "events": result,
            "contract": "{analysis.contract_name}",
            "limit": limit,
            "event_type": event_type
        }}, indent=2)
        
    except Exception as e:
        return json.dumps({{
            "success": False,
            "error": str(e),
            "contract": "{analysis.contract_name}"
        }}, indent=2)
'''
        
        return tool_code
    
    def _generate_resources_code(self, analysis: ContractAnalysis) -> str:
        """Generate MCP resources code."""
        resources = []
        
        # Contract info resource
        contract_info_resource = f'''
@mcp.resource("contract://{analysis.contract_name.lower()}/info")
class ContractInfoResource(BaseModel):
    """Resource providing contract information."""
    name: str = "{analysis.contract_name}"
    address: str = CONTRACT_ADDRESS
    network: str = NETWORK
    functions: List[str] = {[f.name for f in analysis.functions if f.access_level == AccessLevel.ALL]}
    events: List[str] = {[e.name for e in analysis.events]}
    
    def read(self) -> str:
        return json.dumps({{
            "name": self.name,
            "address": self.address,
            "network": self.network,
            "functions": self.functions,
            "events": self.events,
            "documentation": """{analysis.contract_documentation or f'Smart contract {analysis.contract_name}'}"""
        }}, indent=2)
'''
        resources.append(contract_info_resource)
        
        # Contract code resource
        contract_code_resource = f'''
@mcp.resource("contract://{analysis.contract_name.lower()}/code")
class ContractCodeResource(BaseModel):
    """Resource providing contract source code."""
    
    def read(self) -> str:
        # In a real implementation, this would fetch the actual contract code
        return json.dumps({{
            "contract_name": "{analysis.contract_name}",
            "source_code": "// Contract source code would be fetched here",
            "file_path": "{analysis.file_path or 'unknown'}"
        }}, indent=2)
'''
        resources.append(contract_code_resource)
        
        return "\n".join(resources)
    
    def _generate_client_methods(self, analysis: ContractAnalysis) -> str:
        """Generate client methods for contract functions."""
        methods = []
        
        for func in analysis.functions:
            if func.access_level == AccessLevel.ALL and not func.is_init:
                method_name = f"call_{func.name}"
                
                # Generate method parameters
                if func.parameters:
                    params = ", ".join([f"{p.name}: str" for p in func.parameters])
                    args_dict = "{" + ", ".join([f'"{p.name}": {p.name}' for p in func.parameters]) + "}"
                else:
                    params = ""
                    args_dict = "{}"
                
                method_code = f'''
    async def {method_name}(self{", " + params if params else ""}) -> dict:
        """Call {func.name} function on the contract."""
        return await self.call_tool("{method_name}", {args_dict})
'''
                methods.append(method_code)
        
        # Add events method if events exist
        if analysis.events:
            events_method = '''
    async def get_contract_events(self, limit: int = 10, event_type: str = "all") -> dict:
        """Get recent contract events."""
        return await self.call_tool("get_contract_events", {"limit": limit, "event_type": event_type})
'''
            methods.append(events_method)
        
        return "\n".join(methods)
    
    def _cadence_to_python_type(self, cadence_type: str) -> str:
        """Convert Cadence type to Python type annotation."""
        type_mapping = {
            "String": "str",
            "Int": "int", 
            "UInt": "int",
            "Int8": "int",
            "Int16": "int", 
            "Int32": "int",
            "Int64": "int",
            "Int128": "int",
            "Int256": "int",
            "UInt8": "int",
            "UInt16": "int",
            "UInt32": "int", 
            "UInt64": "int",
            "UInt128": "int",
            "UInt256": "int",
            "Fix64": "float",
            "UFix64": "float",
            "Bool": "bool",
            "Address": "str",
            "Void": "None"
        }
        
        # Handle optional types
        if cadence_type.endswith("?"):
            base_type = cadence_type[:-1]
            python_base = type_mapping.get(base_type, "Any")
            return f"Optional[{python_base}]"
        
        # Handle array types
        if cadence_type.startswith("[") and cadence_type.endswith("]"):
            element_type = cadence_type[1:-1]
            python_element = type_mapping.get(element_type, "Any")
            return f"List[{python_element}]"
        
        return type_mapping.get(cadence_type, "Any")
    
    def _python_to_json_type(self, python_type: str) -> str:
        """Convert Python type to JSON schema type."""
        type_mapping = {
            "str": "string",
            "int": "integer", 
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "Any": "string"  # Default to string for unknown types
        }
        
        # Handle Optional types
        if python_type.startswith("Optional["):
            return self._python_to_json_type(python_type[9:-1])
        
        # Handle List types
        if python_type.startswith("List["):
            return "array"
        
        return type_mapping.get(python_type, "string")