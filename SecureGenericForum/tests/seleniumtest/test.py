import unittest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time 


# from server import app

ACCEPTABLE_PAGE_LOADING_TIME_SECONDS = 30

chrome_options = Options()

# From stack overflow
# ChromeDriver is just AWFUL because every version or two it breaks unless you pass cryptic arguments
# AGRESSIVE: options.setPageLoadStrategy(PageLoadStrategy.NONE); // https://www.skptricks.com/2018/08/timed-out-receiving-message-from-renderer-selenium.html

# https://stackoverflow.com/a/26283818/1689770
chrome_options.add_argument("start-maximized")

# https://stackoverflow.com/a/43840128/1689770
chrome_options.add_argument("enable-automation")

# only if you are ACTUALLY running headless
chrome_options.add_argument("--headless")

# https://stackoverflow.com/a/50725918/1689770
chrome_options.add_argument("--no-sandbox")

# https://stackoverflow.com/a/43840128/1689770
chrome_options.add_argument("--disable-infobars")

# https://stackoverflow.com/a/50725918/1689770
chrome_options.add_argument("--disable-dev-shm-usage")

# https://stackoverflow.com/a/49123152/1689770
chrome_options.add_argument("--disable-browser-side-navigation")

# https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
chrome_options.add_argument("--disable-gpu")

chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--dns-prefetch-disable")

class SeleniumTest(unittest.TestCase):

    def setUp(self):
        self.driver = None
        self.delay_time = 5
        try:
            self.driver = webdriver.Remote(
                command_executor="http://selenium-hub:4444/wd/hub",
                options=chrome_options,
            )
            self.driver.set_page_load_timeout(ACCEPTABLE_PAGE_LOADING_TIME_SECONDS)
            self.driver.get(f"http://flask-app:5000/test/session")
            self.driver.implicitly_wait('1')
            self.driver.get(f"http://flask-app:5000/test/session")
        except WebDriverException as e:
            self.driver.browser.quit()
            if "ERR_CONNECTION_REFUSED" not in e.msg:
                print(e)
        #print(self.driver.find_element_by_tag_name("body").text)

    def test_moderator_1_create_category(self):
        insertData = 'create_category'
        self.driver.find_element(By.ID, 'create_category').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.ID, 'createCategoryTextArea1').send_keys(insertData)
        self.driver.find_element(By.XPATH, '//input[@onclick="submitForm(\'formCreate1\');"]').click()
        insertedData = self.driver.find_element(By.XPATH, '//a[@href="/category/4"]').text
        print(insertData == insertedData)
        self.assertEqual(insertData,insertedData)

    def test_moderator_2_edit_category(self):
        insertData = 'edit_category'
        self.driver.find_element(By.XPATH, '//button[@data-bs-target="#Edit4"]').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.ID, 'editCategoryTextArea4').clear()
        self.driver.find_element(By.ID, 'editCategoryTextArea4').send_keys(insertData)
        self.driver.find_element(By.XPATH, '//input[@onclick="submitForm(\'formEdit4\');"]').click()
        insertedData = self.driver.find_element(By.XPATH, '//a[@href=\"/category/4\"]').text
        print(insertData == insertedData)
        self.assertEqual(insertData,insertedData)

    def test_moderator_3_delete_category(self):
        self.driver.find_element(By.XPATH, '//button[@data-bs-target=\"#Delete4\"]').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.XPATH, '//input[@onclick="submitForm(\'formDelete4\');"]').click()
        exist = None
        try:
            exist = self.driver.find_element(By.XPATH, '//a[@href=\"/category/4\"]').text
            exist = True
        except Exception as e:
            exist = False
        self.assertEqual(exist, False)

    def test_moderator_4_create_thread(self):
        self.driver.get('http://flask-app:5000/')
        insertData = 'create_thread'
        self.driver.find_element(By.XPATH, '//a[@href="/category/1"]').click()
        self.driver.find_element(By.XPATH, '//button[@data-bs-target=\"#Create1\"]').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.ID, 'createThreadTextArea1').send_keys(insertData)
        self.driver.find_element(By.XPATH,'//input[@onclick="submitForm(\'formCreate1\');"]').click()
        insertedData = self.driver.find_element(By.XPATH, '//a[@href=\"/thread/7\"]').text
        print(insertData == insertedData)
        self.assertEqual(insertData,insertedData)
        

    def test_moderator_5_edit_thread(self):
        self.driver.get('http://flask-app:5000/category/1')
        insertData = 'edit thread'
        self.driver.find_element(By.XPATH, '//button[@data-bs-target=\"#Edit7\"]').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.ID, 'editThreadTextArea7').clear()
        self.driver.find_element(By.ID, 'editThreadTextArea7').send_keys(insertData)
        self.driver.find_element(By.XPATH, '//input[@onclick="submitForm(\'formEdit7\');"]').click()
        insertedData = self.driver.find_element(By.XPATH, '//a[@href=\"/thread/7\"]').text
        print(insertData == insertedData)
        self.assertEqual(insertData,insertedData)
    
    def test_moderator_6_create_post(self):
        self.driver.get('http://flask-app:5000/category/1')
        self.driver.find_element(By.XPATH, '//a[@href="/thread/1"]').click()
        insertData = 'create_post'
        self.driver.find_element(By.XPATH, '//button[@data-bs-target=\"#Create1\"]').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.ID, 'createPostTextArea1').send_keys(insertData)
        self.driver.find_element(By.XPATH, '//input[@onclick="submitForm(\'formCreate1\');"]').click()
        insertedData = self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div/div/p').text
        print(insertData == insertedData)
        self.assertEqual(insertData,insertedData)

    def test_moderator_7_edit_post(self):
        self.driver.get('http://flask-app:5000//thread/1')
        insertData = 'edit_post'
        self.driver.find_element(By.XPATH, '//button[@data-bs-target="#Edit6"]').click()
        self.driver.implicitly_wait(self.delay_time)
        time.sleep(self.delay_time)
        self.driver.find_element(By.ID, 'editPostTextArea6').clear()
        self.driver.find_element(By.ID, 'editPostTextArea6').send_keys(insertData)
        self.driver.find_element(By.XPATH, '//input[@onclick="submitForm(\'formEdit6\');"]').click()
        insertedData = self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div/div/p').text
        print(insertData == insertedData)
        self.assertEqual(insertData,insertedData)
        
    def tearDown(self):
        self.driver.quit()
    

if __name__ == "__main__":
    unittest.main(verbosity=1)