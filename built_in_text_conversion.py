from exercise_gen import ExerciseGenerator


def texts_to_exgen_df(texts):
    exgen = ExerciseGenerator()
    for text in texts:
        print(text, 'processing in progress')
        exgen.from_path(text + '.txt')
        exgen.export_to_csv(text + '.csv')
