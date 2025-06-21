def check_task_test(text_task, student_answer, yand_model):
    result = yand_model.run(
        [
            {
                "role": "system",
                "text": "Ты ассистент проверяющий тесты, за один запрос тебе даёться вопрос и ответ студента. Твоя задача написать в начале сообщения только 'Верно' или же 'Неверно', а после комментарий который направит студента что нужно сделать чтобы исправиться",
            },
            {
                "role": "user",
                "text": f"Условие: {text_task}\nОтвет студента: {student_answer}",
            },
        ]
    )

    for alternative in result:
        return alternative