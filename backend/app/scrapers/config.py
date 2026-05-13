"""
Scraper Configuration
Centralized configuration for all scrapers
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ScraperConfig:
    """Configuration for a single scraper"""
    name: str
    enabled: bool = True
    max_pages: int = 1
    timeout: int = 30000
    retry_attempts: int = 3
    backoff_factor: float = 2.0
    human_delay_min: int = 500
    human_delay_max: int = 2000
    scroll_count: int = 3


class ScraperRegistry:
    """Registry of all available scrapers"""
    
    @staticmethod
    def get_available_scrapers() -> Dict[str, type]:
        """Get all available scraper classes."""
        from app.scrapers.jobstreet import JobstreetScraper
        from app.scrapers.glints_v2 import GlintsScraper
        from app.scrapers.kalibrr_v2 import KalibrrScraper
        from app.scrapers.dealls_v2 import DeallsScraper

        return {
            "Jobstreet": JobstreetScraper,
            "Glints": GlintsScraper,
            "Kalibrr": KalibrrScraper,
            "Dealls": DeallsScraper
        }
    
    @staticmethod
    def get_scraper(name: str):
        """Get scraper instance by name"""
        scrapers = ScraperRegistry.get_available_scrapers()
        scraper_class = scrapers.get(name)
        
        if not scraper_class:
            raise ValueError(f"Unknown scraper: {name}")
        
        return scraper_class()
    
    @staticmethod
    def get_all_scrapers() -> List:
        """Get all scraper instances"""
        scrapers = ScraperRegistry.get_available_scrapers()
        return [scraper_class() for scraper_class in scrapers.values()]


# Default configurations for each scraper
DEFAULT_CONFIGS = {
    "Jobstreet": ScraperConfig(
        name="Jobstreet",
        enabled=True,
        max_pages=2,
        timeout=30000,
        retry_attempts=3,
        scroll_count=2
    ),
    "Glints": ScraperConfig(
        name="Glints",
        enabled=True,
        max_pages=2,
        timeout=30000,
        retry_attempts=3,
        scroll_count=4,
        human_delay_min=2000,
        human_delay_max=4000
    ),
    "Kalibrr": ScraperConfig(
        name="Kalibrr",
        enabled=True,
        max_pages=2,
        timeout=30000,
        retry_attempts=3,
        scroll_count=3
    ),
    "Dealls": ScraperConfig(
        name="Dealls",
        enabled=True,
        max_pages=2,
        timeout=30000,
        retry_attempts=3,
        scroll_count=3
    )
}


def get_scraper_config(name: str) -> ScraperConfig:
    """Get configuration for a specific scraper"""
    return DEFAULT_CONFIGS.get(name, ScraperConfig(name=name))


def update_scraper_config(name: str, **kwargs):
    """Update configuration for a specific scraper"""
    if name not in DEFAULT_CONFIGS:
        DEFAULT_CONFIGS[name] = ScraperConfig(name=name)
    
    config = DEFAULT_CONFIGS[name]
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
