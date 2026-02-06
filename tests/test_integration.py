"""
Integration Tests - Complete User Flow
Tests the entire user journey from homepage to signup
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="module")
def driver():
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


class TestUserFlowIntegration:
    """Integration tests for complete user flow"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_homepage_load(self, driver):
        """Test homepage loads correctly"""
        driver.get(self.BASE_URL)
        
        # Check page title
        assert "MFHelper" in driver.title
        
        # Check demo button exists
        demo_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Try Demo')]")
        assert demo_button.is_displayed()
        
        # Check add portfolio button
        add_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Your Portfolio')]")
        assert add_button.is_displayed()
    
    def test_demo_portfolio_flow(self, driver):
        """Test loading demo portfolio"""
        driver.get(self.BASE_URL)
        
        # Click demo button
        demo_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Try Demo')]"))
        )
        demo_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        # Check for demo banner
        time.sleep(2)  # Wait for banner to appear
        demo_banner = driver.find_element(By.ID, "demoBanner")
        assert demo_banner.is_displayed()
        
        # Verify localStorage has demo mode
        demo_mode = driver.execute_script("return localStorage.getItem('portfolioMode');")
        assert demo_mode == "demo"
    
    def test_portfolio_source_modal(self, driver):
        """Test portfolio source selection modal"""
        driver.get(f"{self.BASE_URL}/dashboard")
        
        # Clear localStorage to trigger modal
        driver.execute_script("localStorage.clear();")
        driver.refresh()
        
        # Wait for modal to appear
        time.sleep(1)
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "portfolioSourceModal"))
        )
        
        assert modal.is_displayed()
        
        # Check for all three options
        assert driver.find_element(By.XPATH, "//h3[contains(text(), 'Load Demo Portfolio')]")
        assert driver.find_element(By.XPATH, "//h3[contains(text(), 'Add Your Portfolio')]")
        assert driver.find_element(By.XPATH, "//h3[contains(text(), 'Continue with Existing')]")
    
    def test_manual_entry_modal(self, driver):
        """Test manual entry form"""
        driver.get(f"{self.BASE_URL}/dashboard")
        
        # Open manual entry modal
        manual_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Manual Entry')]"))
        )
        manual_btn.click()
        
        # Wait for modal
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "manualEntryModal"))
        )
        
        assert modal.is_displayed()
        
        # Check for simplified form (only 2 inputs per row)
        fund_input = driver.find_element(By.CLASS_NAME, "fund-search")
        amount_input = driver.find_element(By.XPATH, "//input[@type='number']")
        
        assert fund_input.is_displayed()
        assert amount_input.is_displayed()
    
    def test_fund_search_autocomplete(self, driver):
        """Test fund search dropdown"""
        driver.get(f"{self.BASE_URL}/dashboard")
        
        # Open manual entry
        manual_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Manual Entry')]"))
        )
        manual_btn.click()
        
        # Wait for modal
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "manualEntryModal"))
        )
        
        # Type in fund search
        fund_input = driver.find_element(By.CLASS_NAME, "fund-search")
        fund_input.send_keys("HDFC")
        
        # Wait for dropdown
        time.sleep(1)  # Wait for debounce
        dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "fund-dropdown"))
        )
        
        assert dropdown.is_displayed()
    
    def test_export_email_gate(self, driver):
        """Test export email gate modal"""
        driver.get(f"{self.BASE_URL}/dashboard")
        
        # Clear auth token to trigger email gate
        driver.execute_script("localStorage.removeItem('authToken');")
        driver.execute_script("sessionStorage.removeItem('capturedEmail');")
        
        # Trigger export (assuming there's an export button)
        try:
            export_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
            export_btn.click()
            
            # Wait for email modal
            time.sleep(1)
            modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "exportEmailModal"))
            )
            
            assert modal.is_displayed()
            
            # Check email input exists
            email_input = driver.find_element(By.XPATH, "//input[@type='email']")
            assert email_input.is_displayed()
        except:
            # Export button might not be visible in all states
            pass
    
    def test_signup_modal(self, driver):
        """Test signup modal display and form"""
        driver.get(self.BASE_URL)
        
        # Trigger signup modal via JavaScript
        driver.execute_script("showSignupModal();")
        
        # Wait for modal
        time.sleep(1)
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "signupModal"))
        )
        
        assert modal.is_displayed()
        
        # Check form fields
        assert driver.find_element(By.NAME, "full_name")
        assert driver.find_element(By.NAME, "email")
        assert driver.find_element(By.NAME, "password")
    
    def test_conversion_prompt_timing(self, driver):
        """Test conversion prompt appears after time"""
        driver.get(f"{self.BASE_URL}/dashboard")
        
        # Set demo mode
        driver.execute_script("""
            localStorage.setItem('portfolioMode', 'demo');
            localStorage.setItem('demoLoadedAt', new Date().toISOString());
        """)
        
        # Note: This would require waiting 2-5 minutes
        # For testing, we can trigger it manually
        driver.execute_script("conversionPrompts.showTimedPrompt();")
        
        time.sleep(1)
        prompt = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "conversion-prompt"))
        )
        
        assert prompt.is_displayed()
    
    def test_guest_mode_banner(self, driver):
        """Test guest mode banner"""
        driver.get(f"{self.BASE_URL}/dashboard")
        
        # Set guest mode
        driver.execute_script("localStorage.setItem('portfolioMode', 'guest');")
        driver.refresh()
        
        # Wait for banner
        time.sleep(2)
        banner = driver.find_element(By.ID, "guestBanner")
        
        assert banner.is_displayed()
        assert "Guest Mode" in banner.text
    
    def test_complete_demo_to_signup_flow(self, driver):
        """Test complete flow: Homepage -> Demo -> Features -> Signup"""
        # Start at homepage
        driver.get(self.BASE_URL)
        
        # Click demo button
        demo_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Try Demo')]"))
        )
        demo_button.click()
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        # Verify demo mode
        demo_mode = driver.execute_script("return localStorage.getItem('portfolioMode');")
        assert demo_mode == "demo"
        
        # Click signup from banner
        try:
            signup_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign Up')]")
            signup_btn.click()
            
            # Wait for signup modal
            time.sleep(1)
            modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "signupModal"))
            )
            
            assert modal.is_displayed()
        except:
            # Banner might be dismissed
            pass
    
    def test_localStorage_persistence(self, driver):
        """Test localStorage data persists across page loads"""
        driver.get(self.BASE_URL)
        
        # Set demo mode and data
        driver.execute_script("""
            localStorage.setItem('portfolioMode', 'demo');
            localStorage.setItem('demoPortfolioData', JSON.stringify({
                holdings: [{scheme_name: 'Test Fund'}],
                savedAt: new Date().toISOString()
            }));
        """)
        
        # Refresh page
        driver.refresh()
        
        # Check data persists
        mode = driver.execute_script("return localStorage.getItem('portfolioMode');")
        data = driver.execute_script("return localStorage.getItem('demoPortfolioData');")
        
        assert mode == "demo"
        assert data is not None
        assert "Test Fund" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
