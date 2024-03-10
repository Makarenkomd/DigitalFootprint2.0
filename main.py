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
        # news = db_sess.query(News).filter(
        #     (News.user == current_user) | (News.is_private != True))
        return render_template("index.html")
    else:
        # news = db_sess.query(News).filter(News.is_private != True)
        return redirect('/authentication')


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
        # user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/выдать_тест", methods=["POST"])
def issue_test():
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # print(form.name.data)
        # print(User.name.)
        # print(db_sess.query(User).filter(User.name == form.name.data).first())
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user is not None:
            if user.date_of_birth == form.date_of_birth.data:
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        return render_template('login.html',
                               message="Неправильное имя или дата рождения",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# @app.route('/news', methods=['GET', 'POST'])
# @login_required
# def add_news():
#     form = NewsForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         news = News()
#         news.title = form.title.data
#         news.content = form.content.data
#         news.is_private = form.is_private.data
#         current_user.news.append(news)
#         db_sess.merge(current_user)
#         db_sess.commit()
#         return redirect('/')
#     return render_template('news.html', title='Добавление новости',
#                            form=form)


# @app.route('/news/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_news(id):
#     form = NewsForm()
#     if request.method == "GET":
#         db_sess = db_session.create_session()
#         news = db_sess.query(News).filter(News.id == id,
#                                           News.user == current_user
#                                           ).first()
#         if news:
#             form.title.data = news.title
#             form.content.data = news.content
#             form.is_private.data = news.is_private
#         else:
#             abort(404)
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         news = db_sess.query(News).filter(News.id == id,
#                                           News.user == current_user
#                                           ).first()
#         if news:
#             news.title = form.title.data
#             news.content = form.content.data
#             news.is_private = form.is_private.data
#             db_sess.commit()
#             return redirect('/')
#         else:
#             abort(404)
#     return render_template('news.html',
#                            title='Редактирование новости',
#                            form=form
#                            )


# @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
# @login_required
# def news_delete(id):
#     db_sess = db_session.create_session()
#     news = db_sess.query(News).filter(News.id == id,
#                                       News.user == current_user
#                                       ).first()
#     if news:
#         db_sess.delete(news)
#         db_sess.commit()
#     else:
#         abort(404)
#     return redirect('/')


@app.route('/give_test', methods=['GET', 'POST'])
def give_test():
    db_sess = db_session.create_session()
    students = db_sess.query(User).filter(User.user_level != 'admin')
    topics = db_sess.query(Topic)

    if request.method == 'POST':

        students_id = request.form.getlist('students')
        topic_id = request.form.get('topics')

        for j in range(len(students_id)):

            blitz_test = BlitzTest()
            count = db_sess.query(Question).filter(Question.topic_id == topic_id).count()
            questions = [db_sess.query(Question).filter(Question.topic_id == topic_id)[i].id for i in range(0, count)]
            questions_index = [i for i in range(0, count)]

            blitz_test.question_1 = questions[questions_index.pop(random.randrange(len(questions_index)))]
            blitz_test.question_2 = questions[questions_index.pop(random.randrange(len(questions_index)))]
            blitz_test.question_3 = questions[questions_index.pop(random.randrange(len(questions_index)))]
            blitz_test.question_4 = questions[questions_index.pop(random.randrange(len(questions_index)))]
            blitz_test.question_5 = questions[questions_index.pop(random.randrange(len(questions_index)))]
            blitz_test.student = students_id[j]

            db_sess.add(blitz_test)
            db_sess.commit()

    return render_template('give_test.html', students=students, topics=topics)


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host="127.0.0.1", debug=True)


if __name__ == '__main__':
    main()
