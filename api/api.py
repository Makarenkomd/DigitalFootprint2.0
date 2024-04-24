from flask import Blueprint, make_response
from flask import jsonify
from data import db_session
from data.users import User
from data.topics import Topic
from data.blitz_tests import BlitzTest
from data.questions import Question
from server import app

blueprint = Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'user': [user.to_dict(only=('name', 'group', 'date_of_birth', 'user_level', 'avatar', 'id'))
                     for user in users]
        }
    )


@blueprint.route('/api/questions')
def get_questions():
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).all()
    return jsonify(
        {
            'question': [question.to_dict(only=('id', 'text', 'topic_id'))
                         for question in questions]
        }
    )


@blueprint.route('/api/topics')
def get_topics():
    db_sess = db_session.create_session()
    topics = db_sess.query(Topic).all()
    return jsonify(
        {
            'topic': [topic.to_dict(only=('name', 'id'))
                      for topic in topics]
        }
    )


@blueprint.route('/api/blitz_tests')
def get_blitz_tests():
    db_sess = db_session.create_session()
    blitz_tests = db_sess.query(BlitzTest).all()
    return jsonify(
        {
            'blitz_test': [blitz_test.to_dict(
                only=('id', 'date', 'question_1', 'question_2', 'question_3', 'question_4', 'question_5', 'answer_1',
                      'answer_2', 'answer_3', 'answer_4', 'answer_5', 'comment_1', 'comment_2', 'comment_3',
                      'comment_4', 'comment_5', 'result_answer_1', 'result_answer_2', 'result_answer_3',
                      'result_answer_4', 'result_answer_5', 'student'))
                for blitz_test in blitz_tests]
        }
    )


@blueprint.route('/api/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'user': user.to_dict(only=(
                'name', 'group', 'date_of_birth', 'user_level', 'avatar', 'id'))
        }
    )


@blueprint.route('/api/topic/<int:topic_id>', methods=['GET'])
def get_one_topic(topic_id):
    db_sess = db_session.create_session()
    topic = db_sess.query(Topic).get(topic_id)
    if not topic:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'topic': topic.to_dict(only=(
                'name', 'id'))
        }
    )


@blueprint.route('/api/question/<int:question_id>', methods=['GET'])
def get_one_question(question_id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).get(question_id)
    if not question:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'question': question.to_dict(only=(
                'id', 'text', 'topic_id'))
        }
    )


@blueprint.route('/api/blitz_test/<int:blitz_test_id>', methods=['GET'])
def get_one_blitz_test(blitz_test_id):
    db_sess = db_session.create_session()
    blitz_test = db_sess.query(BlitzTest).get(blitz_test_id)
    if not blitz_test:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'blitz_test': blitz_test.to_dict(only=(
                'id', 'date', 'question_1', 'question_2', 'question_3', 'question_4', 'question_5', 'answer_1',
                'answer_2', 'answer_3', 'answer_4', 'answer_5', 'comment_1', 'comment_2', 'comment_3',
                'comment_4', 'comment_5', 'result_answer_1', 'result_answer_2', 'result_answer_3',
                'result_answer_4', 'result_answer_5', 'student'
            ))
        }
    )


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)
