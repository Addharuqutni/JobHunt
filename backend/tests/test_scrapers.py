"""
Simple Scraper Test Suite
Run this to verify all scrapers are working correctly
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.config import ScraperRegistry


def test_all_scrapers():
    """Test all registered scrapers with a simple keyword"""
    
    print("\n" + "="*60)
    print("🧪 JobSentinel Scraper Test Suite")
    print("="*60 + "\n")
    
    # Get all available scrapers
    scrapers = ScraperRegistry.get_available_scrapers()
    
    print(f"Found {len(scrapers)} scrapers: {list(scrapers.keys())}\n")
    
    # Test keyword
    keyword = "python developer"
    max_pages = 1
    
    results = {}
    
    for name, scraper_class in scrapers.items():
        print(f"\n{'='*60}")
        print(f"Testing {name} Scraper")
        print('='*60)
        
        try:
            scraper = scraper_class()
            jobs = scraper.scrape(keyword, max_pages=max_pages)
            
            metrics = scraper.metrics.summary()
            
            results[name] = {
                "status": "✅ PASS",
                "jobs_found": metrics["jobs_found"],
                "jobs_saved": metrics["jobs_saved"],
                "success_rate": metrics["success_rate"],
                "duration": f"{metrics['duration_seconds']:.2f}s",
                "errors": metrics["errors"]
            }
            
            print(f"\n✅ {name} Test PASSED")
            print(f"   Jobs Found: {metrics['jobs_found']}")
            print(f"   Jobs Saved: {metrics['jobs_saved']}")
            print(f"   Success Rate: {metrics['success_rate']}")
            print(f"   Duration: {metrics['duration_seconds']:.2f}s")
            print(f"   Errors: {metrics['errors']}")
            
        except Exception as e:
            results[name] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"\n❌ {name} Test FAILED")
            print(f"   Error: {e}")
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for r in results.values() if r["status"] == "✅ PASS")
    failed = sum(1 for r in results.values() if r["status"] == "❌ FAIL")
    
    for name, result in results.items():
        print(f"{name:15} {result['status']}")
    
    print(f"\nTotal: {passed}/{len(scrapers)} passed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Scraper system is ready.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
    
    assert failed == 0, f"{failed} scraper(s) failed. Check errors above."


if __name__ == "__main__":
    success = test_all_scrapers()
    sys.exit(0 if success else 1)
