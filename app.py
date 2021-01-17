from flask import (
    Flask,
    session,
    request,
    jsonify,
    json,
    make_response
)
import json
import secrets
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tmp/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "JIHDGJIDHFHJDFJ"
app.config['SESSION_TYPE'] = 'sqlalchemy'
# Init db

db = SQLAlchemy(app)


app.config['SESSION_SQLALCHEMY'] = db

sess = Session(app)
# init ma

ma = Marshmallow(app)

# init migration
migrate = Migrate(app, db)


# for flask migration
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u"Please Login First"

# login helper


@login_manager.user_loader
def load_user(user_id):
    return Register.query.filter_by(id=user_id).first()


# type of users to be allowed or registered
class Usertype(db.Model, UserMixin):
    __tablename__ = "Usertype"
    id = db.Column(db.Integer, primary_key=True)
    Usertype_name = db.Column(db.String(50), unique=True)
    # usertype_id = db.Column(db.String(100), unique=True)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.Usertype_name


# type of currency that the system allows to be registered
class Currency_allowed(db.Model, UserMixin):
    __tablename__ = "Currency_allowed"
    id = db.Column(db.Integer, primary_key=True)
    Currency_name = db.Column(db.String(50), unique=True)
    # # currency_id = db.Column(db.String(100), unique=True)
    # Currency_rate = db.Column(db.BigInteger, default=0)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.Currency_name


