import tkinter as tk
import _tkinter
from tkinter import *
import webbrowser
import requests
import urllib.request
from bs4 import BeautifulSoup
import pyautogui
import time
import os
import csv

root = tk.Tk()
URL = "https://www.target.com/" #url сайта
#информация браузера
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15', 'accept': '*/*'}
HOST = "https://www.target.com" #url без дроби
#Путь расположения программы
LOCATION = '/Users/georgiy.tolkachov/Documents/Yulian/work_summer'
#Путь для експорта файла
EXPORT_FILE = '/Users/georgiy.tolkachov/Documents/Yulian/work_summer/products.csv'

#создание и параметры окна
root.title("Parser Target.com")
root.geometry('400x400')
canvas = Canvas(root, height = 400, width = 400)
canvas.pack()
frame = Frame(root)
frame.place(relx = 0.15, rely = 0.15, relwidth = 0.7, relheight = 0.7)

ask = Label(frame, text = 'Input search text', font = 40)
ask.pack()
searchInput = Entry(frame)
searchInput.pack()

#функция поиска на сайте при нажатии на кнопку
def btn_search_click():
	search = searchInput.get()
	s = str(search)
	result = s.replace(" ", "+") #при нескольких словах поиска пробелы заменяются в url
	link = f"https://www.target.com/s?searchTerm={result}"
	webbrowser.open(link)
	return link

btn_search = Button(frame, text = "search", command = btn_search_click)
btn_search.pack()

#функция получения статуса страницы
def get_html(url, params=None):
	r = requests.get(url, headers=HEADERS, params=params)
	return r

#функция сохранения в ексель
def save_file(items, path):
    with open(path, 'w', newline='') as file:
    	#задаем параметры полей ексель файла
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['link', 'title', 'upc', 'price'])
        for item in items: #записываем в него информацию
            writer.writerow([item['link'], item['title'], item['upc'], item['price']])

#функция с парсером
def get_content():
	x = 0
	y = 0
	z = 1
	products = []
	#цыкл для парсинка страниц поиска
	while x < z:
		print(f"page №{x}")
		time.sleep(5)
		pyautogui.scroll(-60)
		time.sleep(2)
		pyautogui.scroll(-60)
		time.sleep(2)
		#сохранение страницы браузера
		pyautogui.hotkey('command', 's')
		time.sleep(3)
		pyautogui.typewrite(f'Page{x}.webarchive')
		pyautogui.press('enter')
		#ожидание скачивания файла
		while 0<1:
			time.sleep(5)
			try: 
				webUrl = urllib.request.urlopen(f"file://{LOCATION}/Page{x}.webarchive")
				break
			except:
				continue
		#чтение кода сохраненной страницы
		html = webUrl.read()
		soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")

		#продукты на странице
		items = soup.find_all('li', class_='Col-favj32-0')
		print(f"items: {len(items)}")

		#следуйщая страница
		try:
			page = soup.find('a', class_='cWGuNV').get('href')
			if page != None:
				z += 1
		except:
			print("it is the last page")

		#парсинг отдельных страниц продуктов
		for item in items:
			print(f"item №{y}")
			solo = item.find('a', class_ = 'Link__StyledLink-sc-4b9qcv-0')
			if solo != None: #проверка на не рекламный баннер
				#ссылка
				solo_link = HOST + solo.get('href')
				print(f'solo_link: {solo_link}')
				html_status = get_html(solo_link)
				print(f"html_status: {html_status}")
				if html_status.status_code == 200:
					webbrowser.open(solo_link)
					time.sleep(5)
					pyautogui.scroll(-20)
					time.sleep(2)
					#сохранение страницы продукта
					pyautogui.hotkey('command', 's')
					time.sleep(1)
					pyautogui.typewrite(f'Product{y}.webarchive')
					pyautogui.press('enter')
					while 0<1:
						time.sleep(5)
						try: 
							file_product = urllib.request.urlopen(f"file://{LOCATION}/Product{y}.webarchive")
							break
						except:
							continue
					#чтение кода страницы продукта
					html_product = file_product.read()
					soup_product = BeautifulSoup(html_product, 'html.parser', from_encoding="utf-8")
					#название
					product_title = item.find('a', class_='styles__StyledTitleLink-h3r0um-1').get_text()
					print(f'product title: {product_title}')
					#цена
					product_price = soup_product.find('div', class_='web-migration-tof__PriceFontSize-sc-14z8sos-14').get_text()
					print(f"product price: {product_price}")
					#upc код (длинный код потому что на сайте нет отдельного класса для upc - он и остальное описание проверяются циклом)
					product_upc = None
					product_upc_path = soup_product.find_all('div', class_='styles__StyledCol-ct8kx6-0')
					for item in product_upc_path:
						check = item.find('b') #все теги b
						if check != None:
							desc = item.find_all('div') #все div
							product_upc_full = []
							for item in desc:
								#поиск по содержанию в каждом из div
								if any("UPC" in s for s in item):
									#сам upc код
									product_upc_full.append(f"{item}")
									product_upc_mayge = str({x.replace('<div aria-hidden="true" tabindex="-1"><b aria-hidden="true" tabindex="-1">UPC</b>: ', '').replace('<hr aria-hidden="true" tabindex="-1"/></div>', '') for x in product_upc_full})
									one = product_upc_mayge.replace("{", "")
									two = one.replace("'", "", 2)
									product_upc = two.replace("}", "")
									print(f"product upc: {product_upc}")

					#массив данных которые получаем при парсинге
					products.append({
						'link': solo_link,
						'title': product_title,
						'upc': product_upc,
						'price': product_price,
					})
					#сохранение
					save_file(products, EXPORT_FILE)
					#чистка браузера и файлов
					pyautogui.hotkey('command', 'w')
					os.remove(f"{LOCATION}/Product{y}.webarchive")
			#это реклама
			else:
				print("this is an advertisement")
			y += 1
		#конец цикла продуктов + очистка файлов страниц
		pyautogui.hotkey('command', 'w')
		os.remove(f"{LOCATION}/Page{x}.webarchive")
		webbrowser.open(page)
		x += 1
	return products

#функция вызова парсера
def btn_parse_click():
	#проверка url
	URL = btn_search_click()
	html = get_html(URL)
	if html.status_code == 200:
		#парсинг
		result = get_content()
		#сохранение
		save_file(result, EXPORT_FILE)
		print(f"Получено {len(result)} товаров")
	else:
		print('Error')
	
#кнопка вызова парсера
btn_parse = Button(frame, text = "parse", command = btn_parse_click)
btn_parse.pack()


#app = Application(master=root)
root.mainloop()