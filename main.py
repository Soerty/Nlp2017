#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")
import re
from itertools import islice
from itertools import tee

import wikipedia




class Preprocessing(object):
    """Базовый класс преобработки текста.
    Реализует основные методы преобработки.
    """
    
    def __init__(self, contents):
        self.frequency = {}
        self.contents = contents


    def _text_language_matching(self, lemmes):
        """Определяет к какому языку относится текст"""

        # В результате получится кортеж
        # Язык, у которого самое большое
        # число в значении и есть целевой язык
        result = {}

        # Обойти частотности слов по языкам
        for lang in self.frequency:
            result[lang] = 0
            # И обойти все леммы входного текста
            for lemm in lemmes:
                # Подсчитав сумму частот лемм текста
                if lemm in self.frequency[lang]:
                    result[lang] += self.frequency[lang][lemm]

        return result




class FrequencyMethod(Preprocessing):
    """Класс реализующий метод частотности слов.
    Наследуется от класса Preprocessing и использует
    некоторые его методы.
    """

    def result(self, text):
        """Возврашает результат определения языка"""

        # Составить словарь частотности для всех текстов
        for lang, texts in self.contents.items():
            texts = ' '.join(texts)
            words = [word.lower() for word in re.findall(r"(\w+)", texts, re.UNICODE)]
            self.frequency[lang] = {}
            for word in words:
                word = word.lower()
                if word in self.frequency[lang]:
                    self.frequency[lang][word] += 1
                else:
                    self.frequency[lang][word] = 1

        # Составить леммы для текста
        lemmes = [word.lower() for word in re.findall(r"(\w+)", str(text), re.UNICODE)]

        # Определить, какой это язык в тексте
        result = self._text_language_matching(lemmes)

        # Посчитать результат в процентах
        summ = sum(result.values())
        for lang, freq in result.items():
            result[lang] = round((freq / summ) * 100, 1)

        return result




class N_gramMethod(Preprocessing):
    """Класс реализующий метод частоты n-грамм.
    Наследует класс Preprocessing и использует его методы.
    """

    def __init__(self, contents, len_ngram=3):
        """Переопределяет констурктор базового класса"""
        self.n = len_ngram
        super(__class__, self).__init__(contents)


    def result(self, text):
        """Возврашает результат определения языка"""

        # Составить словарь частотности для всех текстов
        for lang, texts in self.contents.items():
            texts = ' '.join(texts)
            words = zip(*(islice(seq, index, None) for index, seq in enumerate(tee(texts, self.n))))
            words = [''.join(i) for i in words]
            self.frequency[lang] = {}
            for word in words:
                word = word.lower()
                if word in self.frequency[lang]:
                    self.frequency[lang][word] += 1
                else:
                    self.frequency[lang][word] = 1

         # Составить леммы для текста
        lemmes = zip(*(islice(seq, index, None) for index, seq in enumerate(tee(text, self.n))))
        lemmes =  [''.join(i) for i in lemmes]

        # Определить, какой это язык в тексте
        result = self._text_language_matching(lemmes)

        # Посчитать результат в процентах
        summ = sum(result.values())
        for lang, freq in result.items():
            result[lang] = round((freq / summ) * 100, 1)

        return result





def download_page(lang):
    """Вспомогательная функция которая
    скачивает рандомные статьи из википедии
    """
    wikipedia.set_lang(lang)
    page_name = wikipedia.random(1)

    try:
        page = wikipedia.page(page_name)
    except Exception:
                return None
    else:
        return page.content.replace('==', '')



def generate_content(langs, count):
    """Вспомошательная функция которая
    генерирует для каждого языка несколько страниц
    """
    contents = {}
    for lang in langs:
        contents[lang] = []
        for _ in range(count):
            page = download_page(lang)
            if page:
                contents[lang].append(page)

    return contents


def main():
    count_pages = 50
    ngram_length = 4
    langs = ['ru', 'uk', 'be', 'fr']
    contents = generate_content(langs, count_pages)
    random_page = download_page('ru')

    print ('Результат определения языка в процентах (для русского языка):')
    print ('Метод частотности:', FrequencyMethod(contents).result(random_page))
    print ('Метод n-грамм:', N_gramMethod(contents, ngram_length).result(random_page))



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
