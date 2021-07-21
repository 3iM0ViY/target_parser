import tkinter as tk
from tkinter import *
import webbrowser
import requests
import urllib.request
from bs4 import BeautifulSoup
import pyautogui
import time
import os
import csv
import shutil

root = tk.Tk()
URL = "https://www.target.com/" #url сайта
#информация браузера
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'accept': '*/*'}
#Путь расположения программы
LOCATION = 'C:/Users/Юлиан/Юлиан/Разное/parser/pages'
#Путь для експорта файла
EXPORT_FILE = 'C:/Users/Юлиан/Юлиан/Разное/parser/products.csv'

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

#сохранение страницы
def save(name):
	file_product = None
	succesful = False
	while 0<1:
		z = 0
		pyautogui.hotkey('ctrl', 's')
		time.sleep(1)
		pyautogui.typewrite(name)
		pyautogui.press('enter')
		while True:
			pyautogui.moveTo(1250, 700)
			time.sleep(5)
			if z == 6:
				break
			try: 
				file_product = urllib.request.urlopen(f"file:///{LOCATION}" + name)
				print(f"file product: {file_product}")
				succesful = True
				break
			except:
				z += 1
				continue
		if succesful:
			break
	print(f"file product: {file_product}")
	return file_product

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
	#цыкл для парсинка страниц поиска
	products = []
	while x < z:
		pyautogui.moveTo(1250, 700)
		print(f"page №{x}")
		time.sleep(5)
		pyautogui.scroll(-800)
		time.sleep(1)
		pyautogui.scroll(-800)
		time.sleep(1)
		pyautogui.scroll(-800)
		time.sleep(1)
		pyautogui.scroll(-800)
		time.sleep(1)
		pyautogui.scroll(-800)
		time.sleep(1)
		pyautogui.scroll(-800)
		time.sleep(1)
		#сохранение страницы браузера
		name = f'Page{x}.html'
		webUrl = save(name)
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
			pyautogui.moveTo(1250, 700)
			print(f"item №{y}")
			solo = item.find('a', class_ = 'Link__StyledLink-sc-4b9qcv-0')
			if solo != None: #проверка на не рекламный баннер
				#ссылка на продукт
				solo_link = solo.get('href')
				html_status = get_html(solo_link)
				if html_status.status_code == 200:
					webbrowser.open(solo_link)
					time.sleep(5)
					#сохранение страницы продукта
					name = f"Product{y}.html"
					file_product = save(name)
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
					#чистка браузера
					pyautogui.hotkey('ctrl', 'w')
			#это реклама
			else:
				print("this is an advertisement")
			y += 1
		#конец цикла продуктов
		pyautogui.moveTo(1250, 700)
		pyautogui.hotkey('ctrl', 'w')
		webbrowser.open(page)
		x += 1
	return products

#функция вызова парсера
def btn_parse_click():
	#проверка url
	URL = btn_search_click()
	html = get_html(URL)
	pyautogui.moveTo(1250, 700)
	if html.status_code == 200:
		#парсинг
		result = get_content()
		print(f"Получено {len(result)} товаров")
		#удаление временных файлов
		for root, dirs, files in os.walk('C:/Users/Юлиан/Юлиан/Разное/parser/pages'):
		    for f in files:
		        os.unlink(os.path.join(root, f))
		    for d in dirs:
		        shutil.rmtree(os.path.join(root, d))
	else:
		print('Error')
	
#кнопка вызова парсера
btn_parse = Button(frame, text = "parse", command = btn_parse_click)
btn_parse.pack()


#app = Application(master=root)
root.mainloop()
