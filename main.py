import requests
from bs4 import BeautifulSoup
import psycopg2

url = 'https://nedradv.ru/nedradv/ru/auction'

html_code = requests.get(url).text

soup = BeautifulSoup(html_code, 'html.parser')
auction_rows = soup.find_all('tr')[1:]

data = []

for row in auction_rows:

    cells = row.find_all('td', style='text-align:left;')
    hyper_link = 'https://nedradv.ru/' + row.find('a',  attrs={"class": 'g-color-gray-dark-v1'}).get('href')
    date = cells[0].a.text.strip() if cells and cells[0].a else "N/A"
    lot = cells[1].a.text.strip() if cells and cells[1].a else "N/A"
    region = cells[2].a.text.strip() if cells and cells[2].a else "N/A"
    status = cells[3].a.text.strip() if cells and cells[3].a else "N/A"


    hyper_info = requests.get(hyper_link).text
    detail = BeautifulSoup(hyper_info, 'html.parser')

    # Extracting the deadline for submitting applications
    deadline_element = detail.find('dt', string='Срок подачи заявок')
    deadline = deadline_element.find_next('dd', class_='col-sm-9').get_text() if deadline_element else "N/A"

    # Extracting the participation fee for the auction
    participation_fee_element = detail.find('dt', string='Взнос за участие в аукционе (руб)')
    participation_fee = participation_fee_element.find_next('dd', class_='col-sm-9').get_text() if participation_fee_element else "N/A"

    # Extracting the organizer
    organizator_element = detail.find('dt', string='Организатор')
    organizator = organizator_element.find_next('dd', class_='col-sm-9').get_text() if organizator_element else "N/A"
 

    data_dict = {
        "date": date,
        'lot': lot,
        'hyper_link': hyper_link,
        'region' : region,
        'status': status,
        'deadline': deadline,
        'participation_fee': participation_fee,
        'organizator': organizator

    }

    data.append(data_dict)


# Подключение к базе данных
conn = psycopg2.connect(
    host="ваш_хост",
    database="ваша_база_данных",
    user="ваш_пользователь",
    password="ваш_пароль"
)

# Создание курсора для выполнения SQL-запросов
cur = conn.cursor()

# SQL-запрос для создания таблицы (если она еще не существует)
create_table_query = """
    CREATE TABLE IF NOT EXISTS auction_data (
        id SERIAL PRIMARY KEY,
        date VARCHAR(100) NOT NULL,
        lot VARCHAR(200) NOT NULL,
        hyper_link VARCHAR(200) NOT NULL,
        region VARCHAR(100),
        status VARCHAR(50),
        deadline VARCHAR(100),
        participation_fee VARCHAR(100),
        organizator VARCHAR(100)
    )
"""
cur.execute(create_table_query)
conn.commit()

# Вставка записей из списка словарей
for item in data:
    insert_query = "INSERT INTO auction_data (date, lot, hyper_link, region, status, deadline, participation_fee, organizator) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(insert_query, (item['date'], item['lot'], item['hyper_link'], item['region'], item['status'], item['deadline'], item['participation_fee'], item['organizator']))

# Сохранение изменений и закрытие курсора и соединения
conn.commit()
cur.close()
conn.close()




    

    









