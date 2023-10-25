# импорты

from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize

import re
import sqlite3
import requests
import spacy

# В анекдотах на сайте была беда со знаками препинания, в ф-ии text_nrmlz наводим порядок в тексте

def text_nrmlz(text):
    text = text.replace('\n', '')
    text = text.replace('-', '—')
    text = text.replace(':—', ':')
    text = text.replace('\xa0', '')
    text = re.sub(r'([.,!?]) *', r'\1 ', text)
    text = re.sub(r'([.!?]) »', r'\1»', text)
    text = re.sub(r'([.!?]) "', r'\1"', text)
    text = re.sub(r'\.{3,}', '... ', text)
    text = re.sub(r'(\.{3}) *', r'\1 ', text)
    text = re.sub(r' *([,.!?])', r'\1', text)
    text = re.sub(r'([0-9])\. *', r'\1.', text)
    text = text.replace('Это длинный анекдот, будьте осторожны!', '')

    return text

# Ф-ия anecdotes_parser_1 парсит сайт№1 с анекдотами, создает для каждого анекдота словарь с id, ссылкой и текстом анекдота
# Словари добавляются в общий список meta_list

def anecdotes_parser_1(index, ml):
    url = f'https://megapanoptikum.info/tags/%D0%B4%D0%BB%D0%B8%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%B0%D0%BD%D0%B5%D0%BA%D0%B4%D0%BE%D1%82%D1%8B/page/{i}/#list'
    request = requests.get(url)

    if request.status_code == 200:
        req = session.get(url)
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')
        anecdotes = soup.find_all('article', {'class': "story shortstory lefticons shadow"})

        c = (index - 1) * 10
        for smth in anecdotes:
            title = smth.find('h2', {'class': 'title ultrabold'})
            block = {'text_id': c, 'source': title.find('a').attrs['href'],
                     'text': text_nrmlz(smth.find('div', {'class': 'text'}).text)
                     }

            ml.append(block)
            c += 1

    return ml

# Ф-ия anecdotes_parser_2 парсит сайт№2 с анекдотами, создает для каждого анекдота словарь с id, ссылкой и текстом анекдота
# Словари добавляются в общий список meta_list

def anecdotes_parser_2(c, ml):

    url = 'http://anekdot.me/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%94%D0%BB%D0%B8%D0%BD%D0%BD%D1%8B%D0%B5_%D0%B0%D0%BD%D0%B5%D0%BA%D0%B4%D0%BE%D1%82%D1%8B'
    req = session.get(url)

    if req.status_code == 200:
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')

        links_groups = soup.find_all('div', {'class': "mw-category-group"})
        for group in links_groups:
            links = group.find_all('a')
            for link in links:
                c += 1
                url = 'http://anekdot.me' + link.attrs['href']
                req = session.get(url)
                anec = req.text
                soup = BeautifulSoup(anec, 'html.parser')
                block = {'text_id': c, 'source': url,
                         'text': text_nrmlz(soup.find('div', {'class': "anekdot-centred-text"}).text)
                         }

                ml.append(block)

    return ml

# Ф-ия sent_word каждый анекдот делит на предложения, а предложения на слова,
# добавляет информацию о предложениях и словах в соответсвующие словари

def sent_word(i_meta, sl, wl):
    # начинаем нумерацию пр-й с 0 в каждом анекдоте
    sent_count = 0
    t = i_meta['text']
    # Проводим замену, чтобы sent_tokenize не разбивал прямую речь на предложения
    t = t.replace('! —', '!—')
    t = t.replace('? —', '?—')

    for s in sent_tokenize(t):
        # обратная замена
        s = s.replace('!—', '! —')
        s = s.replace('?—', '? —')
        if s[0] in '»!?':
            s = s[2:]

        if re.search(r'\w', s) is not None:
            # для каждого предложения создаем словарь и сохраняем его в список пр-й
            sd = {'text_id': i_meta['text_id'], 'sent_id': sent_count, 'sent': s}
            sl.append(sd)

            # начинаем нумерацию слов с 0 в каждом предложении
            word_count = 0
            for token in nlp(s):
                if token.text.isalpha():
                    # для каждого слова создаем словарь и сохраняем его в список слов
                    wd = {'text_id': i_meta['text_id'], 'sent_id': sd['sent_id'], 'word_id': word_count,
                          'word': token.text, 'lemma': token.lemma_, 'pos': token.pos_
                          }
                    wl.append(wd)
                    word_count += 1
            sent_count += 1

    return sl, wl


# Ф-ия data_to_db переносит информацию из списков meta_list, sent_list, word_list в базу данных 'anecdote.db'

def data_to_db(ml, sl, wl):
    for md in ml:
        cur.execute(
            """
            INSERT OR IGNORE INTO meta 
                (text_id, source, full_text) 
                VALUES (?, ?, ?)
            """, (
                md['text_id'], md['source'],
                md['text'])
        )

    for sd in sl:
        cur.execute(
            """
            INSERT OR IGNORE INTO sentences 
                (text_id, sent_id, sent) 
                VALUES (?, ?, ?)
            """, (
                sd['text_id'], sd['sent_id'],
                sd['sent'])
        )

    for wd in wl:
        cur.execute(
            """
            INSERT OR IGNORE INTO words 
                (text_id, sent_id, word_id, word, lemma, pos) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                wd['text_id'], wd['sent_id'],
                wd['word_id'], wd['word'],
                wd['lemma'], wd['pos'])
        )

    conn.commit()


session = requests.session()
meta_list, sent_list, word_list = [], [], []

# На сайте 8 страниц, пробегаемся по каждой из них циклом
for i in range(1, 9):
    anecdotes_parser_1(i, meta_list)

# В ф-ию парсинга второго сайта также передаем индекс последнего текста в meta_list, чтобы продолжать нумерацию
anecdotes_parser_2(meta_list[-1]['text_id'], meta_list)

nlp = spacy.load("ru_core_news_sm")

# Для каждого анекдота собираем информацию о предложениях и словах
for i in range(len(meta_list)):
    sent_list, word_list = sent_word(meta_list[i], sent_list, word_list)

# Создаем базу данных 'anecdote.db', состаящую из 3х таблиц
conn = sqlite3.connect('anecdote.db')
cur = conn.cursor()

# В таблице meta будет лежать информация о текстах (id, ссылка, сам текст)
cur.execute("""
CREATE TABLE IF NOT EXISTS meta 
(text_id INTEGER PRIMARY KEY, source text, full_text text)
""")

# В таблице sentences будет лежать информация о предложениях (id текста, id предложения в тексте, само предложение)
cur.execute("""
CREATE TABLE IF NOT EXISTS sentences
(text_id int, sent_id int, sent text) 
""")

# В таблице words будет лежать информация о словах (id текста, id предложения в тексте, id слова в предложении,
# слово, лемма, часть речи)
cur.execute("""
CREATE TABLE IF NOT EXISTS words
(text_id int, sent_id int, word_id int, word text, lemma text, pos text) 
""")

conn.commit()

# Заполняем таблицы данными
data_to_db(meta_list, sent_list, word_list)
