import numpy as np
from navec import Navec
from sklearn.metrics.pairwise import cosine_similarity

from data import db_session
from sqlalchemy import or_
from data.blitz_tests import BlitzTest

# Загрузка предобученной модели Navec для работы с векторными представлениями слов
navec = Navec.load("for_navec/navec_hudlit_v1_12B_500K_300d_100q.tar")

# Функция для преобразования предложения в вектор
def sentence_to_vector(sentence, model):
    # Если предложение не является строкой, преобразуем его в строку
    if not isinstance(sentence, str):
        sentence = str(sentence)

    # Разбиваем предложение на слова
    words = sentence.split()
    
    # Получаем векторные представления для каждого слова, если они есть в модели
    vectors = [model.get(word) for word in words if word in model]
    
    # Если ни одного слова не найдено в модели, возвращаем нулевой вектор
    if not vectors:
        return np.zeros(model.pq.dim)
    
    # Возвращаем среднее значение векторов слов
    return np.mean(vectors, axis=0)

# Функция для сравнения двух предложений с использованием косинусной схожести
def compare_sentences(sentence1, sentence2, model):
    # Преобразуем предложения в векторы
    vec1 = sentence_to_vector(sentence1, model).reshape(1, -1)
    vec2 = sentence_to_vector(sentence2, model).reshape(1, -1)
    
    # Вычисляем косинусную схожесть между векторами
    similarity = cosine_similarity(vec1, vec2)[0][0]
    
    # Нормализуем результат в диапазон [0, 1]
    return (similarity + 1) / 2

# Функция для поиска наиболее похожих комментариев по ответу и идентификатору вопроса
def find_most_similar_comment_by_answer(answer, question_id):
    # Создаем сессию для работы с базой данных
    session = db_session.create_session()
    
    # Формируем запрос к базе данных для получения данных о тестах
    query = session.query(
        BlitzTest.id.label("test_id"),
        BlitzTest.student.label("student_id"),
        BlitzTest.date.label("test_date"),
        BlitzTest.answer_1,
        BlitzTest.answer_2,
        BlitzTest.answer_3,
        BlitzTest.answer_4,
        BlitzTest.answer_5,
        BlitzTest.comment_1,
        BlitzTest.comment_2,
        BlitzTest.comment_3,
        BlitzTest.comment_4,
        BlitzTest.comment_5,
        BlitzTest.question_1,
        BlitzTest.question_2,
        BlitzTest.question_3,
        BlitzTest.question_4,
        BlitzTest.question_5,
    ).filter(
        # Фильтруем результаты по идентификатору вопроса
        or_(
            BlitzTest.question_1 == question_id,
            BlitzTest.question_2 == question_id,
            BlitzTest.question_3 == question_id,
            BlitzTest.question_4 == question_id,
            BlitzTest.question_5 == question_id,
        )
    )
    
    # Получаем все результаты запроса
    results = query.all()
    
    # Список для хранения наиболее похожих комментариев
    most_similar_comments = []
    
    # Перебираем все результаты
    for result in results:
        for i in range(1, 6):
            # Получаем значение вопроса, ответа и комментария
            question_value = getattr(result, f"question_{i}")
            answer_value = getattr(result, f"answer_{i}")
            comment_value = getattr(result, f"comment_{i}")
            
            # Если вопрос соответствует искомому идентификатору
            if question_value == question_id:
                # Если комментарий существует
                if comment_value is not None:
                    # Добавляем комментарий и его схожесть с ответом в список
                    most_similar_comments.append(
                        [
                            answer_value,
                            comment_value,
                            compare_sentences(answer, answer_value, navec),
                        ],
                    )
    
    # Возвращаем три наиболее похожих комментария, отсортированных по убыванию схожести
    return sorted(most_similar_comments, key=lambda x: x[1], reverse=True)[:3]