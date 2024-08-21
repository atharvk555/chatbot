from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs, unquote

def get_product(product_div:WebElement):
	img_element=product_div.find_element(By.CSS_SELECTOR,'img.s-image')
	nme_element=product_div.find_element(By.CSS_SELECTOR,'h2 a span')
	try:
		price_element=product_div.find_element(By.CSS_SELECTOR,'span.a-price-whole')
	except:
		price_element=None
	try:
		url_element=product_div.find_element(By.CSS_SELECTOR,'a.a-link-normal.s-no-hover.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
	except:
		url_element=None

	img_url=img_element.get_attribute('src') if img_element else None

	prd_nme=nme_element.text if nme_element else None

	product_price = float(price_element.text.replace(",","").strip()) if price_element else None
	print(product_price)


	if url_element:
		full_url = url_element.get_attribute('href')
		if("sspa" in full_url):
			parsed_url = urlparse(full_url)
			query_params = parse_qs(parsed_url.query)
			encoded_path = query_params.get('url', [])[0]

			# Decode the path
			decoded_path = unquote(encoded_path)
			product_url = f"https://www.amazon.in{decoded_path}"
			product_url = "/".join(product_url.split('/')[:6])
		else:
			product_url="/".join(full_url.split('/')[:6])

		print(product_url)
	else:
		product_url=None


	return {"img":img_url,"name":prd_nme,"price":product_price,"url":product_url}



