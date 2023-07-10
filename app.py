import random
import requests

import pandas as pd
import streamlit as st
import gensim.downloader as api
import spacy
from annotated_text import annotated_text

from exercise_gen import ExerciseGenerator


# Set size of text in app
# TEXT_SIZE = '#' * 5
TEXT_SIZE = ''
TITLE = ''
HUGGINGFACE_API_TOKEN = st.secrets['HUGGINGFACE_API_TOKEN']
# Set models
GENSIM_MODEL = "glove-wiki-gigaword-100"
SPACY_MODEL = 'en_core_web_md'


# Set page configuration
st.set_page_config(
   page_title="ExGen App by Ivan Aleshin",
   page_icon="🇬🇧",
   layout="wide",
   initial_sidebar_state="expanded",)


@st.cache_resource
def spacy_load():
    return spacy.load(SPACY_MODEL)


@st.cache_resource
def text_to_image(text, title=TITLE):
    # api_url = "https://api-inference.huggingface.co/models/SG161222/Realistic_Vision_V1.4"
    api_url = "https://api-inference.huggingface.co/models/gsdf/Counterfeit-V2.5"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    if title:
        text = f'{title}. {text}'
    response = requests.post(api_url,
                             headers=headers,
                             json={"inputs": text, })
    return response.content


#
# Exercise funictions
#

def ex_question(task, index):
    st.markdown(f"""{TEXT_SIZE} {
        ['Text:', 'Текст:'][language]
    } {(task['sentence'])}""")
    st.markdown(f"""{TEXT_SIZE} {
        ['Question', 'Вопрос'][language]
        } {task['options'][10:]}""")
    task['result'] = st.text_input('', key=index)
    task['total'] = int(task['result'] == task['answer'])


def ex_question_longread(task, index):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"{TEXT_SIZE} {'Text:'} {(task['sentence'][0])}")
        st.markdown(f"{TEXT_SIZE} {(task['sentence'][1])}")
        task['result'] = st.selectbox('',
                                      ['', *task['options']],
                                      key=index)
    with col2:
        fig = text_to_image(task['sentence'][0])
        try:
            st.image(fig)
        except:
            st.text('Unable to load illustration')

    task['total'] = int(task['result'] == task['answer'])


def ex_shuffle_t(task, index):
    st.markdown(f"{TEXT_SIZE} {(task['sentence'])}")
    task['result'] = st.multiselect('', options=task['options'], key=index)
    task['total'] = int(task['result'] == task['answer'])


def ex_shuffle_not(task, index):
    task['result'] = st.multiselect('', options=task['options'], key=index)
    task['total'] = int(task['result'] == task['answer'])


def ex_missings_opt(task, index):
    st.markdown(f"{TEXT_SIZE} {(task['sentence'])}")
    task['result'] = st.selectbox('', options=['', *task['options']], key=index)
    task['total'] = int(task['result'] == task['answer'])


def ex_missings_nopt(task, index):
    st.markdown(f"{TEXT_SIZE} {(task['options'])}")
    st.markdown(f"{TEXT_SIZE} {(task['sentence'])}")
    task['result'] = st.text_input('', key=index)
    task['total'] = int(task['result'] == task['answer'])


def ex_autio_text_missings(task, index):
    st.audio(cached_audio_from_text(task['sentence'][0]))
    col1, col2 = st.columns(2)
    with col2:
        sentence = task['sentence'][1]
        ans1 = st.selectbox("",
                            (['___ 1 ___', *task['options'][0]]),
                            key=(f'{index}a'))
        ans2 = st.selectbox("",
                            (['___ 2 ___', *task['options'][1]]),
                            key=(f'{index}b'))
        ans3 = st.selectbox("",
                            (['___ 3 ___', *task['options'][2]]),
                            key=(f'{index}c'))

    with col1:
        sentence = st.markdown(sentence.format(ans1, ans2, ans3))

    task['result'] = [ans1, ans2, ans3]
    task['total'] = int(task['answer'] == task['result'])


def ex_part_of_word(task, index):
    tags = ExerciseGenerator._all_tags
    sentence = task['sentence']
    col1, col2 = st.columns(2)
    with col2:
        ans1 = st.selectbox("",
                           (['1', *tags]),
                           key=(f'{index}a'))
        ans2 = st.selectbox("",
                           (['2', *tags]),
                           key=(f'{index}b'))
        ans3 = st.selectbox("",
                           (['3', *tags]),
                           key=(f'{index}c'))
        ans4 = st.selectbox("",
                           (['4', *tags]),
                           key=(f'{index}d'))
    with col1:
        ans_dict = {word: ans for word, ans in zip(
            task['options'],
            [f'{ans1}', f'{ans2}', f'{ans3}', f'{ans4}']
        )}
        task['result'] = [(el[0], ans_dict[el[0]]) if isinstance(el, tuple) else el for el in sentence]
        annotated_text(task['result'])
    task['total'] = int(task['result'] == task['answer'])


