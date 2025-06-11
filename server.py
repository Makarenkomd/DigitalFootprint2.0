import datetime
import random
from sqlalchemy import desc, func, select
import csv
import io

from flask import send_file
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from api import api
from data import db_session
from data.blitz_tests import BlitzTest
from data.questions import Question
from data.topics import Topic
from data.users import Group, User
from forms.question import AddQuestionForm
from forms.topic import AddTopicForm
from forms.group import GroupForm
from forms.user import LoginForm, RegisterForm, ProfileForm
from utils.count_correct_and_wrong_ans import count_cor_wng_ans
from utils.count_res_topic import count_res_topics, count_res_topics_sum
from utils.meaningful_comparison import find_most_similar_comment_by_answer
from utils.individual_test import get_individual_test


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()

    return db_sess.query(User).get(user_id)


@app.route("/")
def select_group_for_view_tests():
    if not current_user.is_authenticated:
        return redirect("/authentication")

    if current_user.user_level == "student":
        db_sess = db_session.create_session()
        available_tests = db_sess.query(BlitzTest).filter(BlitzTest.student == current_user.id)
        date_time = datetime.datetime.now()
        results = []
        for test in available_tests:
            test_results = 0
            if test.result_answer_1 == 1:
                test_results += 1
            if test.result_answer_2 == 1:
                test_results += 1
            if test.result_answer_3 == 1:
                test_results += 1
            if test.result_answer_4 == 1:
                test_results += 1
            if test.result_answer_5 == 1:
                test_results += 1

            if None in [
                test.result_answer_1,
                test.result_answer_2,
                test.result_answer_3,
                test.result_answer_4,
                test.result_answer_5,
            ]:
                results.append("Не проверено")
            else:
                results.append(f"{test_results}/5")
        tests_and_results = zip(available_tests, results)

        return render_template("index.html", tests_and_results=tests_and_results, date_time=date_time, title="Главная")

    db_sess = db_session.create_session()
    groups = db_sess.query(Group).all()
    db_sess.close()

    return render_template("select_group_for_view_tests.html", groups=groups)


@app.route("/tests/<int:group_id>")
def tests_by_group(group_id):
    if not current_user.is_authenticated:
        return redirect("/authentication")

    if current_user.user_level == "student":
        return abort(404)

    db_sess = db_session.create_session()

    query_for_admin = select(BlitzTest, User).join(User, BlitzTest.student == User.id).where(User.group_id == group_id)

    tests_admin = db_sess.execute(query_for_admin).fetchall()
    date_time = datetime.datetime.now()

    results = []
    for test in tests_admin:
        test = test[0]
        test_results = 0
        if test.result_answer_1 == 1:
            test_results += 1
        if test.result_answer_2 == 1:
            test_results += 1
        if test.result_answer_3 == 1:
            test_results += 1
        if test.result_answer_4 == 1:
            test_results += 1
        if test.result_answer_5 == 1:
            test_results += 1

        if None in [
            test.result_answer_1,
            test.result_answer_2,
            test.result_answer_3,
            test.result_answer_4,
            test.result_answer_5,
        ]:
            results.append("Не проверено")
        else:
            results.append(f"{test_results}/5")

    tests_and_results = zip(tests_admin, results)
    return render_template(
        "index_admin.html",
        date_time=date_time,
        tests_and_results=tests_and_results,
        title="Главная",
    )


@app.route("/start_test/<int:test_id>")
@login_required
def start_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()

    if test.date + datetime.timedelta(minutes=5) < datetime.datetime.now():
        return abort(404)

    questions = [
        db_sess.query(Question).filter(Question.id == test.question_1).first(),
        db_sess.query(Question).filter(Question.id == test.question_2).first(),
        db_sess.query(Question).filter(Question.id == test.question_3).first(),
        db_sess.query(Question).filter(Question.id == test.question_4).first(),
        db_sess.query(Question).filter(Question.id == test.question_5).first(),
    ]

    answers = [
        db_sess.query(
            BlitzTest.answer_1,
        )
        .filter(
            BlitzTest.id == test_id,
        )
        .first(),
        db_sess.query(BlitzTest.answer_2).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_3).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_4).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_5).filter(BlitzTest.id == test_id).first(),
    ]

    que_ans = zip(questions, answers)

    distance = ((test.date + datetime.timedelta(minutes=5)) - datetime.datetime.now()).total_seconds() * 1000

    return render_template("test.html", test=test, que_ans=que_ans, distance=distance, title="Тест")


