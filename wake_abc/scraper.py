from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .results import Location, Product

WEBSITE_URL = "https://wakeabc.com/search-our-inventory/"

# A cache of results keyed on produce_name
_cache = {}

def _search_inventory(product_name: str) -> dict:
    if product_name in _cache:
        return _cache[product_name]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options)
    driver.get(WEBSITE_URL)
    wait = WebDriverWait(driver, 10)

    search_box = driver.find_element(By.NAME, "productSearch")
    search_box.send_keys(product_name)
    search_button = driver.find_element(By.CSS_SELECTOR, "form.wake-inv-search").find_element(By.CSS_SELECTOR, "input[type='submit']")
    search_button.click()

    first_product_result = driver.find_element(By.XPATH, "//div[@id='productSearchResults']/div[2]")
    show_first_product_button = first_product_result.find_element(By.CLASS_NAME, "collapse-heading")
    show_first_product_button.click()
    result_items = first_product_result.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")

    results = {Location: [], Product: None}
    wait.until(EC.visibility_of(result_items[-1].find_elements(By.TAG_NAME, "span")[0]))
    for item in result_items:
        raw_data = item.find_elements(By.TAG_NAME, "span")
        address = raw_data[0].text.replace("\n", " ")
        count = raw_data[1].text.split(" ", 1)[0]
        results[Location].append(Location(address, int(count)))
    
    product_details = first_product_result.find_element(By.CLASS_NAME, "wake-product").find_elements(By.TAG_NAME, "p")
    price_lookup_code = product_details[0].find_element(By.TAG_NAME, "small").text.split(" ", 1)[1]
    product_values = product_details[1].find_elements(By.TAG_NAME, "span")
    price = product_values[0].text.split(" ", 1)[0]
    volume = product_values[1].text.split("L")[0]
    results[Product] = Product(price_lookup_code, float(price), float(volume))

    _cache[product_name] = results
    return results

def get_inventory(product_name: str) -> list[Location]:
    results = _search_inventory(product_name)
    return results[Location]

def get_product(product_name: str) -> Product:
    results = _search_inventory(product_name)
    return results[Product]

def clear_cache():
    _cache = {}