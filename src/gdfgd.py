from pymorphy2 import MorphAnalyzer
from emojidict import EmojiDict

dic = EmojiDict(lang = 'ru')
print(dic.lang)
text = 'рука'
print(text)
emojis = dic.get_emojis(text)
print(emojis)
