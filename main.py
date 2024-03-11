import random
from flask import Flask, render_template, redirect, abort, request, url_for, flash
from data import db_session
from data.users import User
from data.topics import Topic
from data.blitz_tests import BlitzTest
from forms.user import RegisterForm, LoginForm
from data.questions import Question
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
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
        tests = db_sess.query(BlitzTest).filter(BlitzTest.student == current_user.id)
        return render_template("index.html", tests=tests)
    else:
        return redirect('/authentication')


@app.route("/start_test/<int:test_id>")
@login_required
def start_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()
    questions = [db_sess.query(Question).filter(Question.id == test.question_1).first(),
                 db_sess.query(Question).filter(Question.id == test.question_2).first(),
                 db_sess.query(Question).filter(Question.id == test.question_3).first(),
                 db_sess.query(Question).filter(Question.id == test.question_4).first(),
                 db_sess.query(Question).filter(Question.id == test.question_5).first()]

    return render_template('test.html', test=test, questions=questions)


@app.route('/submit_test/<int:test_id>', methods=['POST'])
@login_required
def submit_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(BlitzTest).filter(BlitzTest.id == test_id).first()

    answers = request.form.getlist('answer')

    test.answer_1 = answers[0]
    test.answer_2 = answers[1]
    test.answer_3 = answers[2]
    test.answer_4 = answers[3]
    test.answer_5 = answers[4]

    db_sess.commit()

    return redirect('/')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/authentication', methods=['GET', 'POST'])
def authentication():
    return render_template('authentication.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user is not None:
            if user.date_of_birth == form.date_of_birth.data:
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        return render_template('login.html',
                               message="Неправильное имя или дата рождения",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/give_test', methods=['GET', 'POST'])
@login_required
def give_test():
    if current_user.user_level == 'admin':
        db_sess = db_session.create_session()
        students = db_sess.query(User).filter(User.user_level != 'admin')
        topics = db_sess.query(Topic)

        if request.method == 'POST':

            students_id = request.form.getlist('students')
            topic_id = request.form.get('topics')

            for j in range(len(students_id)):
                blitz_test = BlitzTest()
                count = db_sess.query(Question).filter(Question.topic_id == topic_id).count()
                questions = [db_sess.query(Question).filter(Question.topic_id == topic_id)[i].id for i in
                             range(0, count)]
                questions_index = [i for i in range(0, count)]

                blitz_test.question_1 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                blitz_test.question_2 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                blitz_test.question_3 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                blitz_test.question_4 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                blitz_test.question_5 = questions[questions_index.pop(random.randrange(len(questions_index)))]
                blitz_test.student = students_id[j]

                db_sess.add(blitz_test)
                db_sess.commit()
    else:
        abort(404)

    return render_template('give_test.html', students=students, topics=topics)


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host="127.0.0.1", debug=True)


if __name__ == '__main__':
    main()
