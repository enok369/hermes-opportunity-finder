#!/usr/bin/env python3
"""
Hermes Skill: Web Scraper
Discovers opportunities from web sources with continuous scraping.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import asyncio

try:
    import aiohttp
    from bs4 import BeautifulSoup
    import feedparser
except ImportError:
    print("Install: pip install aiohttp beautifulsoup4 feedparser")
    exit(1)


class WebScraperSkill:
    """Asynchronous web scraper for opportunity discovery."""
    
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.cache = {}
    
    async def initialize(self):
        """Start async session."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
    
    async def cleanup(self):
        """Close async session."""
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str, parser: str = "html") -> Optional[Dict]:
        """
        Scrape a single URL and extract content.
        
        Args:
            url: URL to scrape
            parser: "html", "json", or "feed" (RSS/Atom)
        
        Returns:
            Dict with title, content, links, scraped_at
        """
        if not self.session:
            await self.initialize()
        
        try:
            async with self.session.get(url, ssl=False) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}", "url": url}
                
                content = await response.text()
                
                if parser == "feed":
                    return self._parse_feed(url, content)
                elif parser == "json":
                    return {"data": json.loads(content), "url": url, "scraped_at": datetime.now().isoformat()}
                else:  # html
                    return self._parse_html(url, content)
        
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def _parse_html(self, url: str, html: str) -> Dict:
        """Extract useful content from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else "No title"
        
        # Extract main text content
        text_content = soup.get_text(separator="\n", strip=True)[:5000]
        
        # Extract links
        links = [{"href": a.get("href"), "text": a.get_text()} 
                 for a in soup.find_all("a", limit=20) if a.get("href")]
        
        return {
            "url": url,
            "title": title,
            "content": text_content,
            "links": links,
            "scraped_at": datetime.now().isoformat()
        }
    
    def _parse_feed(self, url: str, content: str) -> Dict:
        """Parse RSS/Atom feeds."""
        feed = feedparser.parse(content)
        
        entries = []
        for entry in feed.entries[:20]:  # Last 20 entries
            entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:500],
                "published": entry.get("published", "")
            })
        
        return {
            "url": url,
            "feed_title": feed.feed.get("title", ""),
            "entries": entries,
            "scraped_at": datetime.now().isoformat()
        }
    
    async def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs concurrently."""
        if not self.session:
            await self.initialize()
        
        tasks = [self.scrape_url(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    def get_feeds_to_monitor(self) -> List[str]:
        """Return list of feeds to continuously monitor."""
        return [
            # Add your opportunity feeds here
            "https://news.ycombinator.com/rss",
            "https://producthunt.com/feed",
            # Add more feeds based on your niche
        ]
    
    async def continuous_scrape(self, interval_hours: float = 6):
        """
        Continuously scrape feeds at regular intervals.
        Call this from a Hermes cron task.
        """
        feeds = self.get_feeds_to_monitor()
        
        print(f"Starting continuous scrape of {len(feeds)} feeds every {interval_hours} hours")
        
        while True:
            print(f"\n[{datetime.now().isoformat()}] Scraping feeds...")
            
            results = await self.scrape_multiple(feeds)
            
            # Filter and extract opportunities from results
            opportunities = self._extract_opportunities(results)
            
            if opportunities:
                print(f"Found {len(opportunities)} potential opportunities")
                for opp in opportunities:
                    print(f"  - {opp['title']}")
                    # These will be passed to the filter skill
            
            await asyncio.sleep(interval_hours * 3600)
    
    def _extract_opportunities(self, scrape_results: List[Dict]) -> List[Dict]:
        """
        Extract structured opportunity data from raw scrape results.
        Can be enhanced with ML/NLP later.
        """
        opportunities = []
        
        for result in scrape_results:
            if "error" in result:
                continue
            
            # Parse feed entries or HTML content
            if "entries" in result:
                for entry in result["entries"]:
                    opp = {
                        "source": result["url"],
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", ""),
                        "published": entry.get("published", ""),
                        "discovered_at": datetime.now().isoformat(),
                        "type": "feed"
                    }
                    opportunities.append(opp)
            else:
                # HTML scrape result
                opp = {
                    "source": result["url"],
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:1000],
                    "links": result.get("links", []),
                    "discovered_at": datetime.now().isoformat(),
                    "type": "html"
                }
                opportunities.append(opp)
        
        return opportunities


# Hermes skill interface
async def run_continuous_scrape(interval_hours: float = 6):
    """Entry point for Hermes cron task."""
    scraper = WebScraperSkill()
    await scraper.initialize()
    try:
        await scraper.continuous_scrape(interval_hours)
    finally:
        await scraper.cleanup()


if __name__ == "__main__":
    # Test locally
    async def test():
        scraper = WebScraperSkill()
        await scraper.initialize()
        
        # Test scraping a single URL
        result = await scraper.scrape_url("https://news.ycombinator.com")
        print(json.dumps(result, indent=2, default=str))
        
        await scraper.cleanup()
    
    asyncio.run(test())
