import requests
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup

URL = 'http://www.fast-torrent.ru/most-films/'

def get_html(url):
    return requests.get(url).content.decode(encoding='utf-8')

def parse_html(content):
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
    url = "{0}{1}.html".format(URL, number)
    return parse_html(get_html(url))

if __name__ == '__main__':
    pool = Pool(10)
    res = pool.map(work, range(1, 11))
    for i in res:
        print(i)