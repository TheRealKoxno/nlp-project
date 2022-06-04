import string
import requests
from bs4 import BeautifulSoup
from ..emojidict import EmojiDict
import nltk
import spacy


def parse_categories():
    emojis = []
    categories = ["people", "nature", "food-drink", "activity", "travel-places", "objects", "symbols", "flags"]
    for c in categories:
        r = requests.get("https://emojipedia.org/{0}/".format(c))
        soup = BeautifulSoup(r.text, features="html.parser")
        emoji_list = soup.find("ul", {"class": "emoji-list"})
        lis = emoji_list.find_all("a")
        for li in lis:
            emojis.append(li["href"] + "\n")
    print(emojis)
    with open("emojipedia_links.txt", "w") as out:
        out.writelines(emojis)


def parse_emojis():
    nlp = spacy.load("en_core_web_sm")
    ed_en = EmojiDict(empty=True, path="../../")
    with open("emojipedia_links.txt", "r") as inp:
        emojis_links = inp.readlines()
    for e in emojis_links:
        link = "https://emojipedia.org{0}".format(e[:-1])
        print(link)
        r = requests.get(link)
        soup = BeautifulSoup(r.text, features="html.parser")

        # symbol and main name
        spl = soup.find("h1").text.split()
        emoji_symbol, names = spl[0], [" ".join(spl[1:])]

        # add 'also known as' and 'apple names'
        for c in ["aliases", "applenames"]:
            section = soup.find("section", {"class": c})
            if section:
                # remove symbol from every name start
                names += [" ".join(a.text.split()[1:]) for a in section.find_all("li")]

        # codes = soup.find("div", {"class": "ad-below-images"}).find_next("ul").find_all("a")
        # unis = []
        # # one emoji can consist of more than 1 unicode
        # for c in codes:
        #     uni = c.text[4:]
        #     # from format U+1F686 to unicode char
        #     uni = "0" * ((4 - len(uni) % 4) % 4) + uni
        #     unis.append(chr(int(uni, 16)))
        # emoji = "".join(unis)
        # print(emoji)

        # get unicode number from symbol
        emoji_symbol_code = emoji_symbol.encode("unicode-escape").decode("ASCII")
        print(emoji_symbol, emoji_symbol_code)
        print(names)

        # split names to words
        words = nltk.tokenize.word_tokenize(" ".join(names))

        # remove punctuation and stop words
        remove = nltk.corpus.stopwords.words("english") + list(string.punctuation)
        words = [w.lower() for w in words if w.lower() not in remove and len(w) > 1]
        #print(words)

        # tag words as nouns, verbs, adjectives, adverbs
        words = nltk.pos_tag(words)
        #print(words)
        # used to convert tags to 'pos' arg in lemmatize() function
        tags_dict = {"N": "n", "V": "v", "J": "a", "R": "r"}
        wnl = nltk.stem.wordnet.WordNetLemmatizer()
        # w[0] - word, w[1] - tag
        # uses tag's first letter to set 'pos' arg
        words = list(set([wnl.lemmatize(w[0], tags_dict[w[1][0]]) for w in words if w[1][0] in tags_dict]))
        print(words)

        # words_spacy = nlp(" ".join(names).lower())
        # words_spacy = [w.lemma_ for w in words_spacy]
        # words_spacy = list(set([w.lower() for w in words_spacy if w.lower() not in remove and len(w) > 1]))
        # print(words_spacy)

        # add to dictionary
        ed_en.add(emoji_symbol, words)
        ed_en.update_reverse()
        ed_en.save()

    ed_en.update_reverse()
    ed_en.save()


parse_emojis()
