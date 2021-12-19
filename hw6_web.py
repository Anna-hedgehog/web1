#!/usr/bin/env python
# coding: utf-8

# In[79]:


from flask import Flask, url_for, render_template, request, redirect
import sqlite3
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy


# Подготовим базу:

# In[82]:


db = sqlite3.connect('n_y_mood.db')
cur = db.cursor()

cur.execute(
    """CREATE TABLE 
    answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    q1 TEXT,
    q2 TEXT
    )""")

cur.execute(
    """CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
    )""")

cur.execute(
    """CREATE TABLE 
    user ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER,
    gender TEXT,
    education TEXT )""")


# Вопросы для опроса:

# In[83]:


questions = [('Оцените по шкале от 1 до 5, насколько вы сейчас загружены на работе или учёбе:',), 
             ('Оцените по шкале от 1 до 5, насколько вы чувствуете новогоднее настроение:',)]


# In[84]:


for question in questions:
    cur.execute(
        '''INSERT into questions (text) VALUES (?)''', question
    )
db.commit()


# Пишем код сайта:

# In[ ]:


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///n_y_mood.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    tablename = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Integer)


class Questions(db.Model):
    tablename = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)


class Answers(db.Model):
    tablename = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)

    
@app.route('/')
def describe():
    return render_template("describe.html")

@app.route('/quest')
def quest():
    questions = Questions.query.all()
    return render_template(
        'quest.html',
        questions=questions
    )

@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('question_page'))
    gender = request.args.get('gender')
    education = request.args.get('education')
    age = request.args.get('age')
    user = User(
        age=age,
        gender=gender,
        education=education
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    q1 = request.args.get('q1')
    q2 = request.args.get('q2')
    answer = Answers(id=user.id, q1=q1, q2=q2)
    db.session.add(answer)
    db.session.commit()
    return render_template("ok.html")

@app.route('/statistics')
def statistics():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = age_stats[0]
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['total_count'] = User.query.count()
    
    q_stats = db.session.query(
        func.avg(Answers.q1),
        func.avg(Answers.q2),
        func.avg(Answers.q2).filter(Answers.q1 >= 4),
        func.avg(Answers.q2).filter(Answers.q1 <= 2)                              
    ).one()
    all_info['q1_mean'] = q_stats[0]
    all_info['q2_mean'] = q_stats[1]
    all_info['mood_tiredness45'] = q_stats[2]
    all_info['mood_tiredness12'] = q_stats[3]

    return render_template('statistics.html', all_info=all_info)


if __name__ == '__main__':
    app.run(debug=False)


# In[ ]:




