import sqlite3
import os.path
import sys

def main():
    """топ 10 фильмов, у которых количество рекомендаций не меньше N и количество проголосовавших не меньше M,
    где N и M - аргументы командной строки."""
    if len(sys.argv) != 3:
        print("неправильное число аргументов")
        return ''
    try:
        n = int(sys.argv[1])
        m = int(sys.argv[2])
    except:
        print('аргументы должны быть целыми числами!')
        return ''
    films_list = []
    if os.path.isfile('films.db'):
        with sqlite3.connect('films.db') as conn:
            c = conn.cursor()
            c.execute("SELECT film_name FROM films WHERE recommend_count >= ? and votes >= ? "
                      "ORDER BY recommend_count + votes DESC LIMIT 10",
                      (n, m))
            films_list = [film_name[0] for film_name in c.fetchall()]
    else:
        print('для начала вам необходимо создать файл и заполнить его информацией о фильмах')
    return films_list

if __name__ == '__main__':
    top_ten_films = main()
    for film in top_ten_films:
        print(film)