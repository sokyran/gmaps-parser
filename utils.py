from selenium.common.exceptions import ElementClickInterceptedException
from time import sleep


def parse(e):
	class_ = e.split('"')[1]
	return class_


def safe_run(*args, **kwargs):
	def func_wrapper(func):
		try:
			return func
		except ElementClickInterceptedException as e:
			print('caught exception')
			class_ = parse(e.msg)
			driver = kwargs['driver']
			sleep(0.35)
			driver.find_elements_by_class_name(class_).click()
	
	return func_wrapper
