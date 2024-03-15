import time
from flask import render_template, redirect, send_file, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import or_, and_, update
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime, date

from web import app, db
from web.models import Users, Tasks

from config import config

@app.route('/', methods=['GET'])
@login_required
def main():
    # return render_template('index.html')
    return send_file('./templates/index.html')


@app.route('/new_task', methods=['POST'])
@login_required
def new_task():
    content = request.get_json(silent=True)
    is_started = content['is_started']
    text = content['text']
    
    user_id = current_user.id

    if is_started:
        is_active = True
        started_at = datetime.now()
    else:
        is_active = False
        started_at = None
    
    task = Tasks(user_id=user_id, text=text, created_at=datetime.now(), is_active=is_active, started_at=started_at)
    db.session.add(task)
    db.session.commit()
    
    return {"success": True, "task": {"task_id": task.id, "text": task.text, "started_at": int(time.mktime(task.started_at.timetuple()))*1000 if task.started_at else None, "stopped_at": int(time.mktime(task.stopped_at.timetuple()))*1000 if task.stopped_at else None, "is_active": task.is_active}}

@app.route('/get_tasks', methods=['POST'])
@login_required
def get_tasks():
    content = request.get_json(silent=True)
    if 'last_timestamp' in content: last_timestamp = content['last_timestamp']
    else: last_timestamp = None
    
    user_id = current_user.id
    tasks = Tasks.query.filter(and_(Tasks.user_id == user_id, or_(Tasks.is_active == True, Tasks.started_at == None, and_(Tasks.started_at >= date.today()))))
    
    raw_tasks = []
    for task in tasks:
        raw_tasks.append(task.to_dict())
    return {"success": True, "tasks": raw_tasks}

@app.route('/whoami', methods=['POST'])
@login_required
def whoami():
    user = current_user
    return {"success": True, "user": {"login": user.login}}

@app.route('/run_task', methods=['POST'])
@login_required
def run_task():
    content = request.get_json(silent=True)
    task_id = content['task_id']
    user_id = current_user.id
    task = Tasks.query.filter(and_(Tasks.user_id == user_id, Tasks.id == task_id)).first()
    if not task:
        return {"success": False, "error": "record not found"}
    task.is_active = True
    task.started_at = datetime.now()
    db.session.commit()
    return {"success": True, "task": task.to_dict()}

@app.route('/stop_task', methods=['POST'])
@login_required
def stop_task():
    content = request.get_json(silent=True)
    task_id = content['task_id']
    user_id = current_user.id
    task = Tasks.query.filter(and_(Tasks.user_id == user_id, Tasks.id == task_id)).first()
    if not task:
        return {"success": False, "error": "record not found"}
    task.is_active = False
    task.stopped_at = datetime.now()
    db.session.commit()
    return {"success": True, "task": task.to_dict()}


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = Users.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect("/")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = Users(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route('/css/style.css', methods=['GET'])
def style_css():
    return send_file(config["PATH"]+'css/style.css')

@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
