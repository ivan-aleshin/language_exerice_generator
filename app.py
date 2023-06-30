import streamlit as st
from exercise_gen import ExerciseGenerator

# What next:
# 2) Add generation text by class
#
# 3) add progress bar of loading and generating
# from stqdm import stqdm
#
# 4) Add adjusting number of tasks to generate
#
# 5) Add random option
#
# 6) Add adjusting dificulty

tasks = [{'type': 'question',
  'description': ['Right down the answer for this question (only one word in lower case):',
   'Напишите ответ на вопрос (одно слово по английски в нижнем регистре)'],
  'sentence': '"Potter\'s been sent a broomstick, Professor," said Malfoy quickly.',
  'options': 'question: What did Professor Malfoy sayotter was sent?',
  'answer': 'broomstick',
  'result': '',
  'total': 0},
 {'type': 'question_longread',
  'description': ['Read text and answer the question',
   'Прочитайте текст и ответьте на вопрос'],
  'sentence': ('He took a deep breath, covered his face with his arms, and sprinted across the room. He expected to feel sharp beaks and claws tearing at him any second, but nothing happened. He reached the door untouched. He pulled the handle, but it was locked.',
   'question: What did he take to stop the beaks and claws from tearing'),
  'options': ['breathe', 'breath', 'breathing', 'shortness'],
  'answer': 'breath',
  'result': '',
  'total': 0},
 {'type': 'shuffle_with_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': 'Поэтому я сказал ему, после пушистики, дракона будет легко ... "',
  'options': ['after',
   'Fluffy,',
   'would',
   'him,',
   'I',
   'dragon',
   'easy..."',
   'So',
   'told',
   'a',
   'be'],
  'answer': ['So',
   'I',
   'told',
   'him,',
   'after',
   'Fluffy,',
   'a',
   'dragon',
   'would',
   'be',
   'easy..."'],
  'result': '',
  'total': 0},
 {'type': 'shuffle_no_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '',
  'options': ['away."', 'exams', '"Hermione,', 'the', 'ages', 'are'],
  'answer': ['"Hermione,', 'the', 'exams', 'are', 'ages', 'away."'],
  'result': '',
  'total': 0},
 {'type': 'missings_with_options',
  'description': ['Choose the missing word in the sentence:',
   'Выберите пропущенное слово в предложении:'],
  'sentence': "Ron gritted his teeth and stepped carefully over  ____  dog's legs.",
  'options': ['part', 'one', 'the', 'this'],
  'answer': 'the',
  'result': '',
  'total': 0},
 {'type': 'missings_no_options',
  'description': ['Write down the missing word in the sentence (only one in lowercase):',
   'Впишите пропущенное слово в предложении (одно, в нижнем регистре):'],
  'sentence': "Harry's broom had given a  ____  jerk and Harry swung off it.",
  'options': 'Метла Гарри дала дикий рывок, и Гарри отказался от нее.',
  'answer': 'wild',
  'result': '',
  'total': 0},
 {'type': 'question',
  'description': ['Right down the answer for this question (only one word in lower case):',
   'Напишите ответ на вопрос (одно слово по английски в нижнем регистре)'],
  'sentence': 'Everyone was eating the food that had been sent up.',
  'options': 'question: What was sent up to everyone?',
  'answer': 'food',
  'result': '',
  'total': 0},
 {'type': 'question_longread',
  'description': ['Read text and answer the question',
   'Прочитайте текст и ответьте на вопрос'],
  'sentence': ('I think he sort of wanted to give me a chance. I think he knows more or less everything that goes on here, you know. I reckon he had a pretty good idea we were going to try, and instead of stopping us, he just taught us enough to help. I don\'t think it was an accident he let me find out how the mirror worked. It\'s almost like he thought I had the right to face Voldemort if I could...."',
   'question: What did he have that he wanted to give me a chance?'),
  'options': ['notion', 'thought', 'idea', 'thinking'],
  'answer': 'idea',
  'result': '',
  'total': 0},
 {'type': 'shuffle_with_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '«Я слышал, что ты пошел жить с маглов», - сказал Рон.',
  'options': ['"I',
   'with',
   'heard',
   'Ron.',
   'you',
   'Muggles,"',
   'live',
   'to',
   'said',
   'went'],
  'answer': ['"I',
   'heard',
   'you',
   'went',
   'to',
   'live',
   'with',
   'Muggles,"',
   'said',
   'Ron.'],
  'result': '',
  'total': 0},
 {'type': 'shuffle_no_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '',
  'options': ['start.', 'a', 'with', 'Harry', 'woke'],
  'answer': ['Harry', 'woke', 'with', 'a', 'start.'],
  'result': '',
  'total': 0},
 {'type': 'missings_with_options',
  'description': ['Choose the missing word in the sentence:',
   'Выберите пропущенное слово в предложении:'],
  'sentence': 'Harry lay in his dark cupboard much later, wishing he  ____  a watch.',
  'options': ['having', 'been', 'have', 'had'],
  'answer': 'had',
  'result': '',
  'total': 0},
 {'type': 'missings_no_options',
  'description': ['Write down the missing word in the sentence (only one in lowercase):',
   'Впишите пропущенное слово в предложении (одно, в нижнем регистре):'],
  'sentence': 'The cut had turned a nasty shade of  ____ .',
  'options': 'Разрез превратил неприятный оттенок зеленого.',
  'answer': 'green',
  'result': '',
  'total': 0},
 {'type': 'question',
  'description': ['Right down the answer for this question (only one word in lower case):',
   'Напишите ответ на вопрос (одно слово по английски в нижнем регистре)'],
  'sentence': 'Harry bolted to the door and looked out.',
  'options': 'question: Where did Harry bolt to?',
  'answer': 'door',
  'result': '',
  'total': 0},
 {'type': 'question_longread',
  'description': ['Read text and answer the question',
   'Прочитайте текст и ответьте на вопрос'],
  'sentence': ("The white king took off his crown and threw it at Harry's feet. They had won. The chessmen parted and bowed, leaving the door ahead clear. With one last desperate look back at Ron, Harry and Hermione charged through the door and up the next passageway.",
   'question: What did Harry and Hermione charge up?'),
  'options': ['passageway', 'corridors', 'passageways', 'walkway'],
  'answer': 'passageway',
  'result': '',
  'total': 0},
 {'type': 'shuffle_with_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '"И у тебя действительно есть - ты знаешь ..."',
  'options': ['you', 'got', 'know..."', 'really', 'you', '--', '"And', 'have'],
  'answer': ['"And', 'have', 'you', 'really', 'got', '--', 'you', 'know..."'],
  'result': '',
  'total': 0}]

