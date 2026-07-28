import os

LANG = 'ru'
PATH = 'locales'

class phrases(): pass

def load_yaml(lang):
    global phrases
    filepath = os.path.join(PATH, f'{lang}.yaml')
    with open(filepath, 'r', encoding='UTF-8') as file:
        for line in file:
            try:
                i = line.index(':')
                key = line[:i].strip()
                value = line[i+1:].strip().replace('\\n', '\n')
                setattr(phrases, key, value)
            except ValueError: continue

load_yaml(LANG)