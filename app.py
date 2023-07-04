import random
import pandas as pd
import streamlit as st
import gensim.downloader as api
from streamlit_elements import elements, mui, html

from exercise_gen import ExerciseGenerator


# Set size of text in app
TEXT_SIZE = '#' * 5

# Set page configuration
st.set_page_config(
   page_title="ExGen App by Ivan Aleshin",
   page_icon="🇬🇧",
   layout="wide",
   initial_sidebar_state="expanded",)


#
# Exercise funictions
#

def ex_question(task, index):
    st.markdown(f"{TEXT_SIZE} {(task['sentence'])}")
    st.markdown(f"{TEXT_SIZE} {task['options']}")
    task['result'] = st.text_input('', key=index)
    task['total'] = int(task['result'] == task['answer'])


def ex_question_longread(task, index):
    st.markdown(f"{TEXT_SIZE} {'Text:'} {(task['sentence'][0])}")
    st.markdown(f"{TEXT_SIZE} {(task['sentence'][1])}")
    task['result'] = st.selectbox('',
                                  ['', *task['options']],
                                  key=index)
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


#
# Processing functions
#

@st.cache_resource
def word_vectors_preload():
    return api.load("glove-wiki-gigaword-100")


@st.cache_data
def text_from_file(_exgen, text):
    _exgen.from_text_file(text.getvalue().decode("unicode_escape"))
    return _exgen.df_export()


def generate_text(exgen, df, _n_exercises=10, _types='all', _randomized=False):
    exgen.df_import(df)
    return exgen.output(n_exercises=_n_exercises,
                        types=_types,
                        randomized=_randomized)


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
            'missings_no_options': ex_missings_nopt}

built_in_list = {'': '',
                 '----- A-level -----': '',
                 'Atlas Shrugged (Ayn Rand)': 'texts/atlas_shrugged.csv',
                 'Charlie and the Chocolate Factory (Roald Dahl)': 'texts/charlie_and_the_chocolate_factory.csv',
                 'To Kill a Mockingbird (Harper Lee)': '',
                 '----- B-level -----': '',
                 'Brave New World (Aldous Huxley)': 'texts/brave_new_world.csv',
                 'Harry Potter and the Philosopher\'s Stone (J.K. Rowling)': 'texts/harry_potter_1.csv',
                 'To the Lighthouse (Virginia Woolf)': 'texts/to_the_lighthouse.csv',
                 'The Godfather (Mario Puzo)': 'texts/the_godfather.csv',
                 'The Hobbit (J.R.R. Tolkien)': 'texts/the_hobbit.csv',
                 'The Grapes of Wrath (John Stainbeck)': 'texts/grapes_of_wrath.csv',
                 '----- C-level -----': '',
                 'The Advetures of Sherloc Holmes (Arthur Conan Doyle)': 'texts/sherlock_holmes.csv',
                 'Ulysses (James Joyce)': '',
                 'Zen and the Art of Motorcycle Maintenance (Robert Pirsig)': 'texts/zen_and_the_art.csv'}


#
# Class preload
#

with st.spinner('Models caching..'):
    exgen_vectors = word_vectors_preload()


exgen = ExerciseGenerator(exgen_vectors)


# cache the dictionaries separate from class

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
        if quest_ans:
            exercise_toggle_types.append('question')

        quest_long = st.checkbox(['Text reading with question',
                                  'Текст с ответом на вопрос'][language],
                                 value=True)
        if quest_long:
            exercise_toggle_types.append('question_longread')

        order_trans = st.checkbox(['Words order with translation',
                                   'Порядок слов с переводом'][language],
                                  value=True)
        if order_trans:
            exercise_toggle_types.append('shuffle_with_translation')

        order_notrans = st.checkbox(['Words order without translation',
                                     'Порядок слов без перевода'][language],
                                    value=True)
        if order_notrans:
            exercise_toggle_types.append('shuffle_no_translation')

        missing_write = st.checkbox(['Write down the missing word',
                                     'Вписать впропущенное слово'][language],
                                    value=True)
        if missing_write:
            exercise_toggle_types.append('missings_with_options')

        missing_choose = st.checkbox(['Choose the missing word',
                                      'Выбрать пропущенное слово'][language],
                                     value=True)
        if missing_choose:
            exercise_toggle_types.append('missings_no_options')

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


with tab_upload:

    upload_text_label = ['Upload your text file',
                         'Загрузите ваш текстовый фалй'][language]
    st.write(['*Text must be NOT formatted txt type.',
              '*Тест должен быть неотформатированным и меть расширение txt'][language])
    st.markdown(f"{TEXT_SIZE} {upload_text_label}")
    uploaded_text = st.file_uploader('')

    uploadbtn = st.button(['Start text processing',
                           'Начать обработку текста'][language],
                           key='upload_btn')

    if uploadbtn:
        st.session_state.upload = text_from_file(exgen, uploaded_text)
        gen_btn_disabled = False


with tab_insert_text:
    tab_text_label = ['Paste some text to generate exercises',
                      'Вставьте текст для создания упражнения'][language]
    st.markdown(f"{TEXT_SIZE} {tab_text_label}")
    text_input = st.text_area('nolabel', label_visibility="hidden")

    gen_start_text_input = st.button(['Start text processing',
                                      'Начать обработку текста'][language],
                                      key='text_input')

gen_btn = st.button(['Generate it!',
                     'Генерировать упражнения'][language],
                     key='gen_btn',
                     disabled=gen_btn_disabled)


#
# Generation
#

if gen_btn:
    st.session_state.tasks = generate_text(exgen,
                                           st.session_state.upload,
                                           _n_exercises=n_exercises,
                                           _types=exercise_toggle_types,
                                           _randomized=randomized)
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

    if total_sum == len(tasks):
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
