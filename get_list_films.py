import requests
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup

URL = 'http://www.fast-torrent.ru/most-films/'

def get_html(url):
    """получение html кода страницы"""
    r = requests.get(url)
    if r.status_code == 200:
        return r.content.decode(encoding='utf-8')
    else:
        return ''

def parse_html(content):
    """извлечение необходимых данных из html кода страницы"""
    result_list = []
    soup = BeautifulSoup(content, "html.parser")
    films_content = soup.find_all("div", itemtype="http://schema.org/Movie")
    for film in films_content:
        result = {}
        name_year = film.find_all("h2")[0]
        result['name'] = name_year.find("span").text
        result['year'] = str(name_year).split("span>  (")[1].split(")")[0]
        film_info = film.find_all(class_="film-info")[0]
        try:
            result['recommend_count'] = int(film_info.find("span", class_="recommend_count").text.split(" ")[1])
        except IndexError:
            result['recommend_count'] = 0
        result['votes'] = int(film_info.find("em", class_="inline-rating")['votes'])
        result['average_votes'] = float(film_info.find("em", class_="inline-rating")['average'])
        result_list.append(result)
    return result_list

def work(number):
    """вызов функции parse_html для страницы номер number"""
    url = "{0}{1}.html".format(URL, number)
    return parse_html(get_html(url))

def main():
    """основная функция, которая получает необходимую информация о фильмах с первых 10 страниц"""
    pool = Pool(10)
    res = pool.map(work, range(1, 11))
    for page in res:
        for film in page:
            print(film)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()