@app.route("/test_result/<int:test_id>")
@login_required
def test_result(test_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()
        questions = [
            db_sess.query(Question).filter(Question.id == test.question_1).first(),
            db_sess.query(Question).filter(Question.id == test.question_2).first(),
            db_sess.query(Question).filter(Question.id == test.question_3).first(),
            db_sess.query(Question).filter(Question.id == test.question_4).first(),
            db_sess.query(Question).filter(Question.id == test.question_5).first(),
        ]

        answers = [
            db_sess.query(BlitzTest.answer_1).filter(BlitzTest.id == test_id).first(),
            db_sess.query(BlitzTest.answer_2).filter(BlitzTest.id == test_id).first(),
            db_sess.query(BlitzTest.answer_3).filter(BlitzTest.id == test_id).first(),
            db_sess.query(BlitzTest.answer_4).filter(BlitzTest.id == test_id).first(),
            db_sess.query(BlitzTest.answer_5).filter(BlitzTest.id == test_id).first(),
        ]

        comments = [
            db_sess.query(BlitzTest.comment_1).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.comment_2).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.comment_3).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.comment_4).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.comment_5).filter(BlitzTest.id == test_id)[0],
        ]

        results = [
            db_sess.query(BlitzTest.result_answer_1).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.result_answer_2).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.result_answer_3).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.result_answer_4).filter(BlitzTest.id == test_id)[0],
            db_sess.query(BlitzTest.result_answer_5).filter(BlitzTest.id == test_id)[0],
        ]

        most_similar_comments = [
            find_most_similar_comment_by_answer(answers[0], questions[0].id),
            find_most_similar_comment_by_answer(answers[1], questions[1].id),
            find_most_similar_comment_by_answer(answers[2], questions[2].id),
            find_most_similar_comment_by_answer(answers[3], questions[3].id),
            find_most_similar_comment_by_answer(answers[3], questions[4].id),
        ]
        student_id_by_test = test.student

        user_student = db_sess.query(User).filter(User.id == student_id_by_test).first()

        group_id_of_student = user_student.group_id

        que_ans_comm_results = zip(
            questions,
            answers,
            comments,
            results,
            most_similar_comments,
        )
        print(most_similar_comments)

        return render_template(
            "test_result.html",
            test=test,
            que_ans_comm_results=que_ans_comm_results,
            group_id=group_id_of_student,
            title="Тест",
        )
    abort(403)


@app.route("/test_result_view/<int:test_id>")
@login_required
def test_result_view(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()
    questions = [
        db_sess.query(Question).filter(Question.id == test.question_1).first(),
        db_sess.query(Question).filter(Question.id == test.question_2).first(),
        db_sess.query(Question).filter(Question.id == test.question_3).first(),
        db_sess.query(Question).filter(Question.id == test.question_4).first(),
        db_sess.query(Question).filter(Question.id == test.question_5).first(),
    ]

    answers = [
        db_sess.query(BlitzTest.answer_1).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_2).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_3).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_4).filter(BlitzTest.id == test_id).first(),
        db_sess.query(BlitzTest.answer_5).filter(BlitzTest.id == test_id).first(),
    ]

    comments = [
        db_sess.query(BlitzTest.comment_1).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.comment_2).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.comment_3).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.comment_4).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.comment_5).filter(BlitzTest.id == test_id)[0],
    ]

    results = [
        db_sess.query(BlitzTest.result_answer_1).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.result_answer_2).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.result_answer_3).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.result_answer_4).filter(BlitzTest.id == test_id)[0],
        db_sess.query(BlitzTest.result_answer_5).filter(BlitzTest.id == test_id)[0],
    ]

    que_ans_comm_results = zip(questions, answers, comments, results)

    test_result_n = 0

    if test.result_answer_1 == 1:
        test_result_n += 1
    if test.result_answer_2 == 1:
        test_result_n += 1
    if test.result_answer_3 == 1:
        test_result_n += 1
    if test.result_answer_4 == 1:
        test_result_n += 1
    if test.result_answer_5 == 1:
        test_result_n += 1

    if None in [
        test.result_answer_1,
        test.result_answer_2,
        test.result_answer_3,
        test.result_answer_4,
        test.result_answer_5,
    ]:
        test_result_n = "Не проверено"
    else:
        test_result_n = f"{test_result_n}/5"

    return render_template(
        "test_result_view.html",
        test=test,
        que_ans_comm_results=que_ans_comm_results,
        result=test_result_n,
        title="Тест",
    )


