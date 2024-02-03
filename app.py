from os import urandom
from flask import Flask, flash, render_template, request, redirect
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4
from dotenv import load_dotenv, dotenv_values

from chatapp.socket_manager import socketio
from chatapp.database import users, FIRST_TIME as DB_FIRST_TIME
from chatapp.utils import timestamp_now
from chatapp.routes import init
from chatapp.login_form import login_manager, RegistrationForm, LoginForm

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(512)
socketio.init_app(app)
init(app)
login_manager.init_app(app)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return render_template('noauth.index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template("login.html", form=form)

    if not form.validate():
        flash("Registration failed", category="error")
        return render_template('login.html', form=form)

    user_ = users.select_one({'username': form.username})
    if not user_:
        flash("Account doesn't exists", category='error')
        return render_template('login.html', form=form)
    if not check_password_hash(user_.password, form.password): # type: ignore
        flash("Password doesn't match", category='error')
        return render_template('login.html', form=form)
    login_user(user_, remember=form.remember) # type: ignore
    return redirect("/")

@app.get("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return render_template("/")

@app.route("/register", methods=["GET", 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
    if not form.validate():
        flash("Registration failed", category="error")
        return render_template('register.html', form=form)

    users.insert({'username': form.username,
                  'display_name': form.display_name,
                  'password': generate_password_hash(form.password), # type: ignore
                  'email': form.email,
                  'user_id': str(uuid4()),
                  'created_at': timestamp_now()
    })
    flash('Your account has been created!')
    user = users.select({'username': form.username})
    login_user(user, remember=form.remember) # type: ignore
    return redirect('/')

@app.get("/chat")
def chat():
    # TODO: Actually implement chat system. We land at here and things may be happpening in runtime.
    # we also need to design logic in front-end system.
    # The front-end may gather things in runtime and since things happens, we may not inclusively uses /chat/<room>
    # since that's too bad for users and URL. We need to not change anything.
    ...

def init_admin(data: dict[str, str]):
    users.insert({
        'username': data['USERNAME'],
        'display_name': data['DISPLAY_NAME'],
        'email': data['EMAIL'],
        'user_id': str(uuid4()),
        'created_at': timestamp_now()
    })

if DB_FIRST_TIME:
    ADMIN = dotenv_values(".admin.env")
    init_admin(ADMIN) # type: ignore

if __name__ == '__main__':   
    socketio.run(app, use_reloader=True, log_output=True)
