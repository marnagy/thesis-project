import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from os import getcwd

def Main():
	driverPath = 'C:\\Users\\mnagy\\Python scripts\\Selenium\\chromedriver.exe'
	driver = webdriver.Chrome(driverPath)
	timeoutConst = 10
	# op = webdriver.ChromeOptions()  ## for using selenium without opening the browser
	# op.add_argument("headless")
	# driver = webdriver.Chrome(op)
	driver.get("https://www.duckduckgo.com")
	try:

		search_input = WebDriverWait(driver, timeoutConst).until( EC.presence_of_element_located( (By.ID, "search_form_input_homepage" ) ) )
		search_input.send_keys("obchody praha")
		search_input.send_keys(Keys.RETURN)

		more_places = WebDriverWait(driver, timeoutConst).until( EC.presence_of_element_located((By.CLASS_NAME, "module__places-more__link--more-places")) )
		more_places.click()
		
		parent = WebDriverWait(driver, timeoutConst).until( EC.presence_of_element_located((By.CLASS_NAME, "vertical--map__sidebar__results__inner")) )
		places = parent.find_elements_by_tag_name("div")

		for place in places:
			if place is None or place.text == "":
				continue
			ul_list =  place.find_elements_by_tag_name("ul")
			if ul_list != []:
				parts = ul_list[0].find_elements_by_tag_name("li")
				address = ""
				if (len(parts) == 3):
					address = parts[1].text + " " + parts[2].text
				elif (len(parts) == 2):
					address = parts[0].text + " " + parts[1].text
				#encoded_address = address.encode("utf8")
				print(address)

	finally:
		driver.quit()

if __name__ == "__main__":
	Main()