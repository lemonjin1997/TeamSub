from os import environ
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

environ.get("")

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


def before_all(context):
    while True:
        try:
            context.browser = webdriver.Remote(
                command_executor="http://selenium-hub:4444/wd/hub",
                options=chrome_options,
            )
            context.browser.set_page_load_timeout(ACCEPTABLE_PAGE_LOADING_TIME_SECONDS)
            context.browser.get(f"http://flask-app:5000")
            break
        except WebDriverException as e:
            context.browser.quit()
            if "ERR_CONNECTION_REFUSED" not in e.msg:
                print(e)
        sleep(10)

    print(context.browser.find_element_by_tag_name("body").text)

    # Get stuff
    # context.browser.get(f"http://www.google.com")

    # print("Try container name")
    # print("hostname", hostname)

    # context.server = simple_server.WSGIServer(("", 5000), WSGIRequestHandler)
    # context.server.set_app(app)
    # context.pa_app = threading.Thread(target=context.server.serve_forever)
    # context.pa_app.start()

    # context.browser = webdriver.Remote(options=chrome_options, executable_path=CHROME_DRIVER)
    # context.browser.set_page_load_timeout(time_to_wait=200)
    # context.browser.quit()


def after_all(context):
    context.browser.quit()
    # context.server.shutdown()
    # context.pa_app.join()
