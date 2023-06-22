import re
import random
import pandas as pd
import numpy as np
import gensim.downloader as api
import spacy


class ExercieseGenerator:
    def __init__(self, filename: str, encoding: str = 'utf-8'):
        # Reading file & splitting into blocks
        with open(filename, 'rt', encoding=encoding) as file:
            blocks = [re.sub('"', '', line).strip() for line in file.readlines()
                      if line.strip()]

        block_lengths = list(map(lambda x: len(ExercieseGenerator.split_blocks(x)), blocks))
        self.text_data = pd.DataFrame(zip(blocks, block_lengths), columns=['blocks', 'block_length'])
        self.text_data['lines'] = self.text_data['blocks'].apply(ExercieseGenerator.split_blocks)
        self.text_data.explode('lines').reset_index()
        self.text_data['lines'] = self.text_data['lines'].apply(lambda x: x[0])
        self.text_data['lines_length'] = self.text_data['lines'].apply(lambda x: len(x.split()))

    def generate(self, max_num: int = 10):
        pass

    def permutation(self, max_num: int = 1):
        pass

    @staticmethod
    def split_blocks(block):
        sentences = re.split(r'[.!?]', block)
        sentences = map(str.strip, sentences)
        sentences = list(filter(lambda x: x, sentences))
        return sentences