@app.route("/submit_test/<int:test_id>", methods=["POST"])
@login_required
def submit_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()

    if test.date + datetime.timedelta(minutes=5) < datetime.datetime.now():
        return abort(404)

    if "answer_1" in request.form:
        test.answer_1 = request.form.get("answer_1")

    if "answer_2" in request.form:
        test.answer_2 = request.form.get("answer_2")

    if "answer_3" in request.form:
        test.answer_3 = request.form.get("answer_3")

    if "answer_4" in request.form:
        test.answer_4 = request.form.get("answer_4")

    if "answer_5" in request.form:
        test.answer_5 = request.form.get("answer_5")

    db_sess.commit()

    return redirect("/")


@app.route("/submit_test_result/<int:test_id>", methods=["POST"])
@login_required
def submit_test_result(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()

    comments = request.form.getlist("comment")
    result_answers = [
        request.form.get("correct1"),
        request.form.get("correct2"),
        request.form.get("correct3"),
        request.form.get("correct4"),
        request.form.get("correct5"),
    ]

    test.comment_1 = comments[0]
    test.comment_2 = comments[1]
    test.comment_3 = comments[2]
    test.comment_4 = comments[3]
    test.comment_5 = comments[4]

    test.result_answer_1 = 1 if result_answers[0] == "true" else 0
    test.result_answer_2 = 1 if result_answers[1] == "true" else 0
    test.result_answer_3 = 1 if result_answers[2] == "true" else 0
    test.result_answer_4 = 1 if result_answers[3] == "true" else 0
    test.result_answer_5 = 1 if result_answers[4] == "true" else 0

    db_sess.commit()

    return redirect("/")


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/authentication", methods=["GET", "POST"])
def authentication():
    return render_template("authentication.html", title="Аутентификация")


@app.route("/register", methods=["GET", "POST"])
def register():
    db_sess = db_session.create_session()

    form = RegisterForm()
    groups = db_sess.query(Group).all()

    form.group.choices = [(group.id, group.name) for group in groups]

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )

        user = User(
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            group_id=form.group.data,
        )
        db_sess.add(user)
        db_sess.commit()

        return redirect("/")

    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.name == form.name.data).first()

            if user is not None:

                if user.date_of_birth == form.date_of_birth.data:
                    login_user(user, remember=form.remember_me.data)
                    return redirect("/")

            return render_template("login.html", message="Неправильное имя или дата рождения", form=form)

    return render_template("login.html", title="Авторизация", form=form)


@app.route("/select_group_for_test", methods=["GET"])
@login_required
def select_group_for_test():
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        groups = db_sess.query(Group).all()
        db_sess.close()
        return render_template("select_group_for_give_test.html", title="Выбор группы для выдачи теста", groups=groups)

    abort(403)


