import pymorphy2
from textblob import TextBlob, Word
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import random
from pymorphy2 import MorphAnalyzer
from emojidict import EmojiDict


def lemmatize_text(tok_text, lang):
    if lang == 'eng':
        sent = TextBlob(tok_text)
        tag_dict = {"J": 'a',
                    "N": 'n',
                    "V": 'v',
                    "R": 'r'}
        words_and_tags = [(w, tag_dict.get(pos[0], 'n')) for w, pos in sent.tags]
        for i, wd_pos in enumerate(words_and_tags):
            if wd_pos[0].endswith('y') and wd_pos[1] == 'a':
                words_and_tags[i] = (TextBlob(wd_pos[0][:-1]).words[0], 'n')
        return [wd.lemmatize(tag) for wd, tag in words_and_tags]
    else:
        morph = MorphAnalyzer()
        token_text = tok_text.split(' ')
        for i, wd in enumerate(token_text):
            token_text[i] = morph.normal_forms(wd)[0]
        return token_text

def get_lemmas_symbs(text, lang):
    temp_word = ''
    temp_symbols = ''
    token_text, symbs = [], []
    state = True if text[0].isalpha() else False
    is_let_1 = state

    for i in text:
        if i.isalpha() and state:
            temp_word = temp_word + i
        elif not (i.isalpha()) and state:
            token_text.append(temp_word)
            temp_word = ''
            temp_symbols = temp_symbols + i
            state = False

        elif not (i.isalpha()) and not (state):
            temp_symbols = temp_symbols + i
        elif i.isalpha() and not (state):
            symbs.append(temp_symbols)
            temp_symbols = ''
            temp_word = temp_word + i
            state = True
    if state:
        token_text.append(temp_word)
    else:
        symbs.append(temp_symbols)
    lemat_token_text = lemmatize_text(' '.join(token_text), lang)
    return lemat_token_text, token_text, symbs, state

def merge_tokens(lemat_token_text, token_text, symbs, state, dic):
    for i, tok in enumerate(lemat_token_text):
        emojis = dic.get_emojis(tok)
        if emojis: lemat_token_text[i] = emojis[random.randint(0, len(emojis) - 1)] * 3
        else: lemat_token_text[i] = ''

    full_sent = []
    while token_text or symbs:
        if state:
            tok = token_text.pop()
            emoj = lemat_token_text.pop()
            full_sent.insert(0, tok + emoj)
            state = False
        elif not (state):
            sym = symbs.pop()
            full_sent.insert(0, sym)
            state = True
        else:
            break
    return ''.join(full_sent)

def check_lang(text):
    eng, ru = 'abcdefghijklmnopqrstuvwxyz', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    eng_cnt, ru_cnt = 0, 0
    for symb in text:
        if symb in eng: eng_cnt += 1
        elif symb in ru: ru_cnt += 1
        else: continue
    return 'eng' if eng_cnt > ru_cnt else 'ru'

###########################
# text = "The striped bats are, hanging on their - feet for best."
text = 'Супер вафли по акции'
lang = check_lang(text)
if lang == 'eng': dic = EmojiDict()
else: dic = EmojiDict(lang = 'ru')

lemat_token_text, token_text, symbs, state = get_lemmas_symbs(text, lang)
emoji_text = merge_tokens(lemat_token_text, token_text, symbs, state, dic)


