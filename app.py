import os
import datetime
import wrapper
import controller
from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import pbkdf2_sha256
from functools import wraps

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "protocol.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key = "C6H12O6"

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80),nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    transact = db.relationship('Transaction', backref='t')
    av_transact = db.relationship('av_Transaction', backref='av_t')


    #def __repr__(self):
        #return "<Name {}, Email {}, Username {}, Password {}, Register Date {}>".format(self.name, self.email, self.username, self.password, self.register_date)

    def __str__(self, name, email, username, password):
        self.name = name.title()
        self.email = email.lower()
        self.username = username
        self.password = password


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_id = db.Column(db.Integer, db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    c_name = db.Column(db.String(100), nullable=False)
    c_symbol = db.Column(db.String(80), nullable=False)
    c_lastprice = db.Column(db.Integer, nullable=False)
    c_quantity = db.Column(db.Integer, nullable=False)
    c_total = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    
    def __str__(self, c_name, c_symbol, c_lastprice, c_total):
        self.c_name = c_name
        self.c_symbol = c_symbol
        self.c_lastprice = c_lastprice
        self.c_quantity = c_quantity
        self.c_total = c_total


# Alphavantage



class av_Transaction(db.Model):
    __tablename__ = 'av_transaction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_id = db.Column(db.Integer, db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    c_symbol = db.Column(db.String(80), nullable=False)
    c_lastprice = db.Column(db.Integer, nullable=False)
    c_quantity = db.Column(db.Integer, nullable=False)
    c_total = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    
    def __str__(self, c_symbol, c_lastprice, c_total):
        self.c_symbol = c_symbol
        self.c_lastprice = c_lastprice
        self.c_quantity = c_quantity
        self.c_total = c_total

# Routes
  
@app.route("/")
def index():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

# RegistrationForm

class RegisterForm(Form):
    name = StringField('Name:', [validators.length(min=1, max=50)], render_kw={"placeholder": "Enter your full name."})
    username = StringField('Username:', [validators.length(min=4, max=25)], render_kw={"placeholder": "Enter your username."})
    email = StringField('Email:', [validators.length(min=6, max=50)], render_kw={"placeholder": "Enter your valid Email-ID."})
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Passwords do not match")
    ], render_kw={"placeholder": "Enter your password."})
    confirm = PasswordField('Confirm Password:', render_kw={"placeholder": "Re-enter password to confirm."})

# User register

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        if User.query.filter_by(username=request.form['username']).first():          
            username = User.query.filter_by(username=request.form['username']).first().username
            if form.username.data == username:
                flash("Username exists.",'danger')
                return redirect(url_for('register'))    
        if User.query.filter_by(email=request.form['email']).first():          
            email = User.query.filter_by(email=request.form['email']).first().email
            if form.email.data == email:
                flash("Email exists.",'danger')
                return redirect(url_for('register'))
        else:        
            user = User(name = form.name.data, email = form.email.data, username = form.username.data, password = pbkdf2_sha256.hash(str(form.password.data)),balance='200000')
            db.session.add(user)
            db.session.commit()

            flash('Your are now registered.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html',form=form)

# User login

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():          
            hash = User.query.filter_by(username=request.form['username']).first().password
            username = User.query.filter_by(username=request.form['username']).first().username
            if pbkdf2_sha256.verify(request.form['password'], hash):
                session['logged_in'] = True
                session['username'] = username
                flash('Your are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Invalid username and password', 'danger')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')



# Check if user not logged in, not to display dashboard

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Access denied, Please login to continue.', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You are logged out.", 'success')
    return redirect(url_for('index'))

@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template("dashboard.html")


@app.route("/markit")
@is_logged_in
def markit():
    return render_template("markit.html")

@app.route("/lookup",methods=['GET','POST'])
@is_logged_in
def lookup():

    if request.method == 'POST':
        name = request.form['name']
        data= controller.company_search(name) 
        c_name = data[0]['Name']
        c_exchange = data[0]['Exchange']
        c_symbol = data[0]['Symbol']
        return render_template("lookup.html",c_name=c_name,c_exchange=c_exchange,c_symbol=c_symbol)
    else:
        return render_template("lookup.html")

@app.route("/getquote", methods=['GET','POST'])
@is_logged_in
def getquote():
    if request.method == 'POST':
        symbol = request.form['symbol']
        data = controller.get_quote(symbol)
        c_price = data['LastPrice']
        return render_template("getquote.html",c_price=c_price)
    else:
        return render_template("getquote.html")


@app.route("/buy", methods=['GET','POST'])
@is_logged_in
def buy():
        
    old_balance = User.query.filter_by(username=session['username']).first()
    old_balance.balance
    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        symbol = request.form['symbol']
        data = controller.get_quote(symbol)
        name = data['Name']
        symbol = data['Symbol']
        price = data['LastPrice']
        quantity = (request.form['quantity'])
        total = (price*int(quantity))
        

        id = User.query.filter_by(username=session['username']).first().id
        transaction = Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first()
        balance = User.query.filter_by(username=session['username']).first().balance
        if balance < total:
            flash("Insufficient funds.",'danger')
            return redirect(url_for('buy'))
        
        elif Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first():
            transaction.c_quantity = transaction.c_quantity + int(quantity)
            transaction.c_total = transaction.c_total + total
            new_balance = (old_balance.balance - total)
            new_balance = round(new_balance, 2)
            old_balance.balance = new_balance                           

            db.session.commit()
            flash('Stocks Updated','success')

        else:
            transaction = Transaction(c_name=name,c_symbol=symbol,c_lastprice=price,c_quantity=quantity,c_total=total,t=user)
                
            new_balance = (old_balance.balance - total)
            new_balance = round(new_balance, 2)
            old_balance.balance = new_balance                           
            db.session.add(transaction)
            db.session.commit()
            flash('Stocks purchased for new company.', 'success')

        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = Transaction.query.filter_by(t_id=u_id).all()            
   
        
        return render_template('buy.html', u_balance = u_balance, transaction=transaction)

    else:
        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = Transaction.query.filter_by(t_id=u_id).all()
        #for i in transaction:
            #c_name = i.c_name
            #c_symbol = i.c_symbol
            #c_lastprice = i.c_lastprice
            #c_quantity = i.c_quantity


        return render_template("buy.html",transaction=transaction,u_balance=u_balance)



