from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import markdownify
import time
import secrets
import string
import os, glob

class PoeBot:
    def start_driver(self, p_b_cookie, bot_name):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)
        stealth(self.driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
        self.driver.get(f"https://poe.com/")
        self.driver.add_cookie({"name": "p-b", "value": p_b_cookie})
        self.driver.get(f"https://poe.com/{bot_name}")

    def get_latest_message(self):
        bot_messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "Message_botMessageBubble__CPGMI")]')
        if bot_messages:
            latest_message = bot_messages[-1]
            if (latest_message.text == "..."):
                return None
            return markdownify.markdownify(latest_message.get_attribute("innerHTML"), heading_style="ATX")
        else:
            return None
    
    def abort_message(self):
        abort_button = self.driver.find_elements(By.CLASS_NAME, "ChatStopMessageButton_stopButton__LWNj6")
        if abort_button:
            abort_button[0].click()

    def send_message(self, message):
        filename_length = secrets.randbelow(8) + 9
        filename = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(filename_length))

        [os.remove(i) for i in glob.glob(".cache/*.txt")]

        os.makedirs(".cache", exist_ok=True)
        txt_file_path = os.path.join(".cache", f"{filename}.txt")
        open(txt_file_path, 'w', encoding='utf-8').write(message)
        absolute_path = os.path.abspath(txt_file_path)

        file_input = self.driver.find_element(By.CLASS_NAME, 'ChatMessageFileInputButton_input__szx6_')
        file_input.send_keys(absolute_path)
        
        text_area = self.driver.find_element(By.CLASS_NAME, "GrowingTextArea_textArea__eadlu")
        text_area.send_keys("-")
        text_area.send_keys(Keys.RETURN)
        time.sleep(2)
        start_time = time.time()
        while True:
            bot_messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "Message_botMessageBubble__CPGMI")]')
            if bot_messages:
                latest_message = bot_messages[-1].text
            if latest_message != "...":
                break
            if time.time() - start_time > 120:
                raise Exception("Timeout waiting for bot message")
            time.sleep(1)

    def clear_context(self):
        clear_button = self.driver.find_element(By.CLASS_NAME, "ChatBreakButton_button__EihE0")
        clear_button.click()

    def is_generating(self):
        stop_button_elements = self.driver.find_elements(By.CLASS_NAME, "ChatStopMessageButton_stopButton__LWNj6")
        return len(stop_button_elements) > 0
    
    def get_suggestions(self):
        suggestions_container = self.driver.find_elements(By.CLASS_NAME, "ChatMessageSuggestedReplies_suggestedRepliesContainer__JgW12")
        if not suggestions_container:
            return []
        suggestion_buttons = suggestions_container[0].find_elements(By.TAG_NAME, "button")
        return [button.text for button in suggestion_buttons]
    
    def delete_latest_message(self):
        bot_messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "Message_botMessageBubble__CPGMI")]')
        latest_message = bot_messages[-1]
        ActionChains(self.driver).context_click(latest_message).perform()

        delete_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(((By.XPATH, "//button[starts-with(@class, 'DropdownMenuItem_item__nYv_0') and contains(., 'Delete...')]"))))
        ActionChains(self.driver).move_to_element(delete_button).click().perform()

        confirm1_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".Button_buttonBase__0QP_m.Button_danger__zI3OH")))
        ActionChains(self.driver).move_to_element(confirm1_button).click().perform()

        confirm2_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(((By.XPATH, "//button[@class='Button_buttonBase__0QP_m Button_danger__zI3OH']"))))
        ActionChains(self.driver).move_to_element(confirm2_button).click().perform()
    
    def reload(self):
        self.driver.refresh()

    def kill_driver(self):
        if hasattr(self, "driver"):
            self.driver.quit()

    def __del__(self):
        if hasattr(self, "driver"):
            self.kill_driver()