@app.route("/groups/<int:group_id>/give_test", methods=["GET", "POST"])
@login_required
def give_test(group_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        students = db_sess.query(User).filter(User.user_level != "admin" and User.group_id == group_id)
        topics = db_sess.query(Topic)

        if request.method == "POST":

            students_id = request.form.getlist("students")
            topics_id = request.form.getlist("topics")
            topics_id = list(map(int, topics_id))

            for j in range(len(students_id)):
                blitz_test = BlitzTest()
                count = db_sess.query(Question).filter(Question.topic_id.in_(topics_id)).count()
                if count >= 5:
                    questions = [
                        db_sess.query(Question).filter(Question.topic_id.in_(topics_id))[i].id for i in range(count)
                    ]

                    questions_index = [i for i in range(count)]

                    blitz_test.question_1 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_2 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_3 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_4 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_5 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.student = students_id[j]

                    db_sess.add(blitz_test)
                    db_sess.commit()
                    test_id = blitz_test.id

                    db_sess.close()
                    return redirect(f"/timer_of_test/{test_id}")
                else:

                    return render_template(
                        "give_test.html",
                        students=students,
                        topics=topics,
                        title="Выдача тестов",
                        message="Вопросов на выбранную тему меньше 5",
                    )

    else:
        abort(403)

    return render_template(
        "give_test.html",
        students=students,
        topics=topics,
        title="Выдача тестов",
        group_id=group_id,
    )


@app.route("/groups/<int:group_id>/give_individual_test", methods=["GET", "POST"])
@login_required
def give_individual_test(group_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        students = db_sess.query(User).filter(User.user_level != "admin" and User.group_id == group_id)
        topics = db_sess.query(Topic)

        if request.method == "POST":

            students_id = request.form.getlist("students")
            topics_id = request.form.getlist("topics")
            topics_id = list(map(int, topics_id))

            for j in range(len(students_id)):
                blitz_test = BlitzTest()
                count = db_sess.query(Question).filter(Question.topic_id.in_(topics_id)).count()
                if count <= 5:
                    questions = [
                        db_sess.query(Question).filter(Question.topic_id.in_(topics_id))[i].id for i in range(count)
                    ]

                    questions_index = [i for i in range(count)]

                    blitz_test.question_1 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_2 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_3 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_4 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.question_5 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                    blitz_test.student = students_id[j]

                    db_sess.add(blitz_test)
                    db_sess.commit()
                    test_id = blitz_test.id

                    db_sess.close()
                    return redirect(f"/timer_of_test/{test_id}")
                else:

                    return render_template(
                        "give_individual_test.html",
                        students=students,
                        topics=topics,
                        title="Выдача тестов",
                        message="Вопросов на выбранную тему больше 5",
                    )

    else:
        abort(403)

    return render_template(
        "give_individual_test.html",
        students=students,
        topics=topics,
        title="Выдача тестов",
        group_id=group_id,
    )


@app.route("/groups/<int:group_id>/edit", methods=["GET", "POST"])
def edit_group(group_id):
    if current_user.user_level == "admin":
        form = GroupForm()
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id == group_id).first()

        if request.method == "POST":

            if form.validate_on_submit():
                group.name = form.name.data

                db_sess.commit()
                db_sess.close()
                return redirect("/groups")

            return render_template(
                "edit_group.html",
                message="Что-то не так",
                form=form,
            )

        form.name.data = group.name

        return render_template(
            "edit_group.html",
            title="Редактирование группы",
            form=form,
        )

    abort(403)


def stats_topics_by_student_id(student_id):
    sess = db_session.create_session()
    tests = sess.query(BlitzTest).filter(BlitzTest.student == student_id).all()
    topics = {}
    for test in tests:
        for index_of_task in range(1, 6):
            topic_of_question = (
                sess.query(Question).filter(Question.id == getattr(test, f"question_{index_of_task}")).first().topic_id
            )
            if topic_of_question not in topics:
                topics[topic_of_question] = {
                    "wrong": 0,
                    "right": 0,
                }
            if getattr(test, f"result_answer_{index_of_task}") == 0:
                topics[topic_of_question]["wrong"] += 1
            elif getattr(test, f"result_answer_{index_of_task}") == 1:
                topics[topic_of_question]["right"] += 1
    sess.close()
    return topics


@app.route("/export_stats/<int:student_id>", methods=["GET"])
def export_to_csv_file_stats(student_id):
    sess = db_session.create_session()
    # Экспорт topics в csv и передать пользователю как скачивание сразу напрямую файл передать в return send_file
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["topic_id", "correct", "incorrect"])

    for topic_id, stats in topics.items():
        topic = sess.query(Topic).filter(Topic.id == topic_id).first()
        cw.writerow([topic.name, stats["right"], stats["wrong"]])
    sess.close()

    # Преобразуем в байты для отправки
    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8"))
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        download_name=f"stats_student_{student_id}.csv",
        as_attachment=True,
    )


