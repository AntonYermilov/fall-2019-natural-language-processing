import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import re


TAGS = {'NOUN': 'S',
        'ADJF': 'A',
        'ADJS': 'A',
        'VERB': 'V',
        'INFN': 'V',
        'PRTF': 'V',
        'PRTS': 'V',
        'GRND': 'V',
        'COMP': 'ADV',
        'NUMR': 'ADV',
        'NPRO': 'S',
        'PRED': 'ADV',
        'PREP': 'PR',
        'CONJ': 'CONJ',
        'PRCL': 'ADV',
        'INTJ': 'ADV'}


CONJ = ['а', 'но', 'да', 'зато', 'однако', 'и', 'также', 'тоже', 'или', 'либо',
        'то', 'ли', 'же', 'притом', 'причём']
PR = ['без', 'в', 'для', 'за', 'из', 'к', 'на', 'над', 'о', 'об', 'от', 'по', 'под',
      'пред', 'при', 'про', 'с', 'у', 'через']


def xml_to_dict(xml: Path):
    print('Parsing xml with dictionary...', file=sys.stderr)

    tree = ElementTree.parse(xml)
    root = tree.getroot()

    lemmas: Dict[int, str] = {}
    for lemma in root.iter('lemma'):
        lemmas[int(lemma.get('id'))] = lemma.find('l').get('t')

    full_lemmas: Dict[str, str] = {}
    for link in root.iter('link'):
        id_from, id_to = int(link.get('from')), int(link.get('to'))
        full_lemmas[lemmas[id_to]] = lemmas[id_from]

    word_dict: Dict[str, List[Tuple]] = {}
    for lemma in root.iter('lemma'):
        lem = lemma.find('l').get('t')
        tags = [TAGS[tag.get('v')] for tag in lemma.find('l').iter('g') if tag.get('v') in TAGS]
        lem_tag = tags[0] if len(tags) > 0 else 'ADV'

        if lem_tag in 'VA' and lem in full_lemmas:
            lem = full_lemmas[lem]

        for word in lemma.iter('f'):
            w = word.get('t')
            if w not in word_dict:
                word_dict[w] = []
            word_dict[w].append((lem, lem_tag))

    print('Done\n', file=sys.stderr)

    return word_dict


def lemmatize_sentence(sentence: List, word_dict: Dict):
    lemmatized_words = []
    for word in sentence:
        norm_word = word.lower()
        if word.isalpha():
            if norm_word in CONJ:
                lemma = '{' + f'{norm_word}=CONJ' + '}'
                lemmatized_words.append(f'{word}{lemma}')
            elif norm_word in PR:
                lemma = '{' + f'{norm_word}=PR' + '}'
                lemmatized_words.append(f'{word}{lemma}')
            elif norm_word in word_dict:
                lemma = '{' + '{}={}'.format(*word_dict[norm_word][0]) + '}'
                lemmatized_words.append(f'{word}{lemma}')
            else:
                lemma = '{' + f'{norm_word}=ADV' + '}'
                lemmatized_words.append(f'{word}{lemma}')
    return ' '.join(lemmatized_words)


def process_dataset(dataset_path: Path, output_path: Path, word_dict: Dict):
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    with dataset_path.open('r') as dataset, output_path.open('w') as output:
        for i, line in enumerate(dataset.readlines()):
            if i % 20 == 0:
                print(f'Lemmatized {i} sentences', file=sys.stderr)
            sentence = re.sub(r'[^а-яёА-ЯË]', ' ', line).strip().split()
            result = lemmatize_sentence(sentence, word_dict)
            print(result, file=output)


def main():
    dict_path = Path('resources', 'opencorpora', 'dict.opcorpora.xml')
    dataset_path = Path('resources', 'dataset', 'dataset_37845_1.txt')
    output_path = Path('resources', 'output', 'output.txt')

    word_dict = xml_to_dict(dict_path)
    process_dataset(dataset_path, output_path, word_dict)


if __name__ == '__main__':
    main()
