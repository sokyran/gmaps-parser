from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.firefox.options import Options
import pandas as pd
from utils import safe_run
from time import sleep
from models import Restaurant, all_possible_tags

# url of restaurants in area
# url = "https://www.google.com.ua/maps/search/Рестораны/@50.4766857,30.4726883,11z/"
url = "https://www.google.com.ua/maps/search/Рестораны/@52.2267581,21.0062611,15z/"
# Opening driver
options = Options()
options.headless = False
driver = webdriver.Firefox(options=options)
driver.get(url)
wait = WebDriverWait(driver, 10)
# setting those booleans to find out on which page driver stopped
on_details = False
on_tags = False

@safe_run(driver=driver)
def parse_one_restaurant():
	"""
	Parse one page of a restaurant and get all his parameters
	:returns numpy array if rest has ratings
	:returns numpy array with only None if no ratings and/or work hours
	"""
	
	# used for determining on which page error occurs
	global on_tags, on_details
	try:
		on_details = True
		on_tags = False
		# here i get all of useful params of this page
		name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.section-hero-header-title-title'))).text
		type = driver.find_element_by_css_selector(
			'div.GLOBAL__gm2-body-2:nth-child(2)>span:nth-child(1)>span:nth-child(1)>button:nth-child(1)').text
		cost = driver.find_element_by_css_selector(
			'span.section-rating-term:nth-child(2)>span:nth-child(2)>span:nth-child(1)>span:nth-child(2)').text
		rating_and_num = driver.find_element_by_css_selector('div.GLOBAL__gm2-body-2')
		rating = rating_and_num.text.split('\n')[0]
		num = rating_and_num.text.split('\n')[1].split('·')[0]
		open_hours = driver.find_element_by_css_selector('span.section-info-text:nth-child(2)').text.strip()
		# get to the all tags of restaurant page
		tags_page = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.section-editorial')))
		try:
			tags_page.click()
		except ElementClickInterceptedException:
			sleep(0.2)
			tags_page.click()
		on_tags = True
		on_details = False
		# get params that are not present
		neg = driver.find_elements_by_class_name('section-attribute-group-item-negative')
		all_negs = set(i.text for i in neg)
		pos = driver.find_elements_by_class_name('section-attribute-group-item')
		all_pos = set(i.text for i in pos) - all_negs
		# create new Restaurant class so that all params are gathered together
		collected_rest = Restaurant(name, type, cost, rating, num, open_hours, all_pos, all_negs)
		return collected_rest.to_ndarray()
	# catch an error and so skip current restaurant
	except (IndexError, NoSuchElementException, TimeoutException):
		return None

@safe_run(driver=driver)
def parse_one_page():
	global all_possible_tags
	# i gathered all possible tags for restaurant from page 1. i believe there wont be any more
	columns = ['name', 'category', 'cost', 'rating', 'num_of_rates', 'open_hours'] + all_possible_tags
	# create emptry dataframe where i store all my data for current page
	general_df_for_page = pd.DataFrame([], columns=columns)
	sleep(1)
	wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'section-result-content')))
	wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-content')))
	elem = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-header-container')))
	titles = driver.find_elements_by_class_name('section-result-title')
	for i in range(len(titles)):
		wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'section-result-content')))
		wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-content')))
		titles = driver.find_elements_by_class_name('section-result-content')
		sleep(0.3)
		titles[i].click()
		sleep(0.1)
		rest = parse_one_restaurant()
		# check if parse_one_restaueant func return None and not numpy array
		if type(rest) is not type(None):
			general_df_for_page = general_df_for_page.append(pd.DataFrame(rest.reshape(1, -1), columns=columns), ignore_index=True)
		# check if driver stops on tags or detals page
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


global all_possible_tags
columns = ['name', 'category', 'cost', 'rating', 'num_of_rates', 'open_hours'] + all_possible_tags
general_df_for_all = pd.DataFrame([], columns=columns)

for i in range(18):
	df = parse_one_page()
	print(df.shape)
	general_df_for_all = general_df_for_all.append(df, ignore_index=True)
	try:
		next_btn = driver.find_element_by_css_selector('.n7lv7yjyC35__button-next-icon')
	except NoSuchElementException:
		sleep(0.3)
		next_btn = driver.find_element_by_css_selector('.n7lv7yjyC35__button-next-icon')
	next_btn.click()
	sleep(4)

general_df_for_all.to_csv('rests.csv')
driver.close()