@app.route("/users/<int:user_id>/delete", methods=["GET"])
def delete_user(user_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        user = (
            db_sess.query(User)
            .filter(
                User.id == user_id,
            )
            .first()
        )

        group_id = user.group_id

        db_sess.delete(user)
        db_sess.commit()

        return redirect(f"/groups/{group_id}")

    return abort(403)


@app.route("/timer_of_test/<int:test_id>", methods=["GET"])
def timer_test(test_id):
    sess = db_session.create_session()

    test = (
        sess.query(
            BlitzTest,
        )
        .filter(
            BlitzTest.id == test_id,
        )
        .first()
    )

    distance = ((test.date + datetime.timedelta(minutes=5)) - datetime.datetime.now()).total_seconds() * 1000

    return render_template(
        "timer_test.html",
        distance=distance,
    )


@login_required
@app.route("/personal_cabinet/<int:user_id>", methods=["GET", "POST"])
def personal_cabinet(user_id):
    if (current_user.id != user_id and current_user.user_level == "admin") or (user_id == current_user.id):

        db_sess = db_session.create_session()

        student_tests = db_sess.query(BlitzTest).filter(BlitzTest.student == user_id).all()
        usr = db_sess.query(User).filter(User.id == user_id).first()
        form_for_profile = ProfileForm()

        groups = db_sess.query(Group).all()

        form_for_profile.group.choices = [(group.id, group.name) for group in groups]

        message = ""

        topic_res = count_res_topics_sum(db_sess, student_tests)
        correct_ans, wrong_ans = count_cor_wng_ans(student_tests)

        count_of_users_with_this_name = len(
            db_sess.query(
                User,
            )
            .filter(
                User.name == form_for_profile.name.data,
            )
            .all(),
        )
        if request.method == "POST":
            if form_for_profile.validate_on_submit() and (
                count_of_users_with_this_name == 0 or usr.name == form_for_profile.name.data
            ):
                usr.name = form_for_profile.name.data
                usr.date_of_birth = form_for_profile.date_of_birth.data
                usr.group_id = form_for_profile.group.data

                db_sess.commit()

            elif count_of_users_with_this_name != 0:
                message = "Пользователь с таким именем уже существует"
                form_for_profile.name.data = usr.name
        else:
            form_for_profile.name.data = usr.name
            form_for_profile.date_of_birth.data = usr.date_of_birth
            form_for_profile.group.data = usr.group_id

        return render_template(
            "personal_cabinet.html",
            correct_ans=correct_ans,
            wrong_ans=wrong_ans,
            usr=usr,
            topic_res=topic_res,
            title="Личный кабинет",
            form_for_profile=form_for_profile,
            message=message,
        )

    abort(403)


@app.route("/topics")
@login_required
def topics():
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()

        query = (
            select(
                Topic.id,
                Topic.name,
                func.count(Question.id).label("question_count"),
            )
            .join(
                Question,
                Topic.id == Question.topic_id,
                isouter=True,
            )
            .group_by(
                Topic.id,
            )
            .order_by(
                Topic.name,
            )
        )

        topics_with_count_of_questions = db_sess.execute(query).all()

        db_sess.close()

        return render_template(
            "topics.html",
            topics=topics_with_count_of_questions,
            title="Темы",
        )
    abort(403)


@app.route("/questions/<int:topic_id>")
@login_required
def questions(topic_id):
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()
        question_list = (
            db_sess.query(Question)
            .filter(
                Question.topic_id == topic_id,
            )
            .order_by(desc(Question.id))
            .all()
        )
        print(question_list)

        return render_template("questions.html", title="Вопросы по теме", questions=question_list, topic_id=topic_id)
    abort(403)


@app.route("/add_question/<int:topic_id>", methods=["POST", "GET"])
@login_required
def add_question(topic_id):
    if current_user.user_level == "admin":
        form = AddQuestionForm()

        if request.method == "POST":
            db_sess = db_session.create_session()

            question = Question(text=form.text.data, topic_id=topic_id)

            db_sess.add(question)
            db_sess.commit()
            return redirect(f"/questions/{topic_id}")
        return render_template("add_question.html", title="Добавление вопроса", form=form)
    abort(403)


@app.route("/add_topic", methods=["POST", "GET"])
@login_required
def add_topic():
    if current_user.user_level == "admin":
        form = AddTopicForm()

        if request.method == "POST":
            db_sess = db_session.create_session()

            topic = Topic(name=form.name.data)

            db_sess.add(topic)
            db_sess.commit()
            return redirect("/topics")

        return render_template(
            "add_topic.html",
            title="Добавление темы",
            form=form,
        )
    abort(403)


@app.route("/edit_question/<int:topic_id>/<int:question_id>", methods=["POST", "GET"])
@login_required
def edit_question(topic_id, question_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        form = AddQuestionForm()
        if request.method == "POST":
            question = db_sess.query(Question).filter(Question.id == question_id).first()
            question.text = form.text.data

            db_sess.add(question)
            db_sess.commit()
            return redirect(f"/questions/{topic_id}")

        form.text.data = db_sess.query(Question).filter(Question.id == question_id).first().text
        return render_template(
            "edit_question.html",
            title="Редактирование вопроса",
            form=form,
        )
    abort(403)


@app.route("/delete_question/<int:topic_id>/<int:question_id>")
@login_required
def delete_question(topic_id, question_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id == question_id).first()
        db_sess.delete(question)
        db_sess.commit()
        return redirect(f"/questions/{topic_id}")
    abort(403)


@app.route("/edit_topic/<int:topic_id>", methods=["POST", "GET"])
@login_required
def edit_topic(topic_id):
    if current_user.user_level == "admin":
        form = AddTopicForm()

        if request.method == "POST":
            db_sess = db_session.create_session()
            topic = db_sess.query(Topic).filter(Topic.id == topic_id).first()
            topic.name = form.name.data

            db_sess.add(topic)
            db_sess.commit()
            return redirect("/topics")
        return render_template("edit_topic.html", title="Редактирование темы", form=form)
    abort(403)


@app.route("/groups/<int:group_id>")
@login_required
def students_by_group_id(group_id):
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        students_by_group = db_sess.query(User).filter(User.user_level == "student", User.group_id == group_id).all()

        return render_template(
            "students_by_group.html",
            title=f"Студенты группы {group.name}",
            students=students_by_group,
            group_name=group.name,
        )

    abort(403)


@app.route("/groups")
@login_required
def groups_of_students():
    if current_user.user_level == "admin":
        db_sess = db_session.create_session()
        groups = db_sess.query(Group).all()

        return render_template(
            "groups.html",
            title="Группы",
            groups=groups,
        )
    abort(403)


@app.route("/groups/create", methods=["POST", "GET"])
def create_group():
    if current_user.user_level == "admin":
        form = GroupForm()

        if request.method == "POST":
            db_sess = db_session.create_session()

            group = Group(
                name=form.name.data,
            )
            db_sess.add(group)
            db_sess.commit()

            return redirect("/groups")

        return render_template(
            "create_group.html",
            title="Создание группы",
            form=form,
        )


@app.route("/groups/<int:group_id>/delete", methods=["GET"])
def delete_group_by_id(group_id):
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()

        group = (
            db_sess.query(Group)
            .filter(
                Group.id == group_id,
            )
            .first()
        )

        users_for_deleting = db_sess.query(User).filter(User.group_id == group_id).all()

        for user in users_for_deleting:
            db_sess.delete(user)

        db_sess.delete(group)

        db_sess.commit()

        return redirect("/groups")

    abort(403)


@app.route("/student_results/<int:student_id>")
@login_required
def student_results(student_id):
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()
        student_tests = db_sess.query(BlitzTest).filter(BlitzTest.student == student_id).all()
        name = db_sess.query(User.name).filter(User.id == student_id).first()[0]

        topics_res = count_res_topics(db_sess, student_tests)

        return render_template("student_results.html", title="Результаты студента", topics_res=topics_res, name=name)

    abort(403)


@app.route("/top_students")
@login_required
def top_students():
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()
        students = db_sess.query(User).filter(User.user_level == "student").all()

        students_res = [
            [
                student.name,
                count_cor_wng_ans(
                    db_sess.query(BlitzTest)
                    .filter(
                        BlitzTest.student == student.id,
                    )
                    .all(),
                )[0],
            ]
            for student in students
        ]

        students_top = sorted(students_res, key=lambda x: x[1], reverse=True)

        return render_template(
            "top_students.html",
            title="Топ студентов",
            students_top=students_top,
        )

    abort(403)


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(api.blueprint)
    print(find_most_similar_comment_by_answer("f", 2))
    app.run(port=8080, host="0.0.0.0", debug=True)


if __name__ == "__main__":
    main()
