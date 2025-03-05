from seleniumwire import webdriver

def create_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("disable-logging")
    drv = webdriver.Chrome(seleniumwire_options={}, options=opts)
    return drv
