import streamlit as st

# What next:
# 1) put tasks into separate tabs
# st.tabs(list(map(str, range(1, 31))))
#
# 2) add text / file upload
#
# 3) add progress bar of loading and generating
# from stqdm import stqdm
#
# 4) Add adjusting number of tasks to generate
#
# 5) Add random option
#
# 6) Add adhusting dificulty

tasks = [{'type': 'question',
  'description': ['Right down the answer for this question (only one word in lower case):',
   'Напишите ответ на вопрос (одно слово по английски в нижнем регистре)'],
  'sentence': 'As much money and life as you could want!',
  'options': 'question: Money and what else you could want?',
  'answer': 'life',
  'result': '',
  'total': 0},
 {'type': 'shuffle_with_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '"Сколько дней у тебя осталось до твоих праздников?"',
  'options': ['until',
   'got',
   'yer',
   '"How',
   'you',
   'many',
   'left',
   'holidays?"',
   'days'],
  'answer': ['"How',
   'many',
   'days',
   'you',
   'got',
   'left',
   'until',
   'yer',
   'holidays?"'],
  'result': '',
  'total': 0},
 {'type': 'shuffle_no_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '',
  'options': ['giant', 'chuckled.', 'The'],
  'answer': ['The', 'giant', 'chuckled.'],
  'result': '',
  'total': 0},
 {'type': 'missings_with_options',
  'description': ['Choose the missing word in the sentence:',
   'Выберите пропущенное слово в предложении:'],
  'sentence': 'Fred and George Weasley now came into the  ____ , spotted Harry, and hurried over.',
  'options': ['auditorium', 'memorial', 'hall', 'halls'],
  'answer': 'hall',
  'result': '',
  'total': 0},
 {'type': 'missings_no_options',
  'description': ['Write down the missing word in the sentence (only one in lowercase):',
   'Впишите пропущенное слово в предложении (одно, в нижнем регистре):'],
  'sentence': 'Hey -- where\'re yeh goin\'?"',
  'options': 'Эй, где ты иди? "',
  'answer': "goin'",
  'result': '',
  'total': 0},
 {'type': 'question',
  'description': ['Right down the answer for this question (only one word in lower case):',
  'Напишите ответ на вопрос (одно слово по английски в нижнем регистре)'],
  'sentence': 'He was looking at the other boys.',
  'options': 'question: Who was looking at him?',
  'answer': 'boys',
  'result': '',
  'total': 0},
 {'type': 'shuffle_with_translation',
  'description': ['Choose the right order of words',
  'Выберите правильный порядок слов в предложении'],
  'sentence': 'Он рыдал, его лицо в руках.',
  'options': ['his', 'in', 'face', 'sobbed,', 'he', 'hands.', 'his'],
  'answer': ['he', 'sobbed,', 'his', 'face', 'in', 'his', 'hands.'],
  'result': '',
  'total': 0},
 {'type': 'shuffle_no_translation',
  'description': ['Choose the right order of words',
   'Выберите правильный порядок слов в предложении'],
  'sentence': '',
  'options': ['"Good', 'that', 'one.', 'wand,'],
  'answer': ['"Good', 'wand,', 'that', 'one.'],
  'result': '',
  'total': 0},
 {'type': 'missings_with_options',
  'description': ['Choose the missing word in the sentence:',
  'Выберите пропущенное слово в предложении:'],
  'sentence': '"This is  ____ ," Dudley moaned.',
  'options': ['dull', 'boring', 'tedious', 'bored'],
  'answer': 'boring',
  'result': '',
  'total': 0},
 {'type': 'missings_no_options',
  'description': ['Write down the missing word in the sentence (only one in lowercase):',
  'Впишите пропущенное слово в предложении (одно, в нижнем регистре):'],
  'sentence': 'Fifteen brooms rose up,  ____ , high into the air.',
  'options': 'Пятнадцать метл поднялись, высоко, высоко в воздух.',
  'answer': 'high',
  'result': '',
  'total': 0}]

TEXT_SIZE = '#' * 5


def ex_question(task, index):
    st.markdown(f"{TEXT_SIZE} {(task['sentence'])}")
    st.markdown(f"{TEXT_SIZE} {task['options']}")
    task['result'] = st.text_input('', key=index)
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
            'shuffle_with_translation': ex_shuffle_t,
            'shuffle_no_translation': ex_shuffle_not,
            'missings_with_options': ex_missings_opt,
            'missings_no_options': ex_missings_nopt}

col1, col2 = st.columns(spec=(0.8, 0.2))

#############
# interface #
#############

with col2:
    interface_lang = st.selectbox('', ['EN', 'RU'])
with col1:
    lang_dict = {'EN': 0, 'RU': 1}
    language = lang_dict[interface_lang]
    st.header(['Генератор упражнений по английскому языку',
               'English exrecises generator app'][language])

st.subheader(['Insert some text to generate exercises',
              'Вставьте текст для создания упражнения'][language])
st.text_area('nolabel', label_visibility="hidden")
'---'

#########
# tasks #
#########

for i, task in enumerate(tasks):
    st.subheader(task['description'][language])
    ex_type = task['type']
    ex_func = (ex_types[ex_type])
    ex_func(task, i)
    '---'

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
