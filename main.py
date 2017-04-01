# -*- coding: utf-8 -*-

from pprint import pprint
from re import sub
from string import punctuation
from sys import argv
from urlparse import urlparse
from warnings import simplefilter

from bs4 import BeautifulSoup
from newspaper import Article
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer
from polyglot.text import Text
from readability import Document
from stop_words import get_stop_words
from textblob import TextBlob
from unidecode import unidecode

simplefilter(action='ignore', category=FutureWarning)


def remove_punctuation(text):
    if isinstance(text, unicode):
        return unidecode(text).translate(None, punctuation)
    return text


WORD_NET_LEMMATIZER = WordNetLemmatizer()

WORDS = words.words()

STOPWORDS = get_stop_words('en')
STOPWORDS = [remove_punctuation(stop_word) for stop_word in STOPWORDS]


# Keywords


def keywords_remove_duplicates(keywords, phrases):
    for phrase in phrases:
        phrase = phrase.split()
        results = [True if p in keywords else False for p in phrase]
        if all(results):
            for keyword in phrase:
                if keyword in keywords:
                    keywords.remove(p)
    return keywords


def keywords_has_generic(keywords):
    for keyword in keywords:
        if keywords_is_generic(keyword):
            return True
    return False


def keywords_is_generic(keyword):
    if keyword in WORDS:
        return True
    n = WORD_NET_LEMMATIZER.lemmatize(keyword, 'n')
    if n in WORDS:
        return True
    v = WORD_NET_LEMMATIZER.lemmatize(keyword, 'v')
    if v in WORDS:
        return True
    return False


# Phrases


def phrases_clean(phrase):
    phrase = phrase.split(' ')
    if len(phrase) == 1:
        return
    keywords = keywords_has_generic(phrase)
    if not keywords:
        return
    phrase = ' '.join(phrase)
    return phrase


# Texts


def texts_clean(text):
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    text = sub(r'[ ]+', ' ', text)
    text = text.strip()
    return text


# Others

def get_hostname(url):
    try:
        return urlparse(url).hostname
    except Exception:
        pass
    return ""


def is_stopword(keyword):
    if keyword.lower() in STOPWORDS:
        return True
    return False


# Top Level


def get_title(article):
    title = article.title
    return title


def get_text(article):
    text = article.text
    text = texts_clean(text)
    return text


def get_entities(text):
    text = Text(text)
    entities = text.entities
    entities = [' '.join(entity) for entity in entities]
    entities = [remove_punctuation(entity) for entity in entities]
    entities = filter(None, entities)
    entities = [entity for entity in entities if not is_stopword(entity)]
    entities = set(entities)
    entities = list(entities)
    return entities


def get_phrases(text, entities):
    text_blob = TextBlob(text)
    phrases = text_blob.noun_phrases
    phrases = [phrase.string for phrase in phrases]
    phrases = [remove_punctuation(phrase) for phrase in phrases]
    phrases = [phrases_clean(phrase) for phrase in phrases]
    phrases = filter(None, phrases)
    entities = [entity.lower() for entity in entities]
    phrases = [phrase for phrase in phrases if phrase not in entities]
    phrases = set(phrases)
    phrases = list(phrases)
    return phrases


def get_keywords(article, phrases):
    keywords = article.keywords
    keywords = [
        keyword
        for keyword in keywords
        if not is_stopword(keyword) and not keywords_is_generic(keyword)
    ]
    keywords = keywords_remove_duplicates(keywords, phrases)
    return keywords


def get_urls(contents, url, urls):
    hostname = get_hostname(url)
    anchors = BeautifulSoup(contents, 'lxml').findAll('a')
    hrefs = anchors
    hrefs = [href.get('href') for href in hrefs]
    hrefs = filter(None, hrefs)
    hrefs = [
        href
        for href in hrefs
        if href.startswith('http') and get_hostname(href) == hostname
    ]
    hrefs = [href for href in hrefs if href not in urls]
    return urls


# Main


def main(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    document = Document(article.html)
    summary = document.summary()
    content = document.content()

    title = get_title(article)
    text = get_text(article)
    entities = get_entities(text)
    phrases = get_phrases(text, entities)
    keywords = get_keywords(article, phrases)
    urls_primary = get_urls(summary, url, [])
    urls_secondary = get_urls(content, url, urls_primary)

    return {
        'title': title,
        'text': text,
        'entities': entities,
        'keywords': keywords,
        'phrases': phrases,
        'urls': {
            'primary': urls_primary,
            'secondary': urls_secondary,
        },
    }


if __name__ == '__main__':
    pprint(main(argv[1]))
