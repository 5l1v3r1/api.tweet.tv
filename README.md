How to install?
===============

```
$ git clone --recursive git@github.com/mahendrakalkura/api.tweet.tv .
$ cd api.tweet.tv
$ mkvirtualenv api.tweet.tv
$ pip install -r requirements.txt
$ polyglot download embeddings2.en
$ polyglot download ner2.en
$ python -m textblob.download_corpora
```

How to run?
===========

```
$ cd api.tweet.tv
$ workon api.tweet.tv
$ python api.py {{url}}
```
