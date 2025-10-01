"""
Firecrawl integration for CLI contract generation.

Provides enhanced documentation search and context gathering using Firecrawl
for improved smart contract generation.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from .api_client import APIClient
from ..services.firecrawl_service import FirecrawlService
from ..services.documentation_service import DocumentationService
from ..models.database import get_db

console = Console()
logger = logging.getLogger(__name__)


class FirecrawlCLIIntegration:
    """Handles Firecrawl integration for CLI operations."""

    def __init__(self, api_client: APIClient, db_session=None):
        self.api_client = api_client
        self.firecrawl_service = FirecrawlService()
        self.db_session = db_session or next(get_db())
        self.documentation_service = DocumentationService(self.db_session)

    def is_available(self) -> bool:
        """Check if Firecrawl service is available."""
        return self.firecrawl_service.is_available()

    async def search_documentation_for_contract(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search documentation using Firecrawl to enhance contract generation context.
        
        Args:
            requirements: Contract requirements including type, functionality, etc.
            
        Returns:
            List of relevant documentation entries
        """
        if not self.is_available():
            console.print("⚠️  Firecrawl service not available. Using local documentation only.", style="yellow")
            return []

        try:
            # Extract search terms from requirements
            search_terms = self._extract_search_terms(requirements)
            
            console.print(f"🔍 Searching documentation for: {', '.join(search_terms)}", style="blue")
            
            # Search existing indexed documentation first
            local_results = await self._search_local_documentation(search_terms)
            
            # If we have good local results, use them
            if len(local_results) >= 3:
                console.print(f"✅ Found {len(local_results)} relevant documentation entries locally", style="green")
                return local_results[:5]  # Return top 5 results
            
            # Otherwise, try to find and crawl additional sources
            console.print("🌐 Searching for additional documentation sources...", style="blue")
            additional_sources = await self._find_additional_sources(search_terms)
            
            if additional_sources:
                crawled_content = await self._crawl_additional_sources(additional_sources)
                local_results.extend(crawled_content)
            
            return local_results[:5]  # Return top 5 results
            
        except Exception as e:
            logger.error(f"Error searching documentation: {e}")
            console.print(f"❌ Error searching documentation: {e}", style="red")
            return []

    def _extract_search_terms(self, requirements: Dict[str, Any]) -> List[str]:
        """Extract relevant search terms from contract requirements."""
        terms = []
        
        # Add contract type
        if contract_type := requirements.get("type"):
            terms.append(contract_type.lower())
        
        # Add functionality keywords
        if functionality := requirements.get("functionality"):
            # Extract keywords from functionality description
            keywords = [
                "token", "nft", "fungible", "non-fungible", "marketplace", 
                "staking", "governance", "defi", "swap", "liquidity",
                "vault", "collection", "metadata", "royalty", "access control"
            ]
            func_lower = functionality.lower()
            terms.extend([kw for kw in keywords if kw in func_lower])
        
        # Add specific features
        if features := requirements.get("features"):
            if isinstance(features, list):
                terms.extend([f.lower() for f in features])
            elif isinstance(features, str):
                terms.append(features.lower())
        
        # Add network-specific terms
        if network := requirements.get("network"):
            terms.extend(["flow", "cadence", network.lower()])
        else:
            terms.extend(["flow", "cadence"])
        
        return list(set(terms))  # Remove duplicates

    async def _search_local_documentation(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Search locally indexed documentation."""
        try:
            results = []
            for term in search_terms[:3]:  # Limit to top 3 terms to avoid too many queries
                search_result = self.documentation_service.search_documentation(
                    query=term,
                    limit=3,
                    min_score=0.7
                )
                
                if search_result.get("success") and search_result.get("results"):
                    results.extend(search_result["results"])
            
            # Remove duplicates based on URL or title
            seen = set()
            unique_results = []
            for result in results:
                identifier = result.get("url") or result.get("title", "")
                if identifier and identifier not in seen:
                    seen.add(identifier)
                    unique_results.append(result)
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Error searching local documentation: {e}")
            return []

    async def _find_additional_sources(self, search_terms: List[str]) -> List[str]:
        """Find additional documentation sources that might be relevant."""
        # Predefined high-quality Flow/Cadence documentation sources
        potential_sources = [
            "https://cadence-lang.org/docs/",
            "https://developers.flow.com/",
            "https://docs.onflow.org/",
            "https://github.com/onflow/flow-core-contracts",
            "https://github.com/onflow/cadence",
        ]
        
        # For now, return predefined sources
        # In the future, this could use web search APIs to find more sources
        return potential_sources[:2]  # Limit to avoid excessive crawling

    async def _crawl_additional_sources(self, sources: List[str]) -> List[Dict[str, Any]]:
        """Crawl additional documentation sources."""
        crawled_content = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Crawling documentation sources...", total=len(sources))
            
            for source in sources:
                try:
                    progress.update(task, description=f"Crawling {source}")
                    
                    # Scrape the source
                    result = self.firecrawl_service.scrape_url(
                        url=source,
                        formats=['markdown'],
                        only_main_content=True,
                        timeout=10000
                    )
                    
                    if result and result.get("status") == "success":
                        data = result.get("data", {})
                        if data.get("markdown") and len(data["markdown"]) > 100:
                            crawled_content.append({
                                "title": data.get("title", source),
                                "content": data["markdown"][:2000],  # Limit content length
                                "url": source,
                                "source": "firecrawl_realtime",
                                "relevance_score": 0.8  # Default score for crawled content
                            })
                            
                            # Optionally index this content for future use
                            await self._index_crawled_content(data, source)
                    
                    progress.advance(task)
                    
                except Exception as e:
                    logger.error(f"Error crawling {source}: {e}")
                    progress.advance(task)
                    continue
        
        return crawled_content

    async def _index_crawled_content(self, data: Dict[str, Any], url: str):
        """Index crawled content for future searches."""
        try:
            # Use the documentation service to index the content
            index_result = self.documentation_service.index_content(
                title=data.get("title", url),
                content=data.get("markdown", ""),
                url=url,
                source="FIRECRAWL_REALTIME",
                content_type="DOCUMENTATION"
            )
            
            if index_result.get("success"):
                logger.info(f"Successfully indexed content from {url}")
            
        except Exception as e:
            logger.error(f"Error indexing content from {url}: {e}")

    async def crawl_custom_documentation(self, url: str) -> Dict[str, Any]:
        """
        Crawl a custom documentation URL provided by the user.
        
        Args:
            url: URL to crawl
            
        Returns:
            Crawl result with success status and data
        """
        if not self.is_available():
            return {"success": False, "error": "Firecrawl service not available"}

        try:
            console.print(f"🌐 Crawling documentation from: {url}", style="blue")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("Crawling documentation..."),
                console=console
            ) as progress:
                task = progress.add_task("Crawling...", total=None)
                
                result = self.firecrawl_service.scrape_url(
                    url=url,
                    formats=['markdown', 'html'],
                    only_main_content=True,
                    timeout=15000
                )
                
                progress.stop()
            
            if result and result.get("status") == "success":
                data = result.get("data", {})
                
                # Display preview of crawled content
                self._display_crawled_content_preview(data, url)
                
                # Ask if user wants to index this content
                if Confirm.ask("Would you like to index this content for future searches?"):
                    await self._index_crawled_content(data, url)
                    console.print("✅ Content indexed successfully", style="green")
                
                return {
                    "success": True,
                    "data": data,
                    "url": url,
                    "title": data.get("title", ""),
                    "content_length": len(data.get("markdown", ""))
                }
            else:
                error_msg = result.get("error", "Failed to crawl URL") if result else "No data returned"
                console.print(f"❌ Failed to crawl {url}: {error_msg}", style="red")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            logger.error(f"Error crawling custom documentation: {e}")
            console.print(f"❌ Error crawling documentation: {e}", style="red")
            return {"success": False, "error": str(e)}

    def _display_crawled_content_preview(self, data: Dict[str, Any], url: str):
        """Display a preview of crawled content."""
        title = data.get("title", "Untitled")
        content = data.get("markdown", "")
        
        # Create preview table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan", width=15)
        table.add_column("Value", style="white")
        
        table.add_row("URL", url)
        table.add_row("Title", title)
        table.add_row("Content Length", f"{len(content)} characters")
        
        # Show content preview
        preview = content[:300] + "..." if len(content) > 300 else content
        
        console.print(Panel(table, title="📄 Crawled Content", border_style="blue"))
        
        if preview:
            console.print(Panel(
                Markdown(preview),
                title="📖 Content Preview",
                border_style="dim"
            ))

    async def interactive_documentation_search(self) -> Optional[List[Dict[str, Any]]]:
        """
        Interactive documentation search for contract generation.
        
        Returns:
            List of selected documentation entries or None if cancelled
        """
        console.print("📚 Documentation Search for Contract Generation", style="bold blue")
        console.print("Search for relevant documentation to enhance your contract generation.", style="dim")
        
        search_options = [
            "Search existing documentation",
            "Crawl a specific URL",
            "Use predefined Flow/Cadence docs",
            "Skip documentation search"
        ]
        
        # Display options
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan", width=5)
        table.add_column("Description", style="white")
        
        for i, option in enumerate(search_options, 1):
            table.add_row(str(i), option)
        
        console.print(table)
        
        choice = Prompt.ask(
            "Select search option",
            choices=[str(i) for i in range(1, len(search_options) + 1)],
            default="1"
        )
        
        if choice == "1":
            return await self._interactive_existing_search()
        elif choice == "2":
            return await self._interactive_url_crawl()
        elif choice == "3":
            return await self._use_predefined_docs()
        else:
            console.print("⏭️  Skipping documentation search", style="yellow")
            return None

    async def _interactive_existing_search(self) -> List[Dict[str, Any]]:
        """Interactive search of existing documentation."""
        query = Prompt.ask("Enter search terms (e.g., 'NFT collection', 'token contract')")
        
        if not query.strip():
            return []
        
        console.print(f"🔍 Searching for: {query}", style="blue")
        
        search_result = self.documentation_service.search_documentation(
            query=query,
            limit=10,
            min_score=0.6
        )
        
        if not search_result.get("success") or not search_result.get("results"):
            console.print("❌ No relevant documentation found", style="red")
            return []
        
        results = search_result["results"]
        
        # Display results for selection
        table = Table(show_header=True, box=None)
        table.add_column("ID", style="cyan", width=3)
        table.add_column("Title", style="white", width=40)
        table.add_column("Source", style="dim", width=20)
        table.add_column("Score", style="green", width=8)
        
        for i, result in enumerate(results, 1):
            table.add_row(
                str(i),
                result.get("title", "Untitled")[:37] + "..." if len(result.get("title", "")) > 40 else result.get("title", ""),
                result.get("source", "Unknown"),
                f"{result.get('relevance_score', 0):.2f}"
            )
        
        console.print(table)
        
        # Allow multiple selection
        selections = Prompt.ask(
            "Select documentation entries (comma-separated, e.g., '1,3,5')",
            default="1"
        )
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in selections.split(",")]
            selected_results = [results[i] for i in selected_indices if 0 <= i < len(results)]
            
            console.print(f"✅ Selected {len(selected_results)} documentation entries", style="green")
            return selected_results
            
        except (ValueError, IndexError):
            console.print("❌ Invalid selection. Using first result.", style="yellow")
            return [results[0]] if results else []

    async def _interactive_url_crawl(self) -> List[Dict[str, Any]]:
        """Interactive URL crawling."""
        url = Prompt.ask("Enter documentation URL to crawl")
        
        if not url.strip():
            return []
        
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        result = await self.crawl_custom_documentation(url)
        
        if result.get("success"):
            return [{
                "title": result.get("title", url),
                "content": result["data"].get("markdown", ""),
                "url": url,
                "source": "firecrawl_custom",
                "relevance_score": 0.9
            }]
        else:
            return []

    async def _use_predefined_docs(self) -> List[Dict[str, Any]]:
        """Use predefined Flow/Cadence documentation."""
        console.print("📖 Using predefined Flow/Cadence documentation", style="blue")
        
        # Trigger Cadence documentation crawl if needed
        crawl_result = self.documentation_service.crawl_and_index_cadence_docs(force_refresh=False)
        
        if crawl_result.get("success"):
            # Search for general Flow/Cadence content
            search_result = self.documentation_service.search_documentation(
                query="cadence contract flow",
                limit=5,
                min_score=0.5
            )
            
            if search_result.get("success") and search_result.get("results"):
                console.print(f"✅ Found {len(search_result['results'])} predefined documentation entries", style="green")
                return search_result["results"]
        
        console.print("⚠️  No predefined documentation available", style="yellow")
        return []