import pandas as pd
import numpy as np

all_possible_tags = ['Wi-Fi', 'Десерт', 'Паркувальний майданчик для людей на інвалідних візках', 'Години знижок на їжу',
					 'Підходить для сімейного відпочинку', 'Пізні вечері', 'Дитяче меню', 'Є вегетаріанські страви',
					 'Дебетові картки', 'Салат-бар', 'Пиво', 'Груповий відпочинок', 'Органічні страви', 'Камін',
					 'Обіди', 'Оплата лише готівкою', 'Халяльна їжа', 'Затишне місце', 'Туалет', 'Невимушена атмосфера',
					 'Бар', 'Туалет із доступом для інвалідів', 'Високі стільці', 'Спортивні змагання',
					 'Компанії, якими керують жінки', 'Мобільні платежі через NFC', 'Доставка', 'Місця для сидіння',
					 'Підходить для дітей', 'Вхід для людей на інвалідних візках',
					 'Місця для людей на інвалідних візках', 'Жива музика', 'Вечері', 'Сніданки', 'Кредитні картки',
					 'Літній майданчик', 'Чеки', 'Вино', 'Смачні коктейлі']


class Restaurant:
	def __init__(self, name, category, cost, rating, num_of_rates, open_hours, pos_tags, neg_tags):
		self.name = name
		self.category = category
		self.cost = cost
		self.rating = rating
		self.num_of_rates = num_of_rates
		self.open_hours = open_hours
		self.pos_tags = pos_tags
		self.neg_tags = neg_tags
	
	def __str__(self):
		return f"Name: {self.name} with rating {self.rating}, {self.cost} cost and open at {self.open_hours};"
	
	def to_numpy_array(self):
		attrs = np.array(
			[self.name, self.category, self.cost, self.rating, self.num_of_rates, self.open_hours]).reshape(1, -1)
		tags = np.array([1 if tag in self.pos_tags else 0 if tag in self.neg_tags else 0 for tag in all_possible_tags]
						).reshape(1, -1)
		return np.concatenate([attrs, tags], axis=1)
	
	def print_vars(self):
		result = []
		dic = vars(self).values()
		for i in dic:
			if isinstance(i, set):
				result += [*i]
			else:
				result.append(i)
		rest_df = pd.DataFrame(result)
		print(rest_df)