def ex_sentence_order(task, index):
    task['result'] = st.radio('',
                              (task['options']),
                              key=index)
    task['total'] = int(task['result'] == task['sentence'])


def ex_sentence_match(task, index):
    df = pd.DataFrame(zip(task['sentence'],
                          task['options'],
                          task['answer']),
                      columns=['begining',
                               'end',
                               'answer'])

    task_table = st.data_editor(
        df,
        column_config={
            "end": st.column_config.SelectboxColumn(
                "end",
                options=task['options'])},
            column_order=['begining', 'end'],
            disabled=['begining'],
            hide_index=True,
            use_container_width=True,
            key=index
            )

    task['result'] = list(task_table['end'].values)
    task['total'] = task['result'] == task['answer']


#
# Processing functions
#

@st.cache_resource
def word_vectors_preload():
    return api.load(GENSIM_MODEL)


@st.cache_data
def text_from_file(_exgen, text):
    _exgen.from_text_file(text.getvalue().decode("unicode_escape"))
    return _exgen.df_export()


@st.cache_data
def insert_text(_exgen, text):
    _exgen.from_text_file(text)
    return _exgen.df_export()


def generate_text(exgen, df, _n_exercises=10, _types='all', _randomized=False):
    exgen.df_import(df)
    return exgen.output(n_exercises=_n_exercises,
                        types=_types,
                        randomized=_randomized)


@st.cache_resource
def cached_audio_from_text(text):
    return exgen.text_to_speech(text)


@st.cache_data
def load_from_built_in():
    pass


def green_emoji():
    emojis = ["\N{broccoli}",
              "\N{green apple}",
              "\N{pear}",
              "\N{cactus}",
              "\N{cucumber}",
              "\N{leafy green}"]
    return random.choice(emojis)


def red_emoji():
    emojis = ["\N{tomato}",
              "\N{red apple}",
              "\N{strawberry}"]
    return random.choice(emojis)


#
# Session State
#

if 'tasks' not in st.session_state:
    tasks = []
else:
    tasks = st.session_state.tasks

if 'upload_btn' not in st.session_state:
    gen_btn_disabled = True
else:
    gen_btn_disabled = False


#
# Dictionaties
#

ex_types = {'question': ex_question,
            'question_longread': ex_question_longread,
            'shuffle_with_translation': ex_shuffle_t,
            'shuffle_no_translation': ex_shuffle_not,
            'missings_with_options': ex_missings_opt,
            'missings_no_options': ex_missings_nopt,
            'audio_text_missings': ex_autio_text_missings,
            'part_of_word': ex_part_of_word,
            'sentence_order': ex_sentence_order,
            'sentence_match': ex_sentence_match}

built_in_list = {'': '',
                 '----- A-level -----': '',
                 'Charlie and the Chocolate Factory (Roald Dahl)': 'texts/charlie_and_the_chocolate_factory.csv',
                 'The Adventures of Tom Sawyer (Mark Twain)': 'texts/tom_sawyer.csv',
                 'The Jungle Book (Rudyard Kipling)': 'texts/jungle_book.csv',
                 'To Kill a Mockingbird (Harper Lee)': 'texts/to_kill_a_mockingbird.csv',
                 '----- B-level -----': '',
                 'Atlas Shrugged (Ayn Rand)': 'texts/atlas_shrugged.csv',
                 'Harry Potter and the Philosopher\'s Stone (J.K. Rowling)': 'texts/harry_potter_1.csv',
                 'The Grapes of Wrath (John Stainbeck)': 'texts/grapes_of_wrath.csv',
                 'The Godfather (Mario Puzo)': 'texts/the_godfather.csv',
                 'The Hobbit (J.R.R. Tolkien)': 'texts/the_hobbit.csv',
                 'To the Lighthouse (Virginia Woolf)': 'texts/to_the_lighthouse.csv',
                 'Zen and the Art of Motorcycle Maintenance (Robert Pirsig)': 'texts/zen_and_the_art.csv',
                 '----- C-level -----': '',
                 'The Advetures of Sherloc Holmes (Arthur Conan Doyle)': 'texts/sherlock_holmes.csv',
                 'Brave New World (Aldous Huxley)': 'texts/brave_new_world.csv',
                 'Ulysses (James Joyce)': 'texts/ulysses.csv'}


