"""
Documentation search functionality for the CLI.

Handles searching and browsing documentation with semantic search capabilities.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .api_client import APIClient

console = Console()

class DocumentationSearch:
    """Handles documentation search and browsing."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def search_interactive(self) -> None:
        """Run interactive documentation search."""
        console.print("📚 Documentation Search", style="bold blue")
        console.print("Search through the smart contract documentation and knowledge base.", style="dim")

        while True:
            # Get search query
            query = Prompt.ask("\n🔍 Enter search query (or 'quit' to exit)")

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query.strip():
                console.print("❌ Please enter a search query", style="red")
                continue

            # Perform search
            results = await self._perform_search(query)

            if not results:
                console.print("❌ No results found", style="yellow")
                continue

            # Display results
            await self._display_results(results)

            # Offer to view specific document
            if len(results) > 1:
                choice = Prompt.ask(
                    "\nView document (enter number, or 'continue' for new search)",
                    choices=[str(i) for i in range(1, len(results) + 1)] + ["continue"]
                )

                if choice != "continue":
                    await self._view_document(results[int(choice) - 1])

    async def _perform_search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Perform documentation search."""
        console.print(f"\n🔍 Searching for: '{query}'...", style="blue")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Searching documentation...", total=None)

                results = await self.api_client.search_documentation(query, limit)
                progress.update(task, description=f"Found {len(results)} results")

            return results

        except Exception as e:
            console.print(f"❌ Search failed: {e}", style="red")
            return []

    async def _display_results(self, results: List[Dict[str, Any]]) -> None:
        """Display search results in a formatted table."""
        console.print(f"\n📄 Search Results ({len(results)} found):", style="blue")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("#", style="cyan", width=5)
        table.add_column("Title", style="green")
        table.add_column("Relevance", style="yellow")
        table.add_column("Preview", style="white")

        for i, result in enumerate(results, 1):
            # Extract preview from content
            content = result.get("content", "")
            preview = content[:100] + "..." if len(content) > 100 else content

            # Format relevance score
            relevance = result.get("relevance", 0)
            relevance_text = f"{relevance:.0%}" if relevance else "N/A"

            table.add_row(
                str(i),
                result.get("title", "Untitled"),
                relevance_text,
                preview
            )

        console.print(table)

    async def _view_document(self, document: Dict[str, Any]) -> None:
        """View full document details."""
        doc_id = document.get("id", "unknown")
        title = document.get("title", "Untitled")
        content = document.get("content", "")

        console.print(f"\n📖 {title}", style="bold blue")
        console.print(f"ID: {doc_id}", style="dim")

        # Display content in a scrollable panel
        content_panel = Panel(
            Markdown(content),
            title=title,
            border_style="green",
            expand=False
        )

        console.print(content_panel)

        # Show metadata
        if "metadata" in document:
            console.print("\n📋 Document Metadata:", style="blue")
            metadata = document["metadata"]

            metadata_table = Table(show_header=False, box=None)
            metadata_table.add_column("Key", style="cyan")
            metadata_table.add_column("Value", style="white")

            for key, value in metadata.items():
                metadata_table.add_row(key.replace("_", " ").title(), str(value))

            console.print(metadata_table)

        # Action menu
        while True:
            action = Prompt.ask(
                "\nWhat would you like to do?",
                choices=["back", "export", "related", "done"],
                default="back"
            )

            if action == "back":
                break
            elif action == "export":
                await self._export_document(document)
            elif action == "related":
                await self._find_related_documents(document)
            elif action == "done":
                return

    async def _export_document(self, document: Dict[str, Any]) -> None:
        """Export document to file."""
        filename = Prompt.ask(
            "Enter filename for export",
            default=f"{document.get('title', 'document').replace(' ', '_')}.md"
        )

        try:
            content = f"# {document.get('title', 'Untitled')}\n\n"
            content += f"**ID:** {document.get('id', 'unknown')}\n\n"
            content += document.get("content", "")

            Path(filename).write_text(content, encoding='utf-8')
            console.print(f"✅ Document exported to {filename}", style="green")

        except Exception as e:
            console.print(f"❌ Export failed: {e}", style="red")

    async def _find_related_documents(self, document: Dict[str, Any]) -> None:
        """Find and display related documents."""
        console.print("🔗 Finding related documents...", style="blue")

        # Use document title as search query for related content
        title = document.get("title", "")
        if title:
            related = await self._perform_search(title, limit=5)

            # Remove the current document from results
            current_id = document.get("id", "")
            related = [doc for doc in related if doc.get("id") != current_id]

            if related:
                console.print("\n📚 Related Documents:", style="blue")
                await self._display_results(related)
            else:
                console.print("❌ No related documents found", style="yellow")

    async def upload_documentation(self) -> None:
        """Upload new documentation file."""
        console.print("📤 Upload Documentation", style="bold blue")

        file_path = Prompt.ask("Enter path to documentation file")

        path = Path(file_path)
        if not path.exists():
            console.print(f"❌ File not found: {file_path}", style="red")
            return

        # Get metadata
        console.print("\n📋 Document Metadata:", style="blue")
        title = Prompt.ask("Document title", default=path.stem)
        description = Prompt.ask("Brief description", default="")
        tags = Prompt.ask("Tags (comma-separated)", default="").split(",")

        metadata = {
            "title": title,
            "description": description,
            "tags": [tag.strip() for tag in tags if tag.strip()],
            "uploaded_at": datetime.now().isoformat(),
            "file_type": path.suffix.lower()
        }

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Uploading document...", total=None)

                result = await self.api_client.upload_documentation(path, metadata)
                progress.update(task, description="Upload complete")

            console.print("✅ Documentation uploaded successfully!", style="green")
            console.print(f"Document ID: {result.get('document_id', 'unknown')}", style="cyan")

        except Exception as e:
            console.print(f"❌ Upload failed: {e}", style="red")

    async def browse_categories(self) -> None:
        """Browse documentation by categories."""
        console.print("📂 Browse by Category", style="bold blue")

        # Get popular categories (this would be API-driven)
        categories = [
            "Flow Blockchain",
            "CADENCE Language",
            "Smart Contracts",
            "Token Development",
            "NFT Development",
            "DeFi Protocols",
            "Security Best Practices",
            "Deployment Guides"
        ]

        console.print("\n📚 Available Categories:", style="blue")

        for i, category in enumerate(categories, 1):
            console.print(f"{i}. {category}", style="cyan")

        choice = Prompt.ask("Select category", choices=[str(i) for i in range(1, len(categories) + 1)])

        selected_category = categories[int(choice) - 1]
        console.print(f"\n🔍 Browsing: {selected_category}", style="blue")

        # Search for documents in this category
        results = await self._perform_search(selected_category, limit=10)

        if results:
            await self._display_results(results)
        else:
            console.print("❌ No documents found in this category", style="yellow")

    async def quick_reference(self) -> None:
        """Show quick reference guides."""
        console.print("📖 Quick Reference", style="bold blue")

        quick_refs = {
            "CADENCE Basics": "https://docs.onflow.org/cadence/language/",
            "Flow CLI": "https://docs.onflow.org/flow-cli/",
            "Token Standards": "https://docs.onflow.org/token-contract/",
            "NFT Standards": "https://docs.onflow.org/nft-standard/",
            "Transaction Templates": "https://docs.onflow.org/transaction-templates/",
            "Testing Contracts": "https://docs.onflow.org/testing/",
            "Deployment Guide": "https://docs.onflow.org/deployment/",
            "Security Checklist": "https://docs.onflow.org/security/"
        }

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Topic", style="green")
        table.add_column("Documentation Link", style="cyan")

        for topic, link in quick_refs.items():
            table.add_row(topic, link)

        console.print(table)
        console.print("\n💡 Tip: These links provide official Flow blockchain documentation", style="dim")