from data.questions import Question
from data.topics import Topic


def count_res_topics_sum(db_sess, student_tests):
    topic_res = {}
    for topic in db_sess.query(Topic).all():
        name = db_sess.query(Topic.name).filter(Topic.id == topic.id)[0]
        topic_res[name[0]] = 0
    for test in student_tests:
        if test.result_answer_1 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_1)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] += 1
        if test.result_answer_2 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_2)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] += 1
        if test.result_answer_3 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_3)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] += 1
        if test.result_answer_4 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_4)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] += 1
        if test.result_answer_5 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_5)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] += 1

        if test.result_answer_1 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_1)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] -= 1
        if test.result_answer_2 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_2)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] -= 1
        if test.result_answer_3 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_3)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] -= 1
        if test.result_answer_4 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_4)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] -= 1
        if test.result_answer_5 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_5)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name] -= 1

    topic_res = dict(sorted(topic_res.items(), key=lambda item: item[1], reverse=True))
    topic_res = list(topic_res.items())

    return topic_res


def count_res_topics(db_sess, student_tests):
    topic_res = {}
    for topic in db_sess.query(Topic).all():
        name = db_sess.query(Topic.name).filter(Topic.id == topic.id)[0]
        topic_res[name[0]] = [0, 0]
    for test in student_tests:
        if test.result_answer_1 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_1)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][0] += 1
        if test.result_answer_2 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_2)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][0] += 1
        if test.result_answer_3 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_3)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][0] += 1
        if test.result_answer_4 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_4)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][0] += 1
        if test.result_answer_5 == 1:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_5)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][0] += 1

        if test.result_answer_1 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_1)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][1] += 1
        if test.result_answer_2 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_2)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][1] += 1
        if test.result_answer_3 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_3)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][1] += 1
        if test.result_answer_4 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_4)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][1] += 1
        if test.result_answer_5 == 0:
            w_topic = db_sess.query(Question.topic_id).filter(Question.id == test.question_5)[0]
            name = db_sess.query(Topic.name).filter(Topic.id == w_topic[0])[0][0]
            topic_res[name][1] += 1

    topic_res = dict(sorted(topic_res.items(), key=lambda item: item[1][0], reverse=True))
    topic_res = list(topic_res.items())

    return topic_res