#
# Vectors preload
#

with st.spinner('Models caching..'):
    exgen_vectors = word_vectors_preload()


exgen = ExerciseGenerator(exgen_vectors)

# text_to_speech model kick-start
cached_audio_from_text('')

#
# Header
#

col1, col2 = st.columns(spec=(0.8, 0.2))

with col2:
    interface_lang = st.selectbox('', ['EN', 'RU'])
with col1:
    lang_dict = {'EN': 0, 'RU': 1}
    language = lang_dict[interface_lang]
    st.header(['English Exrecises Generator App',
               'Генератор упражнений по английскому языку'][language])


#
# Sidebar
#

with st.sidebar:
    st.markdown(f"{'###'} {['Settings', 'Настройки'][language]}")
    n_exercises = st.slider(['Number of exrcises',
                             'Количество упражнений'][language],
                            1,
                            25,
                            10)

    randomized = st.checkbox(['Randomized',
                              'В случайном порядке'][language],
                             key='random',
                             value=False)
    '---'

    # Part of word settings

    st.markdown(f"{'####'} {['Parts of word', 'Части речи'][language]}")
    with st.expander(''):
        type_of_word = []
        noun = st.checkbox(['Noun', 'Существительное'][language], value=True)
        if noun:
            type_of_word.append('NOUN')

        verb = st.checkbox(['Verb', 'Глагол'][language], value=True)
        if verb:
            type_of_word.append('VERB')

        adjective = st.checkbox(['Adjective', 'Прилагательное'][language], value=True)
        if adjective:
            type_of_word.append('ADJ')

        determinant = st.checkbox(['Determinant', 'Артикль'][language], value=True)
        if determinant:
            type_of_word.append('DET')

        if not type_of_word:
            type_of_word = 'all'

    exgen.set_tags(type_of_word)
    # Exercise type settings

    st.markdown(f"{'####'} {['Exercise type', 'Тип упражения'][language]}")
    exercise_toggle_types = []
    with st.expander(''):
        quest_ans = st.checkbox(['Question answering',
                                 'Ответ на вопрос'][language],
                                value=True)

        quest_long = st.checkbox(['Text reading with question',
                                  'Текст с ответом на вопрос'][language],
                                 value=True)

        order_trans = st.checkbox(['Words order with translation',
                                   'Порядок слов с переводом'][language],
                                  value=True)

        order_notrans = st.checkbox(['Words order without translation',
                                     'Порядок слов без перевода'][language],
                                    value=True)

        missing_write = st.checkbox(['Write down the missing word',
                                     'Вписать впропущенное слово'][language],
                                    value=True)

        missing_choose = st.checkbox(['Choose the missing word',
                                      'Выбрать пропущенное слово'][language],
                                     value=True)

        audio_text_missings = st.checkbox(['Choose the missing word \n (Audio)',
                                           'Выбрать пропущенное слово \n (Аудио)'][language],
                                          value=True)

        part_of_word = st.checkbox(['Part of word',
                                    'Часть речи'][language],
                                   value=True)

        sentence_order = st.checkbox(['Sentence order',
                                      'Порядок слов'][language],
                                     value=True)

        sentence_match = st.checkbox(['Sentence match',
                                      'Выбрать части предложения'][language],
                                     value=True)

        type_ex_switches = {'question': quest_ans,
                            'question_longread': quest_long,
                            'shuffle_with_translation': order_trans,
                            'shuffle_no_translation': order_notrans,
                            'missings_with_options': missing_write,
                            'missings_no_options': missing_choose,
                            'audio_text_missings': audio_text_missings,
                            'part_of_word': part_of_word,
                            'sentence_order': sentence_order,
                            'sentence_match': sentence_match}

        exercise_toggle_types = [item[0] for item in type_ex_switches.items() if item[1]]
        if not exercise_toggle_types:
            exercise_toggle_types = list(ex_types.keys())


#
# Text Choice Tabs
#

tabs_labels = [
    ['Built-in texts', 'Встроенные тексты'][language],
    ['Upload text', 'Загрузить текст'][language],
    ['Insert text', 'Вставить текст'][language]
]

tab_builtin, tab_upload, tab_insert_text = st.tabs(tabs_labels)


