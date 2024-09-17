from flask import Flask, render_template, request, redirect, url_for, session
from pony.orm import *
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = Database()

class User(db.Entity):
    _table_ = 'users'
    id = PrimaryKey(int, auto=True)
    username = Required(str, unique=True)
    password = Required(str)
    messages = Set('Message')

class Message(db.Entity):
    _table_ = 'messages'
    id = PrimaryKey(int, auto=True)
    content = Required(str)
    timestamp = Required(datetime, default=lambda: datetime.now())
    user = Required(User)

db.bind(provider='mysql', host='localhost', user='root', passwd='', db='chat_db')
db.generate_mapping(create_tables=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with db_session:
            if User.get(username=username) is None:
                User(username=username, password=password)
                return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with db_session:
            user = User.get(username=username, password=password)
            if user:
                session['user_id'] = user.id
                return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
@db_session
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    messages = select(m for m in Message).order_by(Message.timestamp)
    return render_template('chat.html', messages=messages)

@app.route('/send', methods=['POST'])
@db_session
def send():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    user = User[session['user_id']]
    Message(content=content, user=user)
    return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
