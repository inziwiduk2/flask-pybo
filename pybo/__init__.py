from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

import config

import numpy as np
import pandas as pd
import itertools

import os
from .forms import *

db = SQLAlchemy()
migrate = Migrate()
# from . import models
from .models import User

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(config)

#     # ORM
#     db.init_app(app)
#     migrate.init_app(app, db)

#     # 블루프린트
#     from .views import main_views, question_views, answer_views
#     app.register_blueprint(main_views.bp)
#     app.register_blueprint(question_views.bp)
#     app.register_blueprint(answer_views.bp)

#     return app

app = Flask(__name__)
app.secret_key = b'ermdlfie20391!@$/'
app.config.from_object(config)

# ORM
db.init_app(app)
migrate.init_app(app, db)
 
# @app.route('/')

@app.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        else:
            if user.approve == 'X':
                error = "승인되지 않았습니다."

        if error is None:
            # session.clear()
            session['user'] = user.id
            return redirect(url_for('calculate'))
        flash(error)
    return render_template('question/login.html', form=form)


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))


# @app.route('/<num>')
# def inputTest(num=''):
#     return render_template('question/main.html', num=num)


# @app.route('/main_page/<num>')
# def inputTest(num):
#     return render_template('question/main.html', num=num)


@app.route('/calculate',methods=['GET','POST'])
def calculate():

    if 'user' in session:

        if request.method == 'POST':
            
            price_index = []
            price_save = []

            for i in range(15):

                temp1 = request.form['t%s' % (i+1)]
                temp2 = request.form['n%s' % (i+1)]

                if(temp2 != ''):

                    price_index.append(temp1)
                    price_save.append(int(temp2))

            if((len(price_save)!=0) & (np.sum(price_save)>=5000)):

                first = pd.DataFrame({'product':price_index,'price':price_save,'count':np.repeat(1,len(price_index))})
                last = pd.DataFrame({'product':[str(price_index)],'price':np.sum(price_save),'count':[len(price_index)]})

                first = pd.concat([first,last])
                for z in range(2,len(price_index)):
                    
                    temp1 = list(itertools.combinations((price_index),z))
                    temp2 = list(itertools.combinations((price_save),z))

                    temp1_fix = [list(i) for i in temp1]
                    temp2_fix = [sum(i) for i in temp2]

                    temp = pd.DataFrame({'product':temp1_fix,'price':temp2_fix,'count':np.repeat(z,len(temp1_fix))})
                    first = pd.concat([first,temp])

                first['price2'] = [int(str(i)[len(str(i))-3:len(str(i))]) for i in first['price']]
                first = first[first['price']>5000].sort_values(by=['price2','price'], ascending=[False,True])
                
                product = str(first.iloc[0,0]).replace('[','').replace(']','').replace("'","")
                
                result = product+'를 계산하세요 '+str(first.iloc[0,1])+'원'
                # str(request.user_agent.string.replace('/',''))

            elif((len(price_save)!=0) & (np.sum(price_save)<5000)):

                result = '가격이 5000원을 넘지 않습니다.'

            else:

                result = '가격이 하나도 입력되지 않았습니다.'

        else:

            result = ''

        return render_template('question/main.html', num=result)
        #return redirect(url_for('inputTest',num=result))

    else:

        return redirect(url_for('login'))



@app.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        user_mail = User.query.filter_by(email=form.email.data).first()

        if ((not user) & (not user_mail)):
        
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                        email=form.email.data,
                        approve = 'X')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        
        else:
        
            flash('이미 존재하는 사용자이거나 이미 존재하는 메일입니다.')
        
    return render_template('question/signup.html', form=form)





