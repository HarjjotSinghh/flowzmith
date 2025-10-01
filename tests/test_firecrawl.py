#!/usr/bin/env python3
"""
Test script for Firecrawl service integration.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our FirecrawlService
try:
    from src.services.firecrawl_service import FirecrawlService, CrawlStatus
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    print("Firecrawl service not available")


def test_firecrawl_service():
    """Test the FirecrawlService functionality."""
    print("🔥 Testing Firecrawl Service Integration")
    print("=" * 50)
    
    # Initialize service
    service = FirecrawlService()
    
    # Check if service is available
    if not service.is_available():
        print("❌ Firecrawl service not available")
        print("Please check:")
        print("1. FIRECRAWL_API_KEY is set in .env")
        print("2. firecrawl-py is installed: pip install firecrawl-py")
        return False
    
    print("✅ Firecrawl service initialized successfully")
    
    # Test single URL scraping
    print("\n📄 Testing single URL scraping...")
    test_url = "https://cadence-lang.org/docs/"
    scrape_result = service.scrape_url(
        url=test_url,
        formats=['markdown'],
        only_main_content=True,
        timeout=30000  # Increased timeout to 30 seconds
    )
    
    if scrape_result and scrape_result.get('status') == 'success':
        print(f"✅ Successfully scraped {test_url}")
        print(f"   Data keys: {list(scrape_result.get('data', {}).keys())}")
        
        # Show a snippet of the markdown content
        markdown_content = scrape_result.get('data', {}).get('markdown', '')
        if markdown_content:
            snippet = markdown_content[:200] + "..." if len(markdown_content) > 200 else markdown_content
            print(f"   Content snippet: {snippet}")
    else:
        print(f"❌ Failed to scrape {test_url}")
        if scrape_result:
            print(f"   Error: {scrape_result.get('error', 'Unknown error')}")
        return False
    
    # Test website crawling
    print("\n🕷️ Testing website crawling...")
    crawl_result = service.crawl_website(
        url="https://cadence-lang.org/docs/",
        limit=5,  # Small limit for testing
        formats=['markdown'],
        only_main_content=True,
        timeout=30000  # Increased timeout to 30 seconds
    )
    
    if crawl_result and crawl_result.get('status') == 'success':
        page_count = crawl_result.get('page_count', 0)
        print(f"✅ Successfully crawled website, found {page_count} pages")
        
        # Show first page info
        pages = crawl_result.get('data', [])
        if pages:
            first_page = pages[0]
            if 'metadata' in first_page and first_page['metadata']:
                title = first_page['metadata'].get('title', 'No title')
                print(f"   First page: {title}")
    else:
        print("❌ Failed to crawl website")
        if crawl_result:
            print(f"   Error: {crawl_result.get('error', 'Unknown error')}")
        return False
    
    # Test Cadence documentation crawling
    print("\n📚 Testing Cadence documentation crawling...")
    cadence_result = service.crawl_cadence_documentation()
    
    if cadence_result:
        successful = cadence_result.get('successful_crawls', 0)
        failed = cadence_result.get('failed_crawls', 0)
        total_pages = cadence_result.get('total_pages', 0)
        
        print(f"✅ Cadence documentation crawl completed:")
        print(f"   Successful crawls: {successful}")
        print(f"   Failed crawls: {failed}")
        print(f"   Total pages: {total_pages}")
        
        if successful > 0:
            print("✅ At least one Cadence documentation source was successfully crawled")
        else:
            print("⚠️ No Cadence documentation sources were successfully crawled")
    else:
        print("❌ Failed to crawl Cadence documentation")
        return False
    
    print("\n🎉 All Firecrawl tests passed!")
    return True


if __name__ == "__main__":
    success = test_firecrawl_service()
    if success:
        print("\n🎉 Firecrawl integration test completed!")
    else:
        print("\n💥 Firecrawl integration test failed!")
        sys.exit(1)