from data import db_session
from data.topics import Topic
from data.questions import Question
from data.users import User
from data.blitz_tests import BlitzTest
from sqlalchemy import or_
from collections import defaultdict
from random import randrange


def get_questions_with_results_by_topic_and_student(session, student_id, question_ids):
    tests = (
        session.query(BlitzTest)
        .filter(
            BlitzTest.student == student_id,
            or_(
                BlitzTest.question_1.in_(question_ids),
                BlitzTest.question_2.in_(question_ids),
                BlitzTest.question_3.in_(question_ids),
                BlitzTest.question_4.in_(question_ids),
                BlitzTest.question_5.in_(question_ids),
            ),
        )
        .all()
    )

    result = []

    for test in tests:
        questions = [
            test.question_1,
            test.question_2,
            test.question_3,
            test.question_4,
            test.question_5,
        ]
        results = [
            test.result_answer_1,
            test.result_answer_2,
            test.result_answer_3,
            test.result_answer_4,
            test.result_answer_5,
        ]

        zipped = list(zip(questions, results))
        result.append(zipped)

    return result


def get_individual_test(student_id, topics_id):
    session = db_session.create_session()
    questions_for_test = []

    print(len(topics_id), ";" * 3)

    for topic_id in topics_id:
        print("-" * 30)
        stats = defaultdict(int)
        
        # Получаем все вопросы по теме
        questions_by_theme = list(
            map(
                lambda x: x.id,
                session.query(
                    Question,
                )
                .filter(
                    Question.topic_id == topic_id,
                )
                .all(),
            )
        )
        
        # получить все элементы тестов у которые решил данный студент по определённое теме
        decided_questions_by_student_and_theme = get_questions_with_results_by_topic_and_student(
            session=session,
            student_id=student_id,
            question_ids=questions_by_theme,
        )
        
        # определяем количество правильных и неправильных ответов по определённым темам
        for test in decided_questions_by_student_and_theme:
            
            for question_id, result_answer in test:
                if result_answer == 1:
                    stats[question_id] += 1
                elif result_answer == 0:
                    stats[question_id] -= 1
                    
        print(student_id, topic_id, stats)
        if stats == {}:
            questions_for_test.append(questions_by_theme[randrange(len(questions_by_theme))])
        else:
            questions_for_test.append(min(stats, key=lambda x: stats[x]))
        
        print("-" * 30)

    print(questions_for_test)
