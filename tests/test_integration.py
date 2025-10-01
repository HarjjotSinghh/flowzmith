#!/usr/bin/env python3
"""
Integration test script for Firecrawl and DocumentationService.

This script tests:
1. Firecrawl service availability
2. DocumentationService integration
3. Cadence documentation crawling and indexing
4. API endpoints functionality
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up environment
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_integration.db")
os.environ.setdefault("VECTOR_DB_PATH", "./test_vector_db")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Base
from src.services.documentation_service import DocumentationService
from src.services.firecrawl_service import FirecrawlService
# Import all models to ensure they're registered with Base.metadata
from src.models import (
    DocumentationKnowledgeBase, ContentType, User, ContractSubmission, 
    GeneratedContract, DeploymentLog, LearningFeedbackLoop, CLILog
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTester:
    """Integration test runner for Firecrawl and DocumentationService."""
    
    def __init__(self):
        """Initialize the test environment."""
        self.engine = create_engine("sqlite:///./test_integration.db")
        
        # Log available tables before creation
        logger.info(f"Available tables in metadata: {list(Base.metadata.tables.keys())}")
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
        
        # Verify tables were created
        from sqlalchemy import text
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Tables created in database: {tables}")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db_session = SessionLocal()
        
        self.firecrawl_service = FirecrawlService()
        self.documentation_service = DocumentationService(self.db_session)
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
    
    def test_firecrawl_availability(self) -> bool:
        """Test if Firecrawl service is available."""
        logger.info("Testing Firecrawl service availability...")
        
        try:
            is_available = self.firecrawl_service.is_available()
            self.test_results["tests"]["firecrawl_availability"] = {
                "success": is_available,
                "message": "Firecrawl service is available" if is_available else "Firecrawl service unavailable"
            }
            
            if is_available:
                logger.info("✅ Firecrawl service is available")
            else:
                logger.warning("❌ Firecrawl service is not available")
            
            return is_available
            
        except Exception as e:
            logger.error(f"❌ Error checking Firecrawl availability: {e}")
            self.test_results["tests"]["firecrawl_availability"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def test_single_page_scraping(self) -> bool:
        """Test scraping a single page."""
        logger.info("Testing single page scraping...")
        
        test_url = "https://cadence-lang.org/docs/"
        
        try:
            result = self.documentation_service.scrape_single_page(test_url)
            
            success = result.get("success", False)
            if success:
                data = result.get("data", {})
                content_length = len(data.get("markdown", ""))
                title = data.get("metadata", {}).get("title", "Unknown")
                
                self.test_results["tests"]["single_page_scraping"] = {
                    "success": True,
                    "url": test_url,
                    "title": title,
                    "content_length": content_length,
                    "message": f"Successfully scraped {content_length} characters"
                }
                
                logger.info(f"✅ Successfully scraped page: {title} ({content_length} chars)")
                return True
            else:
                error = result.get("error", "Unknown error")
                self.test_results["tests"]["single_page_scraping"] = {
                    "success": False,
                    "url": test_url,
                    "error": error
                }
                logger.error(f"❌ Failed to scrape page: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during single page scraping: {e}")
            self.test_results["tests"]["single_page_scraping"] = {
                "success": False,
                "url": test_url,
                "error": str(e)
            }
            return False
    
    def test_cadence_documentation_crawling(self) -> bool:
        """Test crawling and indexing Cadence documentation."""
        logger.info("Testing Cadence documentation crawling and indexing...")
        
        try:
            # Get initial document count
            initial_count = self.db_session.query(DocumentationKnowledgeBase).count()
            
            # Perform crawl and indexing
            result = self.documentation_service.crawl_and_index_cadence_docs(force_refresh=True)
            
            success = result.get("success", False)
            if success:
                pages_indexed = result.get("pages_indexed", 0)
                pages_failed = result.get("pages_failed", 0)
                total_pages = result.get("total_pages", 0)
                
                # Get final document count
                final_count = self.db_session.query(DocumentationKnowledgeBase).count()
                new_docs = final_count - initial_count
                
                self.test_results["tests"]["cadence_documentation_crawling"] = {
                    "success": True,
                    "pages_indexed": pages_indexed,
                    "pages_failed": pages_failed,
                    "total_pages": total_pages,
                    "new_documents": new_docs,
                    "message": f"Indexed {pages_indexed} pages, {pages_failed} failed"
                }
                
                logger.info(f"✅ Successfully crawled Cadence docs: {pages_indexed} indexed, {pages_failed} failed")
                logger.info(f"   Total new documents in database: {new_docs}")
                return True
            else:
                error = result.get("error", "Unknown error")
                self.test_results["tests"]["cadence_documentation_crawling"] = {
                    "success": False,
                    "error": error
                }
                logger.error(f"❌ Failed to crawl Cadence documentation: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during Cadence documentation crawling: {e}")
            self.test_results["tests"]["cadence_documentation_crawling"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def test_documentation_search(self) -> bool:
        """Test searching the indexed documentation."""
        logger.info("Testing documentation search...")
        
        try:
            # Test search for common Cadence terms
            search_terms = ["resource", "capability", "transaction", "account"]
            search_results = {}
            
            for term in search_terms:
                results = self.documentation_service.search_documentation(term, limit=5)
                search_results[term] = {
                    "count": len(results),
                    "titles": [doc.title for doc in results[:3]]  # First 3 titles
                }
            
            total_results = sum(result["count"] for result in search_results.values())
            
            self.test_results["tests"]["documentation_search"] = {
                "success": True,
                "search_terms": search_terms,
                "results": search_results,
                "total_results": total_results,
                "message": f"Found {total_results} total results across {len(search_terms)} search terms"
            }
            
            logger.info(f"✅ Documentation search successful: {total_results} total results")
            for term, result in search_results.items():
                logger.info(f"   '{term}': {result['count']} results")
            
            return total_results > 0
            
        except Exception as e:
            logger.error(f"❌ Error during documentation search: {e}")
            self.test_results["tests"]["documentation_search"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def test_content_indexing(self) -> bool:
        """Test manual content indexing."""
        logger.info("Testing manual content indexing...")
        
        try:
            test_content = """
            # Test Documentation
            
            This is a test document for verifying the content indexing functionality.
            
            ## Features
            - Content indexing
            - Search functionality
            - Vector embeddings
            
            ## Example Code
            ```cadence
            pub contract TestContract {
                pub fun hello(): String {
                    return "Hello, World!"
                }
            }
            ```
            """
            
            # Index the test content
            doc_entry = self.documentation_service.index_scraped_content(
                url="https://test.example.com/test-doc",
                title="Test Documentation",
                content=test_content,
                source="CUSTOM_DOCUMENTATION"
            )
            
            self.test_results["tests"]["content_indexing"] = {
                "success": True,
                "document_id": str(doc_entry.id),  # Convert UUID to string for JSON serialization
                "title": doc_entry.title,
                "content_length": len(test_content),
                "message": "Successfully indexed test content"
            }
            
            logger.info(f"✅ Successfully indexed test content (ID: {str(doc_entry.id)})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during content indexing: {e}")
            self.test_results["tests"]["content_indexing"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def test_documentation_stats(self) -> bool:
        """Test getting documentation statistics."""
        logger.info("Testing documentation statistics...")
        
        try:
            stats = self.documentation_service.get_documentation_stats()
            
            self.test_results["tests"]["documentation_stats"] = {
                "success": True,
                "stats": stats,
                "message": f"Retrieved stats for {stats.get('total_documents', 0)} documents"
            }
            
            logger.info(f"✅ Documentation stats retrieved:")
            logger.info(f"   Total documents: {stats.get('total_documents', 0)}")
            logger.info(f"   Vector search enabled: {stats.get('vector_search_enabled', False)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error getting documentation stats: {e}")
            self.test_results["tests"]["documentation_stats"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def run_all_tests(self) -> bool:
        """Run all integration tests."""
        logger.info("🚀 Starting Firecrawl integration tests...")
        
        tests = [
            ("Firecrawl Availability", self.test_firecrawl_availability),
            ("Single Page Scraping", self.test_single_page_scraping),
            ("Cadence Documentation Crawling", self.test_cadence_documentation_crawling),
            ("Documentation Search", self.test_documentation_search),
            ("Content Indexing", self.test_content_indexing),
            ("Documentation Stats", self.test_documentation_stats),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                    logger.info(f"✅ {test_name} PASSED")
                else:
                    logger.error(f"❌ {test_name} FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name} ERROR: {e}")
        
        # Summary
        logger.info(f"\n{'='*50}")
        logger.info(f"INTEGRATION TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Passed: {passed}/{total}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        self.test_results["summary"] = {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": (passed/total)*100
        }
        
        # Save results
        with open("integration_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Test results saved to: integration_test_results.json")
        
        return passed == total
    
    def cleanup(self):
        """Clean up test resources."""
        try:
            self.db_session.close()
            # Remove test database
            if os.path.exists("test_integration.db"):
                os.remove("test_integration.db")
            logger.info("✅ Test cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")


def main():
    """Main test runner."""
    tester = IntegrationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            logger.info("🎉 All integration tests passed!")
            sys.exit(0)
        else:
            logger.error("💥 Some integration tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during testing: {e}")
        sys.exit(1)
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()