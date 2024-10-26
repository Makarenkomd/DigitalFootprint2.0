import datetime
import os
import random

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
from forms.avatar import AvatarForm
from forms.question import AddQuestionForm
from forms.topic import AddTopicForm
from forms.group import GroupForm
from forms.user import LoginForm, RegisterForm
from utils.count_correct_and_wrong_ans import count_cor_wng_ans
from utils.count_res_topic import count_res_topics, count_res_topics_sum

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["AVATAR_UPLOAD_PATH"] = os.path.join(os.getcwd(), "static", "images", "avatar")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()

    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        available_tests = db_sess.query(BlitzTest).filter(BlitzTest.student == current_user.id)
        tests_admin = db_sess.query(BlitzTest)
        date_time = datetime.datetime.now()
        students = [item for item in db_sess.query(User)]

        if current_user.user_level == "student":
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

            return render_template(
                "index.html", tests_and_results=tests_and_results, date_time=date_time, title="Главная"
            )

        results = []
        for test in tests_admin:
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
            students=students,
            tests_and_results=tests_and_results,
            title="Главная",
        )

    return redirect("/authentication")


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

        que_ans_comm_results = zip(questions, answers, comments, results)

        return render_template("test_result.html", test=test, que_ans_comm_results=que_ans_comm_results, title="Тест")
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

    answers = request.form.getlist("answer")

    test.answer_1 = answers[0]
    test.answer_2 = answers[1]
    test.answer_3 = answers[2]
    test.answer_4 = answers[3]
    test.answer_5 = answers[4]

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

                    db_sess.close()
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


@app.route("/personal_cabinet/<int:user_id>", methods=["POST", "GET"])
@login_required
def personal_cabinet(user_id):
    if (current_user.id != user_id and current_user.user_level == "admin") or (user_id == current_user.id):

        db_sess = db_session.create_session()

        student_tests = db_sess.query(BlitzTest).filter(BlitzTest.student == user_id).all()
        usr = db_sess.query(User).filter(User.id == user_id).first()
        form = AvatarForm()

        topic_res = count_res_topics_sum(db_sess, student_tests)
        correct_ans, wrong_ans = count_cor_wng_ans(student_tests)
        print(topic_res)
        if request.method == "POST" and form.validate_on_submit():
            avatar = form.avatar.data
            if avatar:
                filename = avatar.filename
                avatar.save(os.path.join(app.config["AVATAR_UPLOAD_PATH"], filename))

                usr.avatar = filename
                db_sess.commit()

            db_sess.commit()

        return render_template(
            "personal_cabinet.html",
            correct_ans=correct_ans,
            wrong_ans=wrong_ans,
            usr=usr,
            topic_res=topic_res,
            title="Личный кабинет",
            form=form,
        )
    abort(403)


@app.route("/topics")
@login_required
def topics():
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()
        topic_list = db_sess.query(Topic).all()

        db_sess.close()

        return render_template("topics.html", topics=topic_list, title="Темы")
    abort(403)


@app.route("/questions/<int:topic_id>")
@login_required
def questions(topic_id):
    if current_user.user_level == "admin":

        db_sess = db_session.create_session()
        question_list = db_sess.query(Question).filter(Question.topic_id == topic_id).all()

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

        form.text.data = (
            db_sess.query(Question).filter(Question.id == question_id).first().text
        )
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
        print(students_by_group)

        return render_template(
            "students_by_group.html",
            title=f"Студенты группы {group.name}",
            students=students_by_group,
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

        print(students_top)
        return render_template(
            "top_students.html",
            title="Топ студентов",
            students_top=students_top,
        )

    abort(403)


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(api.blueprint)
    app.run(port=8080, host="0.0.0.0", debug=True)


if __name__ == "__main__":
    main()