@app.route("/sell", methods=['GET','POST'])
@is_logged_in
def sell():
        
    old_balance = User.query.filter_by(username=session['username']).first()
    old_balance.balance
    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        symbol = request.form['symbol']
        data = controller.get_quote(symbol)
        name = data['Name']
        symbol = data['Symbol']
        price = data['LastPrice']
        quantity = (request.form['quantity'])
        total = (price*int(quantity))

        id = User.query.filter_by(username=session['username']).first().id
        transaction = Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first()

        if int(quantity) > transaction.c_quantity:
            flash('Transaction not allowed.','danger')
            return redirect(url_for('sell'))

        elif Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first():
            transaction.c_quantity = transaction.c_quantity - int(quantity)
            transaction.c_total = transaction.c_total - total
            new_balance = (old_balance.balance + total)
            new_balance = round(new_balance, 2)
            old_balance.balance = new_balance                           

            db.session.commit()
            flash('Stock Sold.','success')

        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = Transaction.query.filter_by(t_id=u_id).all()            

        
        return render_template('sell.html',transaction=transaction,u_balance=u_balance)

    else:
        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = Transaction.query.filter_by(t_id=u_id).all()

        
        return render_template("sell.html", transaction=transaction,u_balance=u_balance)


#Alphavantage
@app.route("/alphavantage")
@is_logged_in
def alphavantage():
    return render_template("alphavantage.html")


@app.route("/av_buy", methods=['GET','POST'])
@is_logged_in
def av_buy():
        
    old_balance = User.query.filter_by(username=session['username']).first()
    old_balance.balance
    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        symbol = request.form['symbol']
        data = controller.av_get_quote(symbol)
        print(type(data))
        symbol = data['Meta Data']['2. Symbol']
        last_price = data['Time Series (Daily)'] ['2018-05-04'] ['4. close']
        price = last_price
        price = float(price)
        quantity = request.form['quantity']
        total = (price*int(quantity))

        id = User.query.filter_by(username=session['username']).first().id
        transaction = av_Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first()
        balance = User.query.filter_by(username=session['username']).first().balance
        if balance < total:
            flash("Insufficient funds.",'danger')
            return redirect(url_for('av_buy'))
        
        elif av_Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first():
            transaction.c_quantity = transaction.c_quantity + int(quantity)
            transaction.c_total = transaction.c_total + total
            new_balance = (old_balance.balance - total)
            new_balance = round(new_balance, 2)
            old_balance.balance = new_balance                           

            db.session.commit()
            flash('Stocks Updated','success')

        else:
            transaction = av_Transaction(c_symbol=symbol,c_lastprice=price,c_quantity=quantity,c_total=total,av_t=user)
                
            new_balance = (old_balance.balance - total)
            new_balance = round(new_balance, 2)
            old_balance.balance = new_balance                           
            db.session.add(transaction)
            db.session.commit()
            flash('Stocks purchased for new company.', 'success')

        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = av_Transaction.query.filter_by(t_id=u_id).all()            
   
        
        return render_template('av_buy.html', u_balance = u_balance, transaction=transaction)

    else:
        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = av_Transaction.query.filter_by(t_id=u_id).all()
        #for i in transaction:
            #c_name = i.c_name
            #c_symbol = i.c_symbol
            #c_lastprice = i.c_lastprice
            #c_quantity = i.c_quantity


        return render_template("av_buy.html",transaction=transaction,u_balance=u_balance)



@app.route("/av_sell", methods=['GET','POST'])
@is_logged_in
def av_sell():
        
    old_balance = User.query.filter_by(username=session['username']).first()
    old_balance.balance
    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        symbol = request.form['symbol']
        data = controller.av_get_quote(symbol)

        symbol = data['Meta Data']['2. Symbol']
        last_price = data['Time Series (Daily)'] ['2018-05-04'] ['4. close']
        price = last_price
        price = float(price)
        quantity = (request.form['quantity'])
        quantity = request.form['quantity']
        total = (price*int(quantity))

        id = User.query.filter_by(username=session['username']).first().id
        transaction = av_Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first()

        if int(quantity) > transaction.c_quantity:
            flash('Transaction not allowed.','danger')
            return redirect(url_for('av_sell'))

        elif av_Transaction.query.filter_by(t_id=id, c_symbol=request.form['symbol']).first():
            transaction.c_quantity = transaction.c_quantity - int(quantity)
            transaction.c_total = transaction.c_total - total
            new_balance = (old_balance.balance + total)
            new_balance = round(new_balance, 2)
            old_balance.balance = new_balance                           

            db.session.commit()
            flash('Stock Sold.','success')

        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = av_Transaction.query.filter_by(t_id=u_id).all()            

        
        return render_template('av_sell.html',transaction=transaction,u_balance=u_balance)

    else:
        u_balance = User.query.filter_by(username=session['username']).first().balance
        u_id = User.query.filter_by(username=session['username']).first().id
        transaction = av_Transaction.query.filter_by(t_id=u_id).all()

        
        return render_template("av_sell.html", transaction=transaction,u_balance=u_balance)



if __name__ == "__main__":
    app.run(debug=True)
