import string
import requests
from bs4 import BeautifulSoup
from mipt_nlp_nogotochki_project.emojidict import EmojiDict
import nltk
import spacy


def parse_links():
    r = requests.get("https://hotemoji.com/emoji-meanings.html")
    soup = BeautifulSoup(r.text, features="html.parser")
    content = soup.find("div", {"id": "content"})
    links = [a["href"] + "\n" for a in content.find_all("a") if ".html" in a["href"]]
    print(links)
    with open("hotemoji_links.txt", "w", encoding="utf-8") as out:
        out.writelines(links)


def parse_emojis():
    nlp = spacy.load("ru_core_news_sm")
    ed_ru = EmojiDict(lang="ru", empty=False, path="../../")
    with open("hotemoji_links.txt", "r", encoding="utf-8") as inp:
        emojis_links = inp.readlines()
    for e in emojis_links[1721:]:
        link = "https://hotemoji.com/{0}".format(e[:-1])
        print(link)
        r = requests.get(link)
        soup = BeautifulSoup(r.text, features="html.parser")

        emoji_symbol = soup.find("h1", {"class": "first-emoji"}).text.split()[0]
        emoji_symbol = emoji_symbol.replace("️", "")
        print(emoji_symbol)

        # get name and keywords
        russian = soup.find("tbody").find_all("tr")[2].find_all("td")
        names = [russian[1].text] + russian[2].text.split(", ")
        print(names)

        # split names to words
        words = nlp(" ".join(names).lower())
        words = [w.lemma_ for w in words]
        print(words)

        # remove punctuation and stop words
        remove = nltk.corpus.stopwords.words("russian") + list(string.punctuation)
        words = list(set([w.lower() for w in words if w.lower() not in remove and len(w) > 1]))
        print(words)

        # # tag words as nouns, verbs, adjectives, adverbs
        # words = nltk.pos_tag(words)
        # print(words)
        # # used to convert tags to 'pos' arg in lemmatize() function
        # tags_dict = {"N": "n", "V": "v", "J": "a", "R": "r"}
        # wnl = nltk.stem.wordnet.WordNetLemmatizer()
        # # w[0] - word, w[1] - tag
        # # uses tag's first letter to set 'pos' arg
        # words = list(set([wnl.lemmatize(w[0], tags_dict[w[1][0]]) for w in words if w[1][0] in tags_dict]))

        # # add to dictionary
        ed_ru.add(emoji_symbol, words)
        ed_ru.update_reverse()
        ed_ru.save()

    ed_ru.update_reverse()
    ed_ru.save()

parse_emojis()