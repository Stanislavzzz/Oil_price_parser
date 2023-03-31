# Парсер дневных итогов рыночной цены нефтепродуктов
# Была выбрана следующая стратегия:
# После анализа кода сайта была найдена закономерность генерации динамических страниц с данными таблицами
# Получил общее кол-во таблиц на сайте, и собрал все ссылки с этих страниц на excel файлы
# Считал нужные данные из таблицы и сохранил, для удобства, в DataFrame.
# В дальнейшем, если будет много данных, то обработать Pandas'ом будет легче
# После вывел график и, как наиболее удобный вариант для теста, сохранил данные в таблице excel
# Рядом сохранил созданный график
# Ряд тестов и проверок не делал.
# Чтоб был ясен ход мыслей, то не стал сильно "сжимать" код и городить однострочники.
# Сделал задел на будущие доработки.
# При необходимости, можно сделать. Добавить графический интерфейс, добавить универсальности.
# Сделать возможность сохранять в базе данных

# Импортируем нужные библиотеки
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tqdm import tqdm


# Получаем общее кол-во страниц
def find_number_of_pages(soup_data):
    # table = soup_data.find_all('div', attrs={'class': ['bx-pagination-container']})
    c_page = soup_data.find('div', class_='bx-pagination-container').find('ul').find_all('li')[5].find('a').find('span')
    count_page = int(c_page.text)
    return count_page


# Считываем данные с excel
def read_excel(url_file):
    df = pd.read_excel(url_file, skiprows=6)
    d1 = df[df['Код\nИнструмента'] == 'A592UFM060F']['Unnamed: 11']
    cell_price = int(d1.iloc[0])
    return cell_price


# Парсим ссылки и даты
def parse_excel(url, base_url, count_page):
    list_href = []
    list_date = []
    date_formatter = "%d.%m.%Y"
    print('Парсим данные')
    for number_page in tqdm(range(1, count_page)):
        extra_url = url + '?page=page-' + str(number_page)
        html = requests.get(extra_url).text
        soup = bs(html, 'html.parser')
        table_href = soup.find_all('a', attrs={'class': ['accordeon-inner__item-title', 'link', 'xls']})
        table_date = soup.find_all('div', class_='accordeon-inner__item-inner__title')
        for tbl in table_href[1: 11]:
            href = tbl.get('href')
            file_url = base_url + href
            list_href.append(file_url)
        for tbl_d in table_date[1: 11]:
            if tbl_d != table_date[10]:
                date_string = tbl_d.find('p').find('span').get_text()
                date_date = datetime.strptime(date_string, date_formatter)
            else:
                date_date = list_date[-1] - timedelta(days=1)
            list_date.append(date_date)
    return list_date, list_href


# Получаем цены
def fill_href_list_to_price(href_list_to_price):
    list_price = []
    print('Загружаем данные из таблиц')
    for el in tqdm(href_list_to_price):
        # print(f'{t_r} - {tabel_result[t_r]}')
        price = read_excel(el)
        list_price.append(price)
    return list_price


# Создали DataFrame
def fill_df(date_lst, price_lst):
    data = {'date': date_lst, 'price': price_lst}
    df_filled = pd.DataFrame(data)
    return df_filled


# Сохраняем таблицу
def save_table(df_result):
    time_now = datetime.now().strftime("%d-%m-%Y-%H_%M")
    file_name = 'result_price_table' + str(time_now) + '.xlsx'
    image_name = 'result_price_graph' + str(time_now) + '.jpg'
    writer = pd.ExcelWriter(file_name)
    df_result.to_excel(writer)
    writer.save()
    print(f'Данные cохранили в Excel файл {file_name}')
    return image_name


# Строим график
def show_graph(df_result, name_save_image):
    df_result.plot(x='date', y='price', rot=0, figsize=(14, 10), grid=True, marker='o')
    plt.savefig(name_save_image)
    plt.title("Изменение рыночной цены на нефтепродукты")
    plt.xlabel("Даты")
    plt.ylabel("Рыночная цена")
    print(f'Изображение сохранили с именем {name_save_image}')
    plt.show()


# Стартовое сообщение
def print_parser(msg):
    print(f'{msg}')


def main():
    print('-*' * 30)
    print_parser('Парсер дневных итогов рыночной цены нефтепродуктов')
    url = 'https://spimex.com/markets/oil_products/trades/results/'
    base_url = 'https://spimex.com'
    html = requests.get(url).text
    soup = bs(html, 'html.parser')
    print('-*' * 30)
    number_of_pages = find_number_of_pages(soup)
    print(f"Всего найдено записей - {number_of_pages} ")
    number_of_pages = 300
    print(f"Что бы долго не ждать - обработаем {number_of_pages} записей")
    print('-*' * 30)

    table_result = parse_excel(url, base_url, int(number_of_pages // 10 + 1))
    date_list = table_result[0]
    href_list = table_result[1]

    price_list = fill_href_list_to_price(href_list)
    print('-*' * 30)
    df_result = fill_df(date_list, price_list)
    print('-*' * 30)
    print('Вывод полученных дат и цен')
    print(df_result)
    print('-*' * 30)
    name_image = save_table(df_result)
    print('-*' * 30)
    show_graph(df_result, name_image)
    print('-*' * 30)

if __name__ == '__main__':
    main()


print('Внесли  изменения')