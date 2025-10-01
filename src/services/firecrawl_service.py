"""
Firecrawl service for web crawling and scraping documentation.
"""

import os
import logging
import time
import random
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from enum import Enum

from ..config import get_settings

logger = logging.getLogger(__name__)

# Try to import Firecrawl
try:
    from firecrawl import Firecrawl
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    logger.warning("Firecrawl not available. Install with: pip install firecrawl-py")


class CrawlStatus(str, Enum):
    """Crawl job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FirecrawlService:
    """Service for web crawling and scraping using Firecrawl."""

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Firecrawl client."""
        if not FIRECRAWL_AVAILABLE:
            logger.error("Firecrawl SDK not available")
            return

        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            logger.error("FIRECRAWL_API_KEY not found in environment variables")
            return

        try:
            self.client = Firecrawl(api_key=api_key)
            logger.info("Firecrawl client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Firecrawl service is available."""
        return FIRECRAWL_AVAILABLE and self.client is not None

    def _is_rate_limit_error(self, error_message: str) -> bool:
        """Check if the error is a rate limit error."""
        rate_limit_indicators = [
            "rate limit exceeded",
            "rate limit",
            "too many requests",
            "429"
        ]
        error_lower = str(error_message).lower()
        return any(indicator in error_lower for indicator in rate_limit_indicators)

    def _extract_retry_after(self, error_message: str) -> int:
        """Extract retry-after time from error message."""
        # Look for patterns like "retry after 3s" or "resets at"
        import re
        
        # Try to find "retry after Xs" pattern
        retry_match = re.search(r'retry after (\d+)s', str(error_message))
        if retry_match:
            return int(retry_match.group(1))
        
        # Default to 60 seconds if we can't parse the retry time
        return 60

    def _retry_with_backoff(self, func, *args, max_retries: int = 3, **kwargs):
        """
        Retry a function with exponential backoff for rate limit errors.
        
        Args:
            func: Function to retry
            *args: Function arguments
            max_retries: Maximum number of retries
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or raises the last exception
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                error_message = str(e)
                
                if self._is_rate_limit_error(error_message):
                    if attempt < max_retries:
                        # Calculate wait time
                        if attempt == 0:
                            # First retry: use the time from error message or default
                            wait_time = self._extract_retry_after(error_message)
                        else:
                            # Exponential backoff with jitter
                            base_wait = 2 ** attempt
                            jitter = random.uniform(0.5, 1.5)
                            wait_time = int(base_wait * jitter)
                        
                        logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}). Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Max retries ({max_retries}) exceeded for rate limit error")
                        raise e
                else:
                    # Not a rate limit error, don't retry
                    raise e
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception

    def scrape_url(
        self,
        url: str,
        formats: Optional[List[str]] = None,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        only_main_content: bool = True,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a single URL.
        
        Args:
            url: URL to scrape
            formats: Output formats (e.g., ['markdown', 'html'])
            include_tags: HTML tags to include
            exclude_tags: HTML tags to exclude
            only_main_content: Extract only main content
            timeout: Request timeout in milliseconds
            
        Returns:
            Scraped data or None if failed
        """
        if not self.is_available():
            logger.error("Firecrawl service not available")
            return None

        try:
            # Set default formats
            if formats is None:
                formats = ['markdown', 'html']

            # Prepare scrape options
            scrape_options = {
                'formats': formats,
                'only_main_content': only_main_content
            }

            if include_tags:
                scrape_options['includeTags'] = include_tags
            if exclude_tags:
                scrape_options['excludeTags'] = exclude_tags
            if timeout:
                scrape_options['timeout'] = timeout

            logger.info(f"Scraping URL: {url}")
            
            # Use retry logic for rate limiting
            def _scrape():
                return self.client.scrape(url, **scrape_options)
            
            result = self._retry_with_backoff(_scrape, max_retries=3)

            if result:
                logger.info(f"Successfully scraped {url}")
                
                # Convert Document object to dictionary
                data = {}
                if hasattr(result, 'markdown'):
                    data['markdown'] = result.markdown
                if hasattr(result, 'html'):
                    data['html'] = result.html
                if hasattr(result, 'metadata'):
                    # Convert metadata object to dictionary
                    if hasattr(result.metadata, '__dict__'):
                        data['metadata'] = result.metadata.__dict__
                    else:
                        data['metadata'] = {}
                if hasattr(result, 'extract'):
                    data['extract'] = result.extract
                
                return {
                    'url': url,
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'data': data,
                    'status': 'success'
                }
            else:
                logger.warning(f"No data returned for {url}")
                return None

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'status': 'failed'
            }

    def crawl_website(
        self,
        url: str,
        limit: int = 100,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        formats: Optional[List[str]] = None,
        only_main_content: bool = True,
        wait_for: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Crawl an entire website.
        
        Args:
            url: Base URL to crawl
            limit: Maximum number of pages to crawl
            include_paths: URL patterns to include
            exclude_paths: URL patterns to exclude
            formats: Output formats (e.g., ['markdown', 'html'])
            only_main_content: Extract only main content
            wait_for: Wait time for page loading (milliseconds)
            timeout: Request timeout per page (milliseconds)
            
        Returns:
            Crawl results or None if failed
        """
        if not self.is_available():
            logger.error("Firecrawl service not available")
            return None

        try:
            # Set default formats
            if formats is None:
                formats = ['markdown', 'html']

            # Prepare crawl options
            crawl_options = {
                'limit': limit,
                'scrape_options': {
                    'formats': formats,
                    'only_main_content': only_main_content
                }
            }

            if include_paths:
                crawl_options['includePaths'] = include_paths
            if exclude_paths:
                crawl_options['excludePaths'] = exclude_paths
            if wait_for:
                crawl_options['scrape_options']['waitFor'] = wait_for
            if timeout:
                crawl_options['scrape_options']['timeout'] = timeout

            logger.info(f"Starting crawl of {url} with limit {limit}")
            
            # Use retry logic for rate limiting
            def _crawl():
                return self.client.crawl(url, **crawl_options)
            
            try:
                result = self._retry_with_backoff(_crawl, max_retries=3)
            except Exception as e:
                error_msg = str(e).lower()
                if 'insufficient credits' in error_msg or 'payment required' in error_msg:
                    logger.info(f"Crawl failed due to insufficient credits, falling back to scraping {url}")
                    scrape_result = self.scrape_url(url, formats=formats, only_main_content=only_main_content, timeout=timeout)
                    if scrape_result and scrape_result.get('status') == 'success':
                        return {
                            'url': url,
                            'crawled_at': datetime.now(timezone.utc).isoformat(),
                            'data': [scrape_result['data']],
                            'status': 'success',
                            'page_count': 1
                        }
                raise e

            if result:
                # Extract data from the crawl response
                crawl_data = []
                if hasattr(result, 'data') and result.data:
                    crawl_data = result.data
                elif hasattr(result, '__dict__') and 'data' in result.__dict__:
                    crawl_data = result.__dict__['data']
                
                # If crawl returned no data, fall back to scraping the original URL
                if not crawl_data:
                    logger.info(f"Crawl returned no data for {url}, falling back to scraping")
                    scrape_result = self.scrape_url(url, formats=formats, only_main_content=only_main_content, timeout=timeout)
                    if scrape_result and scrape_result.get('status') == 'success' and 'data' in scrape_result:
                        crawl_data = [scrape_result['data']]
                
                # Convert Document objects to dictionaries
                processed_data = []
                for doc in crawl_data:
                    if isinstance(doc, dict):
                        # Already a dictionary
                        processed_data.append(doc)
                    else:
                        # Convert object to dictionary
                        doc_data = {}
                        if hasattr(doc, 'markdown'):
                            doc_data['markdown'] = doc.markdown
                        if hasattr(doc, 'html'):
                            doc_data['html'] = doc.html
                        if hasattr(doc, 'metadata'):
                            doc_data['metadata'] = doc.metadata
                        if hasattr(doc, 'extract'):
                            doc_data['extract'] = doc.extract
                        processed_data.append(doc_data)
                
                logger.info(f"Successfully crawled {url}, found {len(processed_data)} pages")
                return {
                    'url': url,
                    'crawled_at': datetime.now(timezone.utc).isoformat(),
                    'data': processed_data,
                    'status': 'success',
                    'page_count': len(processed_data)
                }
            else:
                logger.warning(f"No data returned for crawl of {url}")
                return None

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return {
                'url': url,
                'crawled_at': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'status': 'failed'
            }

    def crawl_cadence_documentation(self) -> Dict[str, Any]:
        """
        Crawl Cadence documentation sites.
        
        Returns:
            Combined results from all Cadence documentation sources
        """
        cadence_urls = [
            "https://cadence-lang.org/docs/",
            "https://cadence-lang.org/docs/cadence-migration-guide"
        ]

        results = {
            'crawled_at': datetime.now(timezone.utc).isoformat(),
            'sources': {},
            'total_pages': 0,
            'successful_crawls': 0,
            'failed_crawls': 0
        }

        for url in cadence_urls:
            logger.info(f"Crawling Cadence documentation: {url}")
            
            # Special handling for Cadence docs with navigation sidebar
            crawl_result = self.crawl_website(
                url=url,
                limit=50,  # Reasonable limit for documentation
                formats=['markdown', 'html'],
                only_main_content=False,  # Include navigation for link discovery
                wait_for=2000,  # Wait 2 seconds for JS to load
                timeout=15000   # 15 second timeout per page
            )

            if crawl_result and crawl_result.get('status') == 'success':
                results['sources'][url] = crawl_result
                results['total_pages'] += crawl_result.get('page_count', 0)
                results['successful_crawls'] += 1
                logger.info(f"Successfully crawled {url}")
            else:
                results['sources'][url] = crawl_result or {'status': 'failed', 'error': 'No result returned'}
                results['failed_crawls'] += 1
                logger.error(f"Failed to crawl {url}")

        logger.info(f"Cadence documentation crawl completed: {results['successful_crawls']} successful, {results['failed_crawls']} failed")
        return results

    def extract_navigation_links(self, html_content: str) -> List[str]:
        """
        Extract navigation links from HTML content.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of extracted URLs
        """
        import re
        from urllib.parse import urljoin, urlparse

        # Look for navigation with the specific class mentioned by user
        nav_pattern = r'<nav[^>]*class="[^"]*menu thin-scrollbar menu_SIkG[^"]*"[^>]*>(.*?)</nav>'
        nav_matches = re.findall(nav_pattern, html_content, re.DOTALL | re.IGNORECASE)

        links = []
        for nav_content in nav_matches:
            # Extract href attributes from anchor tags
            link_pattern = r'href="([^"]+)"'
            href_matches = re.findall(link_pattern, nav_content)
            links.extend(href_matches)

        # Filter and clean links
        cleaned_links = []
        for link in links:
            # Skip anchors, external links, and non-documentation links
            if link.startswith('#') or link.startswith('http') and 'cadence-lang.org' not in link:
                continue
            
            # Convert relative links to absolute
            if link.startswith('/'):
                link = f"https://cadence-lang.org{link}"
            elif not link.startswith('http'):
                link = f"https://cadence-lang.org/docs/{link}"
                
            cleaned_links.append(link)

        return list(set(cleaned_links))  # Remove duplicates

    def get_crawl_status(self, crawl_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a crawl job.
        
        Args:
            crawl_id: ID of the crawl job
            
        Returns:
            Crawl status information
        """
        if not self.is_available():
            logger.error("Firecrawl service not available")
            return None

        try:
            status = self.client.get_crawl_status(crawl_id)
            return status
        except Exception as e:
            logger.error(f"Error getting crawl status for {crawl_id}: {e}")
            return None