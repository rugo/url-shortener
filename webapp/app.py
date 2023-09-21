from flask import Flask, request, render_template, redirect
from pathlib import Path
import random
import logging as log
import os

rng = random.SystemRandom()

app = Flask(__name__)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def read_wordlist(file_path):
    return [x.strip() for x in open(file_path).readlines()]


WORD_LIST_ARTICLE = read_wordlist("wordlists/articles.txt")
WORD_LIST_ADJECTIVE = read_wordlist("wordlists/adjectives.txt")
WORD_LIST_NOUN = read_wordlist("wordlists/nouns.txt")


def random_phrase():
    art = rng.choice(WORD_LIST_ARTICLE)
    adj = rng.choice(WORD_LIST_ADJECTIVE)
    noun = rng.choice(WORD_LIST_NOUN)

    return "-".join((art, adj, noun))


class Database:

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        assert self.base_dir.is_dir()

    def create_entry(self, entry_name, url):
        entry_path = self.base_dir / entry_name

        if entry_path.exists():
            raise ValueError(f"Entry >{entry_name}< already exists!")

        entry_path.open("w").write(url)

    def read_entry(self, entry_name):
        entry_path = self.base_dir / entry_name

        if not str(entry_path.absolute()).startswith(str(self.base_dir.absolute())):
            raise ValueError(f"Invalid path: {entry_path}")

        if not entry_path.is_file():
            raise ValueError(f"Entry >{entry_path}< does not exist.")

        return entry_path.open().read()


db = Database("db")


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")


@app.route('/create', methods=["POST"])
def create():
    url = request.form.get("url")

    for _ in range(10):
        try:
            phrase = random_phrase()
            db.create_entry(phrase, url)
            break
        except ValueError:
            pass
    else:
        log.error("Error when trying to create phrase. All out of words?")
        return "No phrases seem to be left...", 500

    return render_template("create.html", base_url=BASE_URL, mnemonic=phrase, url=url)


@app.route('/<art>-<adj>-<noun>', methods=["GET"])
def redirect_to_url(art, adj, noun):
    if not (art.isalpha() or adj.isalpha() or noun.isalpha()):
        return "Invalid phrase", 400

    entry = f"{art}-{adj}-{noun}"

    try:
        url = db.read_entry(entry)
    except ValueError as ex:
        log.info("Exception: %s", ex)
        return "This phrase does not exist", 404

    return redirect(url)


if __name__ == '__main__':
    app.run()
