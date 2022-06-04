import json
import os


# create folders for path
def create_folders(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


# load dict from json file
def load_dict(path):
    create_folders(path)

    # load dict or create empty
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as inp:
            return json.load(inp)
    else:
        save_dict(path, {})
        return {}


# save dict to json file
def save_dict(path, dict_):
    create_folders(path)
    with open(path, "w", encoding="utf-8") as out:
        json.dump(dict_, out, sort_keys=True, indent=4, ensure_ascii=False)


class EmojiDict:
    updated_emojis = set()  # set of emojis for which words have been added

    def __init__(self, lang="en", empty=False, path=""):
        self.lang = lang
        self.dict_path = path + "data/emojidict_{0}.json".format(lang)
        self.dict_reverse_path = path + "data/emojidict_{0}_reverse.json".format(lang)

        if empty:
            self.dict_json = {}
            self.dict_reverse_json = {}
        else:
            self.dict_json = load_dict(self.dict_path)
            self.dict_reverse_json = load_dict(self.dict_reverse_path)

    def add(self, emoji, words):
        if emoji in self.dict_json:
            self.dict_json[emoji] = list(set(self.dict_json[emoji] + words))
        else:
            self.dict_json[emoji] = words

        self.updated_emojis.add(emoji)

    def save(self):
        save_dict(self.dict_path, self.dict_json)
        save_dict(self.dict_reverse_path, self.dict_reverse_json)

    def get_dict(self):
        return self.dict_json

    def get_dict_reverse(self):
        return self.dict_reverse_json

    def get_words(self, emoji):
        if emoji in self.dict_json:
            return self.dict_json[emoji]
        else:
            return []

    def get_emojis(self, word):
        if word in self.dict_reverse_json:
            return self.dict_reverse_json[word]
        else:
            return []

    def update_reverse(self, use_all=False):
        if use_all:
            self.updated_emojis = self.dict_json.keys()

        # check each updated emoji
        for e in self.updated_emojis:
            # check each word from selected emoji
            for w in self.dict_json[e]:
                if w in self.dict_reverse_json:
                    if e not in self.dict_reverse_json[w]:
                        self.dict_reverse_json[w].append(e)
                else:
                    self.dict_reverse_json[w] = [e]

        self.updated_emojis = set()
