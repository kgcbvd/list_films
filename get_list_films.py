import requests
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
import sqlite3
import os.path

"""
Скрипт, получает список фильмов с первых 10 страниц сайта http://www.fast-torrent.ru/most-films/.
Получает название фильма, год выпуска, рейтинг(оценка и количество голосов, количество рекомендаций).
Полученные данные схраняются в файл films.db. При перезаписи файла, если в нем уже присутствует такой фильм,
то данные обновляются. Если фильма не было, то он добавляется.
"""

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

def save_db(data):
    """функция открывает файл films.db и добавляет в него информацию о фильме, если его нет или обновляет информацию,
    если файл не существует, то создаем его и таблицу films"""
    if not os.path.isfile('films.db'):
        with sqlite3.connect('films.db') as conn:
            c = conn.cursor()
            c.execute("CREATE TABLE films "
                      "(film_name TEXT NOT NULL, year TEXT NOT NULL, average_votes DOUBLE DEFAULT 0.0, "
                      "votes INT DEFAULT 0, recommend_count INT DEFAULT 0)")
            conn.commit()

    with sqlite3.connect('films.db') as conn:
        c = conn.cursor()
        c.execute("SELECT film_name FROM films")
        films_name_db = [name[0] for name in c.fetchall()]
        for page_films in data:
            for film in page_films:
                if film['name'] not in films_name_db:
                    c.execute("INSERT INTO films VALUES (?, ?, ?, ?, ?)",
                              (film['name'], film['year'], film['average_votes'],
                               film['votes'], film['recommend_count']))
                    conn.commit()
                    print("фильм \"{0}\" добавлен".format(film['name']))
                else:
                    c.execute("SELECT votes, recommend_count FROM films WHERE film_name = ?", (film['name'],))
                    votes, recommend_count = c.fetchall()[0]
                    if film['votes'] != int(votes) or film['recommend_count'] != int(recommend_count):
                        c.execute("UPDATE films SET average_votes = ?, votes = ?, recommend_count = ? "
                                  "WHERE film_name=?",
                                  (film['average_votes'], film['votes'], film['recommend_count'], film['name']))
                        conn.commit()
                        print("информация о фильме \"{0}\" обновлена".format(film['name']))
    return ''

def main():
    """Функция, которая получает необходимую информация о фильмах с первых 10 страниц"""
    pool = Pool(10)
    res = pool.map(work, range(1, 11))
    save_db(res)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()