with tab_builtin:
    builtin_label = ['Choose a text from the list',
                     'Выберите текст из списка'][language]
    st.markdown(f"{TEXT_SIZE} {builtin_label}")

    built_in_text = st.selectbox('', list(built_in_list.keys()))

    if ((not built_in_text) or
        ('level' in built_in_text) or
        (not built_in_list[built_in_text])):
        builtin_load_btn_disabled = True
    else:
        builtin_load_btn_disabled = False

    builtin_load_btn = st.button(['Load text',
                                  'Загрузить тест'][language],
                                  key='built_in',
                                  disabled=builtin_load_btn_disabled)

    if builtin_load_btn:
        st.session_state.upload = exgen.import_from_csv(built_in_list[built_in_text])
        gen_btn_disabled = False
        TITLE = built_in_text


with tab_upload:

    upload_text_label = ['Upload your text file',
                         'Загрузите ваш текстовый фалй'][language]
    st.write(['*Text must be NOT formatted txt type.',
              '*Тест должен быть неотформатированным и меть расширение txt'][language])
    st.markdown(f"{TEXT_SIZE} {upload_text_label}")
    uploaded_text = st.file_uploader('')

    book_title = st.text_input(['Fill the title of book',
                                'Укажите название книги \n (на английском)'][language])

    uploadbtn = st.button(['Start text processing',
                           'Начать обработку текста'][language],
                          key='upload_btn')

    if uploadbtn:
        st.session_state.upload = text_from_file(exgen, uploaded_text)
        gen_btn_disabled = False
        TITLE = book_title

with tab_insert_text:
    tab_text_label = ['Paste some text to generate exercises',
                      'Вставьте текст для создания упражнения'][language]
    st.markdown(f"{TEXT_SIZE} {tab_text_label}")
    text_input = st.text_area('nolabel', label_visibility="hidden")

    gen_start_text_input = st.button(['Start text processing',
                                      'Начать обработку текста'][language],
                                      key='text_input')
    if gen_start_text_input:
        st.session_state.upload = insert_text(exgen, text_input)
        gen_btn_disabled = False
        TITLE = book_title


gen_btn = st.button(['Generate it!',
                     'Генерировать упражнения'][language],
                     key='gen_btn',
                     disabled=gen_btn_disabled)


#
# Generation
#

if gen_btn:
    while True:
        try:
            st.session_state.tasks = generate_text(exgen,
                                           st.session_state.upload,
                                           _n_exercises=n_exercises,
                                           _types=exercise_toggle_types,
                                           _randomized=randomized)
            break

        except KeyError:
            st.text('Key error occured. Retrying to generate exercises...')
            continue

        except:
            st.text('Unknown error occured')
            break

    st.experimental_rerun()


#
# Task Tabs
#

exercises_label = ['Exercises', 'Упражнения'][language]
st.markdown(f"{TEXT_SIZE} {exercises_label}")

task_tabs = st.tabs(list(map(str, range(1, n_exercises + 1))))
answers = []

if 'tasks' in st.session_state:

    for i, task in enumerate(tasks[: n_exercises]):
        with task_tabs[i]:
            st.subheader(task['description'][language])
            ex_type = task['type']
            ex_func = (ex_types[ex_type])
            ex_func(task, i)

'---'

#
# Total counter
#

total_scores = [int(task['total']) for task in tasks]
total_sum = sum(total_scores)

if st.button(['Submit for review',
              'Отправить задание'][language]):

    st.subheader(f'{total_sum} / {len(tasks)}')

    if total_sum / len(tasks) >= 0.95:
        st.success(['Perfect!',
                    'Превосходно!'][language])
        st.balloons()

    elif total_sum / len(tasks) >= 0.85:
        st.success(['Excellent!',
                    'Отлично!'][language])
        st.balloons()

    elif total_sum / len(tasks) >= 0.70:
        st.success(['Good!',
                    'Хорошо!'][language])
        st.balloons()

    elif total_sum / len(tasks) > 0.55:
        st.success(['You did it!',
                    'Вы справились!'][language])
    else:
        st.error(['Try one more time',
                  'Попробуйте еще раз'][language])

    # Display answers
    with st.expander('', expanded=False):

        ans_df = zip(map(lambda task: str(task['result']), tasks),
                     map(lambda task: str(task['answer']), tasks),
                     map(lambda task: (green_emoji() if task['result'] == task['answer'] else red_emoji()), tasks))
        answers = pd.DataFrame(ans_df,
                               index=range(1, n_exercises + 1))
        answers.columns = [['Answer', 'Ответ'][language],
                           ['Correct answer', 'Правильный ответ'][language],
                           ['Result', 'Результат'][language]]
        st.table(answers)
