from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()
from . import models

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

from flask import Flask, render_template, redirect, request, url_for
import numpy as np
import pandas as pd
import itertools

app = Flask(__name__)
 
@app.route('/')
@app.route('/<num>')
def inputTest(num=None):
    return render_template('question/main.html', num=num)
    
@app.route('/calculate',methods=['POST'])
def calculate(num=None):
    if request.method == 'POST':
        
        price_index = []
        price_save = []

        for i in range(15):

            temp1 = request.form['t%s' % (i+1)]
            temp2 = request.form['n%s' % (i+1)]

            if(temp2 != ''):

                price_index.append(temp1)
                price_save.append(int(temp2))

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
        result = str(first.iloc[0,0])+'를 계산하세요 '+str(first.iloc[0,1])+'원'
        # str(request.user_agent.string.replace('/',''))

    else:

        result = ''

    return redirect(url_for('inputTest',num=result))


