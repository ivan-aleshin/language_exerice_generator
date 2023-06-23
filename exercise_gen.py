import re
import random
import pandas as pd
import numpy as np
import gensim.downloader as api
import spacy


class ExercieseGenerator:
    nlp = spacy.load('en_core_web_sm')

    def __init__(self, filename: str, encoding: str = 'utf-8'):
        # Reading file & splitting into blocks
        self.text_data = ExercieseGenerator.text_to_dataset(filename)
        self.text_data = ExercieseGenerator.explode_dataset(self.text_data)

    def generate(self, max_num: int = 10):
        pass

    def permutation(self, max_num: int = 1):
        pass

    @staticmethod
    def split_blocks(block: str):
        """
        Returns splitted block into separate sentences
        """
        doc = nlp(block)

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

        return pd.DataFrame(zip(blocks, block_lengths), columns=['block', 'block_length'])

    @staticmethod
    def explode_dataset(dataset):
        dataset['line'] = dataset['block'].apply(ExercieseGenerator.split_blocks)
        dataset = dataset.explode('line').reset_index()
        dataset['line_length'] = dataset['line'].apply(lambda x: len(x.split()))
        return dataset
