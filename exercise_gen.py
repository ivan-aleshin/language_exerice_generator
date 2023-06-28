import re
import random
import pandas as pd
import gensim.downloader as api
import spacy
import translators as ts
import requests
from lang_proj.tokens import HUGGINGFACE_API_TOKEN


class ExerciseGenerator:
    _nlp = spacy.load('en_core_web_sm')
    _tags = ['ADJ', 'DET', 'NOUN', 'VERB']

    def __init__(self, filename: str, encoding: str = 'utf-8'):
        self.word_vectors = api.load("glove-wiki-gigaword-100")
        self.text_data = ExerciseGenerator.text_to_dataset(filename)

    def _template_wrapper(exercise_generator):
        def wrapper(*args, **kwargs):
            result = exercise_generator(*args, **kwargs)
            task = {'type': result[0],
                    'description': result[1],
                    'sentence': result[2],
                    'options': result[3],
                    'answer': result[4],
                    'result': '',
                    'total': 0}
            return task
        return wrapper

    @staticmethod
    def split_blocks(block: str):
        """
        Returns splitted block into separate sentences
        """
        doc = ExerciseGenerator._nlp(block)

        return [sent.text.strip() for sent in doc.sents]

    @staticmethod
    def text_to_dataset(filename: str):
        """
        Returns dataset with text splitted into paragraphs (blocks) in first column
        and length of each block in second one.
        """

        with open(filename, 'rt') as file:
            text = file.read()
            blocks = [block.strip() for block in text.split('\n') if block.strip()]
            block_lengths = list(map(lambda x: len(ExerciseGenerator.split_blocks(x)), blocks))
            text_data = pd.DataFrame(zip(blocks, block_lengths), columns=['block', 'block_length'])
            text_data = ExerciseGenerator.explode_dataset(text_data)
            text_data['part_of_word'] = text_data['line'].apply(ExerciseGenerator.add_part_of_word)

        return text_data

    @staticmethod
    def explode_dataset(dataset):
        dataset['line'] = dataset['block'].apply(ExerciseGenerator.split_blocks)
        dataset = dataset.explode('line').reset_index()
        dataset['line_length'] = dataset['line'].apply(lambda x: len(x.split()))
        return dataset

    @staticmethod
    def add_part_of_word(sentence):
        doc = ExerciseGenerator._nlp(sentence)
        part_of_word = []
        for pow in doc:
            if pow.pos_ not in part_of_word:
                part_of_word.append(pow.pos_)
        return str(part_of_word)

    def choose_sentence(self, option=None, limits=(3, 15)):
        if option is None:
            option = random.choice(ExerciseGenerator._tags)
        index_tag = self.text_data[(self.text_data['part_of_word'].str.contains(option))].index
        index_limit = self.text_data[(self.text_data['line_length'] >= limits[0]) &
                                     (self.text_data['line_length'] <= limits[1])].index
        final_index = pd.Index.intersection(index_tag, index_limit)
        if self.text_data.loc[final_index].shape[0]:
            chosen_index = random.choice(self.text_data.loc[final_index].index)
            return self.text_data.loc[chosen_index, 'line']
        else:
            return 'The Stogovs left their flat early in the morning and went by bus to the country.'

    @_template_wrapper
    def gen_missings(self, tag=None, options=True):
        if tag is None:
            tag = random.choice(ExerciseGenerator._tags)
        sentence = self.choose_sentence(tag, limits=(5, 18))
        if not options:
            try:
                sentence_trans = ExerciseGenerator.translate(sentence)
            except:
                options = True
        target_word = random.choice([str(token) for token in ExerciseGenerator._nlp(sentence) if token.pos_ == tag])
        blank_line = ' ____ '
        question_sentence = re.sub(fr'\b{target_word}\b', blank_line, sentence, count=1, flags=re.I)
        if options:
            answers = [target_word]
            wrong_answers = map(lambda x: x[0], self.word_vectors.most_similar(target_word.lower())[:3])
            answers.extend(wrong_answers)
            random.shuffle(answers)
            return ('missings_with_options',
                    ['Choose the missing word in the sentence:',
                    'Выберите пропущенное слово в предложении:'],
                    question_sentence,
                    answers,
                    target_word.lower(),
                    '',
                    0)
        else:
            return ('missings_no_options',
                    ['Write down the missing word in the sentence (only one in lowercase):',
                    'Впишите пропущенное слово в предложении (одно, в нижнем регистре):'],
                    question_sentence,
                    sentence_trans,
                    target_word.lower(),
                    '',
                    0)

    @_template_wrapper
    def gen_shuffle(self, translation=True):
        if translation:
            sentence = self.choose_sentence(limits=(7, 12))
            try:
                sentence_trans = ExerciseGenerator.translate(sentence)
            except:
                gen_shuffle(self, translation=False)
            right_ans, shuffled = ExerciseGenerator.shuffle(sentence)
            return ('shuffle_with_translation',
                   ['Choose the right order of words',
                   'Выберите правильный порядок слов в предложении'],
                    sentence_trans,
                    shuffled,
                    right_ans)
        else:
            sentence = self.choose_sentence(limits=(3, 6))
            right_ans, shuffled = ExerciseGenerator.shuffle(sentence)
            return ('shuffle_no_translation',
                   ['Choose the right order of words',
                   'Выберите правильный порядок слов в предложении'],
                   '',
                   shuffled,
                   right_ans)

    @staticmethod
    def shuffle(sentence):
        right_ans = sentence.split()
        shuffled = sentence.split()
        while right_ans == shuffled:
            random.shuffle(shuffled)
        return right_ans, shuffled

    @staticmethod
    def translate(sentence):
        return ts.translate_text(sentence,
                                 translator='google',
                                 from_language='en',
                                 to_language='ru')

    @_template_wrapper
    def gen_question(self):
        sentence = self.choose_sentence(option='NOUN', limits=(7, 12))
        target_word = random.choice([str(token) for token in ExerciseGenerator._nlp(sentence) if token.pos_ == 'NOUN'])
        question = ExerciseGenerator.huggin_question(sentence, target_word)
        return ('question',
                [
                    'Right down the answer for this question (only one word in lower case):',
                    'Напишите ответ на вопрос (одно слово по английски в нижнем регистре)'
                ],
                sentence,
                question,
                target_word.lower()
               )


    def long_read(self):
        # same as gen_question but with options (multiple?) and longer text
        pass

    @staticmethod
    def huggin_question(sentence, answer):
        API_URL = "https://api-inference.huggingface.co/models/mrm8488/t5-base-finetuned-question-generation-ap"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
        text = f'answer: {answer} context: {sentence}'
        response = requests.post(API_URL, headers=headers, json={"inputs": text,})
        return response.json()[0]['generated_text']

    def output(self, n_exercises: int=10, types=None):
        output = {}
        for i in range(n_exercises):
            pass
