from playwright.sync_api import sync_playwright
import time

def test_kalibrr():
    url = "https://www.kalibrr.com/job-board/te/it-software/q/react-developer/1"
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
        time.sleep(5) # wait for dynamic content
        
        # Take screenshot
        screenshot_path = "kalibrr_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        js_code = """
        () => {
            // Find all elements containing 'Software Engineer' but having no children (text nodes)
            const elements = Array.from(document.querySelectorAll('*'))
                .filter(e => e.textContent.includes('Software Engineer') && e.children.length === 0);
            
            if (elements.length > 0) {
                // Return the outerHTML of the element that has it, and its parent, and its grandparent
                let current = elements[0];
                let res = "ELEMENT:\\n" + current.outerHTML + "\\n\\nPARENT:\\n" + current.parentElement.outerHTML.substring(0, 500) + '...';
                
                // Let's also see if we can find the job card container
                // Look up until we find an element containing the location, e.g. 'Indonesia'
                let container = current;
                while (container && container !== document.body) {
                   if (container.textContent.includes('Indonesia') && container.textContent.includes('Rekruter terakhir aktif')) {
                       res += "\\n\\nCONTAINER:\\n" + container.outerHTML.substring(0, 1000) + '...';
                       break;
                   }
                   container = container.parentElement;
                }
                return res;
            }
            return 'not found';
        }
        """
        html_info = page.evaluate(js_code)
        print("HTML INFO:", html_info)
        
        with open("kalibrr_card_info.txt", "w", encoding="utf-8") as f:
            f.write(html_info)
            
        browser.close()

if __name__ == "__main__":
    test_kalibrr()
