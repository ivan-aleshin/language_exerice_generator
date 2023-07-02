import re
import random
import pandas as pd
import gensim.downloader as api
import spacy
import translators as ts
import requests
#from tokens import HUGGINGFACE_API_TOKEN
import math
import streamlit as st
import spacy.cli

spacy.cli.download("en_core_web_sm")

HUGGINGFACE_API_TOKEN = st.secrets['HUGGINGFACE_API_TOKEN']


class ExerciseGenerator:
    _nlp = spacy.load('en_core_web_sm')
    _tags = ['ADJ', 'DET', 'NOUN', 'VERB']
    _exercises = {'question': 'gen_question()',
                  'question_longread': 'gen_longread()',
                  'shuffle_with_translation': 'gen_shuffle(translation=True)',
                  'shuffle_no_translation': 'gen_shuffle(translation=False)',
                  'missings_with_options': 'gen_missings(options=True)',
                  'missings_no_options': 'gen_missings(options=False)'}

    _line_error_text = """Translation error caused confusion, due to inadvertent
    linguistic substitution, during the automated process.""".replace('\n', '')

    _block_error_text = """We regret to inform you that an unforeseen error has
    occurred within our app, resulting in an inconvenience for our valued users.
    Our dedicated team is diligently investigating the issue and working
    tirelessly to rectify it promptly. We sincerely apologize for any disruption
    caused and kindly request your patience as we strive to provide a seamless
    and enhanced user experience. Thank you for your understanding and continued
    support.""".replace('\n', '')

    def __init__(self):
        self.word_vectors = api.load("glove-wiki-gigaword-100")

    def from_path(self, source):
        with open(source, 'rt') as file:
            text = file.read()
        self.text_data = ExerciseGenerator.text_to_dataset(text)

    def from_text_file(self, text):
        self.text_data = ExerciseGenerator.text_to_dataset(text)

    def from_text(self):
        pass

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
    def text_to_dataset(text: str):
        """
        Returns dataset with text splitted into paragraphs (blocks) in first column
        and length of each block in second one.
        """
        blocks = [block.strip() for block in text.split('\n') if block.strip()]
        block_lengths = list(map(lambda x: len(ExerciseGenerator.split_blocks(x)), blocks))
        text_data = pd.DataFrame(zip(blocks, block_lengths), columns=['block', 'block_length'])
        text_data = ExerciseGenerator.explode_dataset(text_data)
        text_data['part_of_word'] = text_data['line'].apply(ExerciseGenerator.add_part_of_word)
        blocks_group = text_data.groupby('index')['line_length'].sum()
        text_data['block_words'] = text_data['index'].map(blocks_group)

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
            return ExerciseGenerator._line_error_text

    def choose_block(self, option=None, limits=(40, 150)):
        if option is None:
            option = random.choice(ExerciseGenerator._tags)
        index_tag = self.text_data[(self.text_data['part_of_word'].str.contains(option))].index
        index_limit = self.text_data[(self.text_data['block_words'] >= limits[0]) &
                                     (self.text_data['block_words'] <= limits[1])].index
        if index_limit.empty:
            max_len = self.text_data['block_words'].max()
            index_limit = self.text_data.loc[self.text_data['block_words'] == max_len].index
            del max_len
        final_index = pd.Index.intersection(index_tag, index_limit)
        if final_index.empty:
            return ExerciseGenerator._block_error_text
        else:
            chosen_index = random.choice(final_index)
            return self.text_data.loc[chosen_index, 'block']


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
                sentence_trans = 'Error occured during translation'
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
                target_word.lower())

    @_template_wrapper
    def gen_longread(self):
        sentence = self.choose_block(option='NOUN', limits=(40, 150))
        target_word = random.choice([str(token) for token in ExerciseGenerator._nlp(sentence) if token.pos_ == 'NOUN'])
        question = ExerciseGenerator.huggin_question(sentence, target_word)
        answers = [target_word]
        wrong_answers = map(lambda x: x[0], self.word_vectors.most_similar(target_word.lower())[:3])
        answers.extend(wrong_answers)
        random.shuffle(answers)
        return ('question_longread',
                [
                    'Read text and answer the question',
                    'Прочитайте текст и ответьте на вопрос'
                ],
                (sentence, question),
                answers,
                target_word.lower())

    @staticmethod
    def huggin_question(sentence, answer):
        API_URL = "https://api-inference.huggingface.co/models/mrm8488/t5-base-finetuned-question-generation-ap"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
        text = f'answer: {answer} context: {sentence}'
        response = requests.post(API_URL, headers=headers, json={"inputs": text, })
        return response.json()[0]['generated_text']

    def output(self, n_exercises: int = 10, types='all', randomized=True):
        if types == 'all':
            types = list(self._exercises.keys())
        types = types * math.ceil(n_exercises / len(types))

        if randomized:
            types = random.choices(types, k=n_exercises)
        else:
            types = types[:n_exercises]

        output = []
        for i in range(n_exercises):
            output.append(eval('self.' + self._exercises[types[i]]))
        return output

    def df_export(self):
        return self.text_data

    def df_import(self, df):
        self.text_data = df

    def inport_from_csv(self, path):
        pass

    def export_to_csv(self, filename):
        self.text_data.to_csv(filename)