TEXT_SIZE = '#' * 5


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


ex_types = {'question': ex_question,
            'question_longread': ex_question_longread,
            'shuffle_with_translation': ex_shuffle_t,
            'shuffle_no_translation': ex_shuffle_not,
            'missings_with_options': ex_missings_opt,
            'missings_no_options': ex_missings_nopt}

#
# Header
#

col1, col2 = st.columns(spec=(0.8, 0.2))

with col2:
    interface_lang = st.selectbox('', ['EN', 'RU'])
with col1:
    lang_dict = {'EN': 0, 'RU': 1}
    language = lang_dict[interface_lang]
    st.header(['English exrecises generator app',
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
                              value=True)
    '---'
    st.markdown(f"{'####'} {['Parts of word', 'Части речи'][language]}")
    with st.expander(''):
        noun = st.checkbox(['Noun', 'Существительное'][language], value=True)
        verb = st.checkbox(['Verb', 'Глагол'][language], value=True)
        adjective = st.checkbox(['Adjective', 'Прилагательное'][language], value=True)
        determinant = st.checkbox(['Determinant', 'Артикль'][language], value=True)

    st.markdown(f"{'####'} {['Exercise type', 'Тип упражения'][language]}")
    with st.expander(''):
        quest_ans = st.checkbox(['Question answering', 'Ответ на вопрос'][language], value=True)
        quest_long = st.checkbox(['Text reading with question', 'Текст с ответом на вопрос'][language], value=True)
        order_trans = st.checkbox(['Words order with translation', 'Порядок слов с переводом'][language], value=True)
        order_notrans = st.checkbox(['Words order without translation', 'Порядок слов без перевода'][language], value=True)
        missing_writeS = st.checkbox(['Write down the missing word', 'Вписать впропущенное слово'][language], value=True)
        missing_choose = st.checkbox(['Choose the missing word', 'Выбрать пропущенное слово'][language], value=True)

#
# Text Choice Tabs
#

tabs_labels = [
    ['Insert text', 'Вставить текст'][language],
    ['Upload text', 'Загрущить текст'][language],
    ['Built-in texts', 'Встроенные тексты'][language]
]

tab_text, tab_upload, tab_builtin = st.tabs(tabs_labels)

with tab_text:
    tab_text_label = ['Paste some text to generate exercises',
                      'Вставьте текст для создания упражнения'][language]
    st.markdown(f"{TEXT_SIZE} {tab_text_label}")
    text_input = st.text_area('nolabel', label_visibility="hidden")

    gen_start_text_input = st.button(['Genearte it!',
                                      'Генерировать упражнения'][language],
                                      key='text_input')

with tab_upload:
    upload_text_label = ['Upload your text file',
                         'Загрузите ваш текстовый фалй'][language]
    st.markdown(f"{TEXT_SIZE} {upload_text_label}")
    uploaded_text = st.file_uploader('')

    gen_start_upload = st.button(['Genearte it!',
                                  'Генерировать упражнения'][language],
                                  key='upload')

with tab_builtin:
    builtin_label = ['Choose the text from list',
                     'Выберите текст из списка'][language]
    st.markdown(f"{TEXT_SIZE} {builtin_label}")
    built_in_list = ['',
                     '----- A-level -----',
                     'To Kill a Mockingbird',
                     'Brave New World',
                     'To the Lighthouse',
                     'Harry Potter',
                     '----- B-level -----',
                     'Charlie and the Chocolate Factory',
                     'The Hobbit',
                     'Atlas Shrugged by Ayn Rand (1957)',
                     'Zen and the Art of Motorcycle Maintenance',
                     '----- C-level -----',
                     'The Godfather',
                     'The Grapes of Wrath',
                     'Ulysses']
    built_in_text = st.selectbox('', built_in_list)

    gen_start_builtin = st.button(['Genearte it!',
                                   'Генерировать упражнения'][language],
                                   key='built_in')

if gen_start_text_input:
    st.success('!')
elif gen_start_upload:
    st.success('!!')
elif gen_start_builtin:
    st.success('!!!')
#
# Task Tabs
#

task_tabs = st.tabs(list(map(str, range(1, n_exercises + 1))))

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

total_sum = sum(task['total'] for task in tasks)

if st.button('Отправить задание'):

    st.subheader(f'{total_sum} / {len(tasks)}')

    if total_sum == len(tasks):
        st.success(['Превосходно!',
                    'Perfect!'][language])
        st.balloons()

    elif total_sum / len(tasks) >= 0.85:
        st.success(['Отлично!',
                    'Excellent!'][language])
        st.balloons()

    elif total_sum / len(tasks) >= 0.70:
        st.success(['Хорошо!',
                    'Good!'][language])
        st.balloons()

    elif total_sum / len(tasks) > 0.55:
        st.success(['Вы справились!',
                    'You did it!'][language])
    else:
        st.error(['Попробуйте еще раз',
                  'Try one more time'][language])
