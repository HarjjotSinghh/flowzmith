"""
CLI Suggestions System

Provides contextual "what's next" suggestions and command recommendations
after completing various CLI workflows.
"""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

console = Console()

class CLISuggestions:
    """Centralized system for providing contextual CLI suggestions."""

    def __init__(self):
        self.suggestions_map = {
            "contract_creation": self._get_contract_creation_suggestions,
            "contract_deployment": self._get_deployment_suggestions,
            "documentation_search": self._get_documentation_suggestions,
            "documentation_upload": self._get_documentation_upload_suggestions,
            "flow_automation": self._get_flow_automation_suggestions,
            "wizard_complete": self._get_wizard_complete_suggestions,
        }

    def show_suggestions(self, workflow_type: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Display contextual suggestions for the given workflow type."""
        if workflow_type not in self.suggestions_map:
            return

        suggestions = self.suggestions_map[workflow_type](context or {})
        if not suggestions:
            return

        self._display_suggestions(suggestions, workflow_type)

    def _display_suggestions(self, suggestions: Dict[str, Any], workflow_type: str) -> None:
        """Display suggestions in a formatted panel."""
        title = suggestions.get("title", "🚀 What's Next?")
        
        # Create the main content
        content_lines = []
        
        if suggestions.get("description"):
            content_lines.append(suggestions["description"])
            content_lines.append("")

        # Add primary suggestions
        if suggestions.get("primary_actions"):
            content_lines.append("**🎯 Recommended Next Steps:**")
            for action in suggestions["primary_actions"]:
                content_lines.append(f"• **{action['title']}** - {action['description']}")
                content_lines.append(f"  `{action['command']}`")
                content_lines.append("")

        # Add secondary suggestions
        if suggestions.get("secondary_actions"):
            content_lines.append("**📋 Other Available Commands:**")
            for action in suggestions["secondary_actions"]:
                content_lines.append(f"• **{action['title']}** - {action['description']}")
                content_lines.append(f"  `{action['command']}`")
                content_lines.append("")

        # Add coming soon features
        if suggestions.get("coming_soon"):
            content_lines.append("**🔮 Coming Soon:**")
            for feature in suggestions["coming_soon"]:
                content_lines.append(f"• **{feature['title']}** - {feature['description']}")
                if feature.get("eta"):
                    content_lines.append(f"  *Expected: {feature['eta']}*")
                content_lines.append("")

        # Add tips
        if suggestions.get("tips"):
            content_lines.append("**💡 Pro Tips:**")
            for tip in suggestions["tips"]:
                content_lines.append(f"• {tip}")
                content_lines.append("")

        content = "\n".join(content_lines).strip()
        
        console.print(Panel(
            Markdown(content),
            title=title,
            border_style="bright_blue",
            expand=True
        ))

    def _get_contract_creation_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get suggestions after contract creation."""
        contract_name = context.get("contract_name", "your contract")
        has_deployment_info = context.get("has_deployment_info", False)
        project_path = context.get("project_path")
        
        suggestions = {
            "title": "🎉 Contract Created Successfully!",
            "description": f"Your smart contract '{contract_name}' has been generated and is ready for the next steps.",
            "primary_actions": [],
            "secondary_actions": [],
            "coming_soon": [
                {
                    "title": "Contract Security Audit",
                    "description": "AI-powered security analysis and vulnerability detection",
                    "eta": "Q2 2026"
                },
                {
                    "title": "Automated Testing Suite",
                    "description": "Generate comprehensive test cases for your contract",
                    "eta": "Q2 2026"
                }
            ],
            "tips": [
                "Review your contract code before deployment",
                "Test on emulator first before deploying to testnet",
                "Keep your private keys secure and never share them"
            ]
        }

        # Primary action: Deploy the contract
        if not has_deployment_info:
            suggestions["primary_actions"].append({
                "title": "Deploy Contract",
                "description": "Deploy your contract to Flow blockchain (testnet/mainnet)",
                "command": "python cli.py deploy-contract"
            })
        
        # Secondary actions
        suggestions["secondary_actions"].extend([
            {
                "title": "Create Another Contract",
                "description": "Generate a new smart contract",
                "command": "python cli.py create-contract"
            },
            {
                "title": "Run Full Wizard",
                "description": "Complete end-to-end contract creation and deployment",
                "command": "python cli.py wizard"
            },
            {
                "title": "Search Documentation",
                "description": "Find Flow/Cadence documentation and examples",
                "command": "python cli.py search-docs"
            },
            {
                "title": "View System Status",
                "description": "Check system health and deployment statistics",
                "command": "python cli.py status"
            }
        ])

        if project_path:
            suggestions["tips"].append(f"Your project files are saved at: {project_path}")

        return suggestions

    def _get_deployment_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get suggestions after contract deployment."""
        contract_name = context.get("contract_name", "your contract")
        network = context.get("network", "testnet")
        contract_address = context.get("contract_address")
        transaction_hash = context.get("transaction_hash")
        
        suggestions = {
            "title": "🚀 Contract Deployed Successfully!",
            "description": f"Your contract '{contract_name}' is now live on {network}!",
            "primary_actions": [
                {
                    "title": "View Deployment History",
                    "description": "See all your contract deployments",
                    "command": "python cli.py list-deployments"
                }
            ],
            "secondary_actions": [
                {
                    "title": "Deploy Another Contract",
                    "description": "Deploy a different contract to the blockchain",
                    "command": "python cli.py deploy-contract"
                },
                {
                    "title": "Create New Contract",
                    "description": "Generate and deploy a new smart contract",
                    "command": "python cli.py create-contract"
                },
                {
                    "title": "Search Documentation",
                    "description": "Learn about interacting with deployed contracts",
                    "command": "python cli.py search-docs"
                }
            ],
            "coming_soon": [
                {
                    "title": "Contract Interaction Tools",
                    "description": "Call contract functions and view state directly from CLI",
                    "eta": "Q2 2024"
                },
                {
                    "title": "Contract Monitoring",
                    "description": "Real-time monitoring of contract events and transactions",
                    "eta": "Q3 2026"
                }
            ],
            "tips": [
                "Save your contract address for future interactions",
                "Monitor your contract on Flow blockchain explorer",
                "Consider setting up event listeners for your contract"
            ]
        }

        if contract_address:
            suggestions["tips"].append(f"Contract Address: {contract_address}")
        
        if transaction_hash:
            suggestions["tips"].append(f"Transaction Hash: {transaction_hash}")

        return suggestions

    def _get_documentation_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get suggestions after documentation search."""
        query = context.get("query", "")
        results_count = context.get("results_count", 0)
        
        suggestions = {
            "title": "📚 Documentation Search Complete",
            "description": f"Found {results_count} results for your search.",
            "primary_actions": [
                {
                    "title": "Create Contract",
                    "description": "Use the documentation to create a new smart contract",
                    "command": "python cli.py create-contract"
                }
            ],
            "secondary_actions": [
                {
                    "title": "Search Again",
                    "description": "Search for different documentation",
                    "command": "python cli.py search-docs"
                },
                {
                    "title": "Browse Categories",
                    "description": "Browse documentation by categories",
                    "command": "python cli.py browse-docs"
                },
                {
                    "title": "Upload Documentation",
                    "description": "Add new documentation to the knowledge base",
                    "command": "python cli.py upload-docs"
                }
            ],
            "tips": [
                "Use specific keywords for better search results",
                "Browse categories to discover new topics",
                "Upload your own documentation to help the community"
            ]
        }

        return suggestions

    def _get_documentation_upload_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get suggestions after documentation upload."""
        files_uploaded = context.get("files_uploaded", 0)
        
        suggestions = {
            "title": "📤 Documentation Uploaded Successfully!",
            "description": f"Successfully uploaded {files_uploaded} documentation file(s) to the knowledge base.",
            "primary_actions": [
                {
                    "title": "Search Documentation",
                    "description": "Search the updated knowledge base",
                    "command": "python cli.py search-docs"
                }
            ],
            "secondary_actions": [
                {
                    "title": "Upload More Documentation",
                    "description": "Add more files to the knowledge base",
                    "command": "python cli.py upload-docs"
                },
                {
                    "title": "Create Contract",
                    "description": "Create a contract using the new documentation",
                    "command": "python cli.py create-contract"
                }
            ],
            "tips": [
                "Your uploaded documentation is now searchable",
                "Well-structured documentation improves AI contract generation",
                "Consider adding examples and code snippets to your documentation"
            ]
        }

        return suggestions

    def _get_flow_automation_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get suggestions after Flow automation workflow."""
        contract_name = context.get("contract_name", "your contract")
        deployment_successful = context.get("deployment_successful", False)
        
        suggestions = {
            "title": "🔄 Flow Automation Complete!",
            "description": f"Automated workflow for '{contract_name}' has been completed.",
            "primary_actions": [],
            "secondary_actions": [
                {
                    "title": "Run Another Automation",
                    "description": "Start another automated Flow workflow",
                    "command": "python cli.py flow-auto"
                },
                {
                    "title": "View Deployments",
                    "description": "Check deployment status and history",
                    "command": "python cli.py list-deployments"
                }
            ],
            "coming_soon": [
                {
                    "title": "Advanced Flow Automation",
                    "description": "Multi-contract deployments and complex workflows",
                    "eta": "Q3 2024"
                }
            ],
            "tips": [
                "Flow automation saves time on repetitive tasks",
                "Review generated files before production deployment"
            ]
        }

        if deployment_successful:
            suggestions["primary_actions"].append({
                "title": "Monitor Deployment",
                "description": "Check your deployed contract status",
                "command": "python cli.py status"
            })
        else:
            suggestions["primary_actions"].append({
                "title": "Deploy Contract",
                "description": "Deploy your generated contract manually",
                "command": "python cli.py deploy-contract"
            })

        return suggestions

    def _get_wizard_complete_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get suggestions after completing the full wizard."""
        contract_name = context.get("contract_name", "your contract")
        
        suggestions = {
            "title": "🧙 Wizard Complete!",
            "description": f"You've successfully completed the full contract creation and deployment wizard for '{contract_name}'.",
            "primary_actions": [
                {
                    "title": "View System Status",
                    "description": "Check overall system health and statistics",
                    "command": "python cli.py status"
                }
            ],
            "secondary_actions": [
                {
                    "title": "Run Wizard Again",
                    "description": "Create and deploy another contract",
                    "command": "python cli.py wizard"
                },
                {
                    "title": "Manual Contract Creation",
                    "description": "Create a contract with more control",
                    "command": "python cli.py create-contract"
                },
                {
                    "title": "Search Documentation",
                    "description": "Learn more about Flow and Cadence",
                    "command": "python cli.py search-docs"
                }
            ],
            "coming_soon": [
                {
                    "title": "Advanced Wizard",
                    "description": "Multi-contract projects and complex deployments",
                    "eta": "Q3 2024"
                }
            ],
            "tips": [
                "The wizard is perfect for quick prototyping",
                "Use manual commands for more advanced workflows",
                "Explore documentation to learn advanced patterns"
            ]
        }

        return suggestions

# Global instance for easy access
suggestions = CLISuggestions()