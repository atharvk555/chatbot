import json
from amazon import get_product
from requests import post
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver



AMAZON="https://www.amazon.in"

URLS={
	AMAZON:{
		"search_field_query": 'input[name="field-keywords"]',
		"search_button_query": 'input[value="Go"]',
		"product_selector": "div.s-card-container"
	}
}

avail_urls=URLS.keys()

def save_results(results):
	data = {"results": results}
	file = "results.json"
	with open(file, "w") as f:
		json.dump(data, f)


def post_results(results, endpoint, search_text, source):
	headers = {
		"Content-Type": "application/json"
	}
	data = {"data": results, "search_text": search_text, "source": source}

	print("Sending request to", endpoint)
	response = post("http://localhost:5000" + endpoint, headers=headers, json=data)
	print("Status code:", response.status_code)


def search(metadata: dict, driver: WebDriver, search_text: str):
	print(f"Searching for {search_text} on {driver.current_url}")
	search_field_query = metadata.get("search_field_query")
	search_button_query = metadata.get("search_button_query")

	if search_field_query and search_button_query:
		print("Filling")
		search_box=driver.find_element(By.CSS_SELECTOR,search_field_query)
		search_box.clear()
		search_box.send_keys(search_text)

		print("Pressing")
		search_box.send_keys(Keys.ENTER)

	else:
		raise Exception("Could not search")

	driver.maximize_window()
	driver.implicitly_wait(10)


	return driver

def get_products(driver:WebDriver,search_text,selector,get_product):
	driver.set_page_load_timeout(20)
	print("fetching products")
	product_divs=driver.find_elements(By.CSS_SELECTOR,selector)
	valid_prd=[]
	words=search_text.split(" ")
	for div in product_divs:

		product=get_product(div)

		if not product["price"] or not product["url"]:
			continue

		if all(word.lower() in product["name"].lower() for word in words ):
			valid_prd.append(product)

	return valid_prd


def main(url,search_text,response_route=None):
	metadata=URLS.get(url)
	if not metadata:
		print("INVALID URL")
		return

	driver=webdriver.Chrome()
	driver.get(url)

	print("Loading amazon page")

	driver1=search(metadata,driver,search_text)

	products=get_products(driver1,search_text,metadata["product_selector"],get_product)

	print("saving")
	save_results(products)
	post_results(products,response_route,search_text,url)

	driver.close()

if __name__=="__main__":
	main(AMAZON,"ps5")
