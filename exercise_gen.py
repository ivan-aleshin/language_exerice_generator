import re
import random
import pandas as pd
import gensim.downloader as api
import spacy


class ExercieseGenerator:
    nlp = spacy.load('en_core_web_sm')

    def __init__(self, filename: str, encoding: str = 'utf-8'):
        self.word_vectors = api.load("glove-wiki-gigaword-100")
        self.text_data = ExercieseGenerator.text_to_dataset(filename)
        #self.output

    def generate(self, max_num: int = 10):
        pass

    def permutation(self, max_num: int = 1):
        pass

    @staticmethod
    def split_blocks(block: str):
        """
        Returns splitted block into separate sentences
        """
        doc = ExercieseGenerator.nlp(block)

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
            block_lengths = list(map(lambda x: len(ExercieseGenerator.split_blocks(x)), blocks))
            text_data = pd.DataFrame(zip(blocks, block_lengths), columns=['block', 'block_length'])
            text_data = ExercieseGenerator.explode_dataset(text_data)
            text_data['part_of_word'] = text_data['line'].apply(ExercieseGenerator.add_part_of_word)

        return text_data

    @staticmethod
    def explode_dataset(dataset):
        dataset['line'] = dataset['block'].apply(ExercieseGenerator.split_blocks)
        dataset = dataset.explode('line').reset_index()
        dataset['line_length'] = dataset['line'].apply(lambda x: len(x.split()))
        return dataset

    @staticmethod
    def add_part_of_word(sentence):
        doc = ExercieseGenerator.nlp(sentence)
        part_of_word = []
        for pow in doc:
            if pow.pos_ not in part_of_word:
                part_of_word.append(pow.pos_)
        return str(part_of_word)

    def choose_sentence(self, option='VERB', limits=(3, 15)):
        index_tag = self.text_data[(self.text_data['part_of_word'].str.contains(option))].index
        index_limit = self.text_data[(self.text_data['line_length'] >= limits[0]) &
                              (self.text_data['line_length'] <= limits[1])].index
        final_index = pd.Index.intersection(index_tag, index_limit)
        if self.text_data.loc[final_index].shape[0]:
            chosen_index = random.choice(self.text_data.loc[final_index].index)
            return self.text_data.loc[chosen_index, 'line']
        else:
            return 'The Stogovs left their flat early in the morning and went by bus to the country.'

    def generate_missings(self, option='random'):
        if option == 'random':
            option = random.choice(tags_)
        sentence = self.choose_sentence(option, limits=(5, 18))
        target_word = random.choice([str(token) for token in nlp(sentence) if token.pos_ == option])
        blank_line = ' ____ '
        question_sentence = re.sub(f'\W{target_word}\W', blank_line, sentence, count=1)
        answers = [target_word]
        wrong_answers = map(lambda x: x[0], self.word_vectors.most_similar(target_word.lower())[:3])
        answers.extend(wrong_answers)
        random.shuffle(answers)
        print('Fill the gap in the sentence:')
        print(question_sentence)
        print('Options:', answers)
        print('Right answer:', target_word)
