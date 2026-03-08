from playwright.sync_api import sync_playwright
import time

def test_jobstreet():
    url = "https://id.jobstreet.com/id/react-developer-jobs"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # using a realistic user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        print(f"Navigating to {url}")
        page.goto(url, timeout=30000)
        time.sleep(8) # wait for dynamic content
        
        # Take screenshot
        screenshot_path = "jobstreet_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Extract text directly to see if DOM has it
        js_extract = """
        () => {
            let cards = document.querySelectorAll('article[data-automation="normalJob"]');
            if (cards.length === 0) cards = document.querySelectorAll('article[data-automation="jobCard"]');
            if (cards.length === 0) cards = document.querySelectorAll('article');
            
            return Array.from(cards).map(c => c.textContent).join('\\n---\\n');
        }
        """
        inner_text = page.evaluate(js_extract)
        with open("jobstreet_text.txt", "w", encoding="utf-8") as f:
            f.write(inner_text)
            
        browser.close()

if __name__ == "__main__":
    test_jobstreet()
