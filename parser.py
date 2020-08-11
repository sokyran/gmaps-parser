from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.firefox.options import Options
import pandas as pd
from time import sleep
from models import Restaurant, all_possible_tags

# url of restaurants in area
# url = "https://www.google.com.ua/maps/search/Рестораны/@50.4766857,30.4726883,11z/"
url = input("Enter url of google maps area:\n")

# Opening driver
options = Options()
options.headless = False
driver = webdriver.Firefox(options=options)
driver.get(url)
wait = WebDriverWait(driver, 20)

# Setting those booleans to find out on which page driver stopped
on_details = False
on_tags = False


def parse_one_restaurant():
	"""
	Parse one page of a restaurant and get all his parameters
	:returns numpy array if rest has ratings or only None if no ratings and/or work hours
	"""
	
	# Used for determining on which page error occurs
	global on_tags, on_details
	try:
		on_details = True
		on_tags = False
		
		# Get all of useful params of this page
		name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.section-hero-header-title-title'))).text
		sleep(1)
		type_ = driver.find_element_by_css_selector(
			'div.GLOBAL__gm2-body-2:nth-child(2)>span:nth-child(1)>span:nth-child(1)>button:nth-child(1)').text
		cost = driver.find_element_by_css_selector(
			'span.section-rating-term:nth-child(2)>span:nth-child(2)>span:nth-child(1)>span:nth-child(2)').text
		rating_and_num = driver.find_element_by_css_selector('div.GLOBAL__gm2-body-2')
		rating = rating_and_num.text.split('\n')[0]
		num = rating_and_num.text.split('\n')[1].split('·')[0]
		open_hours = driver.find_element_by_css_selector('span.section-info-text:nth-child(2)').text.strip()
		
		# Get to the all tags of restaurant page
		tags_page = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.section-editorial')))
		try:
			tags_page.click()
		except ElementClickInterceptedException:
			sleep(0.4)
			tags_page.click()
		on_tags = True
		on_details = False
		
		# Get params from tags page
		neg = driver.find_elements_by_class_name('section-attribute-group-item-negative')
		all_negs = set(i.text for i in neg)
		pos = driver.find_elements_by_class_name('section-attribute-group-item')
		all_pos = set(i.text for i in pos) - all_negs
		
		# Create new Restaurant class so that all params are gathered together
		collected_rest = Restaurant(name, type_, cost, rating, num, open_hours, all_pos, all_negs)
		return collected_rest.to_numpy_array()
		
	# Catch an error and so skip current restaurant
	except (IndexError, NoSuchElementException, TimeoutException):
		return None


def parse_one_page():
	# Make import tags available within function
	global all_possible_tags
	
	# Columns for df
	columns = ['name', 'category', 'cost', 'rating', 'num_of_rates', 'open_hours'] + all_possible_tags
	
	# Create emptry dataframe where we store all data for current page
	general_df_for_page = pd.DataFrame([], columns=columns)
	sleep(1.5)
	titles = driver.find_elements_by_class_name('section-result-title')
	for i in range(len(titles)):
		sleep(0.4)
		titles = driver.find_elements_by_class_name('section-result-content')
		sleep(0.4)
		titles[i].click()
		sleep(0.1)
		rest = parse_one_restaurant()
		
		# Check if parse_one_restaueant func return None and not numpy array
		if type(rest) is not type(None):
			general_df_for_page = general_df_for_page.append(pd.DataFrame(rest.reshape(1, -1), columns=columns), ignore_index=True)
			
		# Check if driver stops on tags or detals page
		if on_tags:
			back_to_details_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.section-header-back-button')))
			back_to_details_btn.click()
			back_to_results_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.section-back-to-list-button')))
			back_to_results_btn.click()
		elif on_details:
			back_to_results_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.section-back-to-list-button')))
			try:
				back_to_results_btn.click()
			except ElementClickInterceptedException:
				sleep(0.3)
				back_to_results_btn.click()
	
	return general_df_for_page

def main():
	global all_possible_tags
	columns = ['name', 'category', 'cost', 'rating', 'num_of_rates', 'open_hours'] + all_possible_tags
	general_df_for_all = pd.DataFrame([], columns=columns)

	for _ in range(5):
		df = parse_one_page()
		print(df.shape)
		general_df_for_all = general_df_for_all.append(df, ignore_index=True)
		try:
			next_btn = driver.find_element_by_css_selector('.n7lv7yjyC35__button-next-icon')
		except NoSuchElementException: # In case driver is in hurry and doesnt wait for button to load
			sleep(0.3)
			next_btn = driver.find_element_by_css_selector('.n7lv7yjyC35__button-next-icon')
		next_btn.click()
		sleep(3)

	general_df_for_all.to_csv('rests.csv')
	driver.close()
	
main()	