# registration route
class Register(db.Model, UserMixin):
    __tablename__ = "Register"
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), unique=True)
    UserName = db.Column(db.String(50), unique=True)
    Userid = db.Column(db.String(50), unique=True)
    Reg_Usertype = db.Column(db.String(100))
    Reg_Usertype_id = db.Column(db.String(100))  # delete later
    CurrencyName = db.Column(db.String(50))
    Password = db.Column(db.String(200), unique=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.Name


class Wallet_tb(db.Model, UserMixin):
    __tablename__ = "Wallet_tb"
    id = db.Column(db.Integer, primary_key=True)
    Wallet_name = db.Column(db.String(100))
    wallet_id = db.Column(db.String(100))
    Wallet_currency = db.Column(db.String(100))
    Userid = db.Column(db.String(100))
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.Wallet_name


class Wallet_transaction(db.Model, UserMixin):
    __tablename__ = "Wallet_transaction"
    id = db.Column(db.Integer, primary_key=True)
    Transcation_id = db.Column(db.String(100))
    Transcation_type = db.Column(db.String(100))
    Transcation_status = db.Column(
        db.String(100), unique=False, default='approved')
    wallet_id = db.Column(db.String(100))
    Userid = db.Column(db.String(100))
    balance = db.Column(db.BigInteger, default=0)

    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.Transcation_id


@app.route('/')
def index():
    return "Hello world"


def walletgenerate(Wallet_name, wallet_id, Wallet_currency, Userid):
    walletdump = Wallet_tb(Wallet_name=Wallet_name, wallet_id=wallet_id,
                           Wallet_currency=Wallet_currency, Userid=Userid)
    db.session.add(walletdump)
    db.session.commit()
    print('wallet created')


def wallettnx(wallet_id, Userid):
    createtnx = Wallet_transaction(wallet_id=wallet_id, Userid=Userid)
    db.session.add(createtnx)
    createtnx.Transcation_id = secrets.token_hex(5)
    createtnx.Transcation_status = "approved"
    db.session.commit()
    print('Transcation completed')


@app.route('/v1/register', methods=['POST'])
def register():
    Name = request.json['Name']
    UserName = request.json['UserName']
    Password = request.json['Password']
    Password = generate_password_hash(Password, method="sha256")
    Reg_Usertype = request.json['Reg_Usertype']
    Reg_Usertype = Reg_Usertype.capitalize()
    CurrencyName = request.json['CurrencyName']
    Wallet_name = request.json['Wallet_name']

    if Name == '' or UserName == '' or Password == '' or Reg_Usertype == '' or CurrencyName == '':
        return jsonify({'Message': 'KIndly Ensure that all feilds are not empty'}), 400
    usercheck = Register.query.filter_by(Name=Name).first(
    ) or Register.query.filter_by(UserName=UserName).first()
    if usercheck:
        return jsonify({'Message': 'Name or username already exist'}), 401
    if current_user.is_authenticated:
        if current_user.Reg_Usertype == "Elite" and Reg_Usertype == "Admin":
            return jsonify({'Message': 'Soory, you can not register an admin'}), 401
        if current_user.Reg_Usertype == "Noob" and Reg_Usertype == "Admin":
            return jsonify({'Message': 'Soory, you can not register an admin'}), 401

    if db.session.query(Usertype).filter(Usertype.Usertype_name == Reg_Usertype).count() == 1:
        if db.session.query(Currency_allowed).filter(Currency_allowed.Currency_name == CurrencyName).count() == 1:
            if Reg_Usertype == "Admin":
                if current_user.is_anonymous == True:
                    return jsonify({'Message': 'KIndly login to register as an admin'}), 401
            wallet_id = secrets.token_hex(5)
            Wallet_currency = CurrencyName
            register_update = Register(Name=Name, UserName=UserName, Password=Password,
                                       Reg_Usertype=Reg_Usertype, CurrencyName=CurrencyName)
            db.session.add(register_update)
            Userid = secrets.token_hex(5)
            register_update.Userid = Userid
            if Reg_Usertype == "Admin":
                return jsonify({'Message': 'Registration successfull.'})
            wallettnx(wallet_id=wallet_id, Userid=Userid)
            walletgenerate(Wallet_name, wallet_id,
                           Wallet_currency, Userid=Userid)

            # register_update.Reg_Usertype_id=usertype_newid
            db.session.commit()
            if current_user.is_authenticated:
                if current_user.Reg_Usertype == 'Admin':
                    return jsonify({'Message': 'Registration successfull.Kindly inform ' + Name + ' to login in and have access the wallet'})
            return jsonify({'Message': 'Registration successfull.Kindly login to access your wallet'})
        else:
            return jsonify({'Message': 'Currency Do not Exist'}), 400
    else:
        return jsonify({'Message': 'UserType Does Not Exist'}), 400
        # return jsonify({'Message':'Seen usertype and currency'})
        # productscart = Currency_allowed.query.filter_by(Currency_name=CurrencyName).first()


# login route
@app.route('/v1/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'Message': "You have login Already"})
    UserName = request.json['UserName']
    Password = request.json['Password']
    if UserName == '':
        return jsonify({'Message': "Username Can not be empty"}), 401
    user = Register.query.filter_by(UserName=UserName).first()
    if user and check_password_hash(user.Password, Password):
        # if user and user.Password == Password:
        login_user(user)
        print(current_user.Reg_Usertype)
        return jsonify({'Message': "Login Successful"})
    else:
        return jsonify({'Message': "Wrong Password or Username"}), 401


# Wallet create route
@app.route('/v1/wallet', methods=['POST'])
def wallet():
    if current_user.is_anonymous:
        return jsonify({'Message': 'Not allowed, Kindly login to create a wallet', 'Status': '401'}), 401
    if current_user.Reg_Usertype == "Elite":
        Wallet_name = request.json['Wallet_name']
        Wallet_currency = request.json['Wallet_currency']
        if Wallet_name == '' or Wallet_currency == '':
            return jsonify({'Message': 'KIndly Ensure that all feilds are not empty'}), 400
        wallet_id = secrets.token_hex(5)
        Userid = current_user.Userid
        walletusercheck = Wallet_tb.query.filter_by(Userid=Userid).first(
        ) and Wallet_tb.query.filter_by(Wallet_currency=Wallet_currency).first()
        if walletusercheck:
            return jsonify({'Message': 'Sorry, You have a ' + Wallet_currency + ' wallet, kindly choose a new currency'}), 401
        if current_user.Reg_Usertype == "Admin":
            return jsonify({'Message': 'Admin can not have a wallet'})
        if db.session.query(Currency_allowed).filter(Currency_allowed.Currency_name == Wallet_currency).count() == 1:
            walletdump = Wallet_tb(Wallet_name=Wallet_name, wallet_id=wallet_id,
                                   Wallet_currency=Wallet_currency, Userid=Userid)
            db.session.add(walletdump)
            db.session.commit()
            wallettnx(wallet_id=wallet_id, Userid=Userid)
            return jsonify({'Message': 'Wallet Created Successfully'})
        else:
            return jsonify({'Message': 'Currency Do not Exist'}), 400
    elif current_user.Reg_Usertype == "Noob":
        return jsonify({'Message': 'Noob are only allowed to create a single wallet'}), 401
    else:
        return jsonify({'Message': 'Admin is not allowed to have a wallet'}), 401


# funding wallet route
@app.route('/v1/funding', methods=['PUT'])
# @login_required
def funding():
    if current_user.is_anonymous:
        return jsonify({'Message': 'Not allowed, Kindly login to fund a wallet', 'Status': '401'}), 401
    if current_user.Reg_Usertype == "Admin":
        wallet_id = request.json['wallet_id']
        Userid = request.json['Userid']
        amount = request.json['amount']
        statusupdate = request.json['statusupdate']
        updatecurrency = request.json['updatecurrency']

        if wallet_id == '' or Userid == '' or amount == '' or statusupdate == '' or updatecurrency == '':
            return jsonify({'Message': 'Kindly Ensure that all feilds are not empty'}), 400

        adminfunding = Wallet_transaction.query.filter_by(
            Userid=Userid, wallet_id=wallet_id).first()
        if adminfunding:
            if type(amount) == str:
                return jsonify({'Message': 'KIndly Ensure that all feilds are filled correctly and are not empty'}), 400
            adminfunding.balance = int(amount + adminfunding.balance)
            adminfunding.Transcation_status = statusupdate
            db.session.commit()

            if updatecurrency == 'yes':
                # return jsonify({'Message' :'still working on currency change'})
                currencychange = request.json['currencychange']
                currencychangeto = request.json['currencychangeto']
                Userid = request.json['Userid']
                if currencychange == '' or currencychangeto == '':
                    return jsonify({'Message': 'Kindly Ensure that all feilds are not empty'}), 400
                if db.session.query(Currency_allowed).filter(Currency_allowed.Currency_name == currencychangeto).count() == 0:
                    return jsonify({'Message': 'Currency Does Not Exist'}), 400
                Userid = Userid
                walletusercheck = Wallet_tb.query.filter_by(
                    Userid=Userid, Wallet_currency=currencychangeto).all()
                print(walletusercheck)
                if walletusercheck:
                    return jsonify({'Message': 'Sorry, You have a ' + currencychangeto + ' wallet, kindly choose a new currency'}), 401
                almostdone = Wallet_tb.query.filter_by(
                    Userid=Userid, wallet_id=wallet_id).first()
                if almostdone:
                    almostdone.Wallet_currency = currencychangeto
                    db.session.commit()
                    return('you are free to update the user currency')
                return('Userid or wallet id does not exist')
            if updatecurrency == 'no':
                return jsonify({'Message': 'Amount or status updated successfully'})
            return jsonify({'Message': 'wrong input yes OR no'})
        return jsonify({'Message': 'wrong wallet id or User id'})
    Wallet_currency = request.json['Wallet_currency']
    amount = request.json['amount']
    if Wallet_currency == '':
        return jsonify({'Message': 'KIndly Ensure that all feilds are not empty'}), 400
    if amount == '':
        return jsonify({'Message': 'KIndly Ensure that all feilds are not empty'}), 400
    if type(amount) == str:
        return jsonify({'Message': 'KIndly Ensure that all feilds are filled correctly and are not empty'}), 400
    confirmdetails1 = Wallet_tb.query.filter_by(
        Userid=current_user.Userid, Wallet_currency=Wallet_currency).first()
    if confirmdetails1:
        wallet_id = confirmdetails1.wallet_id
        confirmdetails2 = Wallet_transaction.query.filter_by(
            Userid=current_user.Userid, wallet_id=wallet_id).first()
        if confirmdetails2.Transcation_status == 'pending':
            return jsonify({'Message': 'Sorry, you still have pending transcation. Kindly wait for your last transcation to be approved.'}), 401
        confirmdetails2.balance = int(amount + confirmdetails2.balance)
        confirmdetails2.Transcation_status = 'pending'
        now = datetime.now()
        confirmdetails2.date_created = now
        db.session.commit()
        print(confirmdetails2.balance)
        return jsonify({'Message': Wallet_currency + ' Funded. Kindly wait for approval'})
    return jsonify({'Message': ' Sorry, You do not have ' + Wallet_currency + ' wallet or ' + Wallet_currency + ' does not exit. You only have '})


@app.route('/v1/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'Message': "You have successfully Logout", 'Status': '200'})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
