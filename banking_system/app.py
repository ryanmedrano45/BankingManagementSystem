# Imports for flask
from flask import Flask, render_template, redirect, url_for, request, session
# Imports migrations used for the database
from flask_migrate import Migrate
# Imports the database
from db import db

# Initializes the Flask application
app = Flask(__name__)

# Necessary secret key
app.secret_key = ''

# Configures the database using PostgreSQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@localhost/banking_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializes the database
db.init_app(app)

# Initialize Migration object
migrate = Migrate(app, db)

# Import models after initializing db and migrate
from models import User, CheckingAccount, SavingsAccount, Withdrawals, Deposits, Purchases, MoneyTransfers

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    # Checks if the user submitted the form
    if request.method == 'POST':
        # Recieves input from the user
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']

        # Finds matching user in the database
        user = User.query.filter_by(u_firstName=first_name, u_lastName=last_name).first()

        # Checks if the user exists and if the password matches
        if user and user.u_password == password:
            # Redirects user to the main page using their userID to keep track of the session
            session['user_id'] = user.u_userID
            return redirect(url_for('main_page'))
        # Redirects back to the login page with an error
        else:
            return render_template('login.html', error="Invalid credentials")
    # Displays the login page
    return render_template('login.html')

# Create Account page
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    # Checks if the user submitted the form
    if request.method == 'POST':
        # Recieves input from the user
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        dob = request.form['dob']
        password = request.form['password']

        # Checks if the user already exists
        existing_user = User.query.filter_by(u_email=email).first()
        # Sends them back to the create an account page with an error if so
        if existing_user:
            return render_template('create_account.html', error="This email already exists in the system")

        # Creates a new user and adds them to the database
        new_user = User(
            u_firstName=first_name,
            u_lastName=last_name,
            u_email=email,
            u_phoneNumber=phone_number,
            u_address=address,
            u_dateOfBirth=dob,
            u_password=password
        )
        db.session.add(new_user)
        db.session.commit()

        # Creates a checking and savings account for the new user and adds them to the datahbase
        checking_account = CheckingAccount(
            ca_userID=new_user.u_userID,
            ca_totalBalance=0.0  
        )
        savings_account = SavingsAccount(
            sa_userID=new_user.u_userID,
            sa_totalBalance=0.0  
        )
        db.session.add(checking_account)
        db.session.add(savings_account)
        db.session.commit()

        # Redirects to the login page after the user is finished creating an account
        return redirect(url_for('login'))
    # Displays the create account page
    return render_template('create_account.html')

# Main page
@app.route('/main')
def main_page():
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login')) 
    # Displays the main page
    return render_template('main.html')

# Logout functionality
@app.route('/logout', methods=['POST'])
def logout():
    # Removes the user from the current session
    session.pop('user_id', None)
    # Displays the login page
    return redirect(url_for('login'))

# Account Information page
@app.route('/account_info')
def account_info():
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))
    # Gets the user from the user ID
    user = User.query.get(session['user_id'])
    # Displays the account information page
    return render_template('account_information.html', user=user)

# Checking Account page
@app.route('/checking_account', methods=['GET', 'POST'])
def checking_account():
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))
    
    # Finds the checking account from the database using the user ID
    user_id = session['user_id']
    checking_account = CheckingAccount.query.filter_by(ca_userID=user_id).first()

    # Displays the checking account page
    return render_template('checking_account.html', account=checking_account)

# Savings Account page
@app.route('/savings_account', methods=['GET', 'POST'])
def savings_account():
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))
    
    # Finds the savings account from the database using the user ID
    user_id = session['user_id']
    savings_account = SavingsAccount.query.filter_by(sa_userID=user_id).first()

    # Displays the savings account page
    return render_template('savings_account.html', account=savings_account)

# Withdrawal page
@app.route('/withdraw/<account_type>', methods=['GET', 'POST'])
def withdraw(account_type):
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))

    # Finds the account from the database using the user ID
    user_id = session['user_id']
    account = None
    # Gets the correct account
    if account_type == 'checking':
        account = CheckingAccount.query.filter_by(ca_userID=user_id).first()
        balance_field = 'ca_totalBalance'
        account_id_field = 'ca_accountID'
    elif account_type == 'savings':
        account = SavingsAccount.query.filter_by(sa_userID=user_id).first()
        balance_field = 'sa_totalBalance'
        account_id_field = 'sa_accountID'

    # Checks if the user submitted the form
    if request.method == 'POST':
        # Gets the amount to withdraw
        amount = float(request.form['amount'])

        # Checks if the balance is high enough to withdraw that amount
        current_balance = getattr(account, balance_field) 
        # Tells the user if it is not
        if amount > current_balance:
            return "<h1>Insufficient Balance</h1>"

        # Updates the account balance to the database
        setattr(account, balance_field, current_balance - amount)  
        db.session.commit()

        # Creates a new withdrawal and adds it to the database
        withdrawal = Withdrawals(
            w_amountWithdrawn=amount,
            w_userID=user_id,
            w_accountID=getattr(account, account_id_field)
        )
        db.session.add(withdrawal)
        db.session.commit()

        # Redirects to the proper account page
        return redirect(url_for(f'{account_type}_account'))

    # Displays the withdrawal page
    return render_template('withdraw.html', account_type=account_type)

# Deposit page
@app.route('/deposit/<account_type>', methods=['GET', 'POST'])
def deposit(account_type):
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))

    # Finds the account from the database using the user ID
    user_id = session['user_id']
    account = None
    # Gets the correct account
    if account_type == 'checking':
        account = CheckingAccount.query.filter_by(ca_userID=user_id).first()
        balance_field = 'ca_totalBalance'
        account_id_field = 'ca_accountID'
    elif account_type == 'savings':
        account = SavingsAccount.query.filter_by(sa_userID=user_id).first()
        balance_field = 'sa_totalBalance'
        account_id_field = 'sa_accountID'

    # Checks if the user submitted the form
    if request.method == 'POST':
        # Gets the amount to deposit
        amount = float(request.form['amount'])

        # Updates the account balance to the database
        current_balance = getattr(account, balance_field)
        setattr(account, balance_field, current_balance + amount)
        db.session.commit()

        # Creates a new deposit and adds it to the database
        deposit = Deposits(
            d_amountDeposited=amount,
            d_userID=user_id,
            d_accountID=getattr(account, account_id_field)
        )
        db.session.add(deposit)
        db.session.commit()

        # Redirects to the proper account page
        return redirect(url_for(f'{account_type}_account'))
    
    # Displays the deposit page
    return render_template('deposit.html', account_type=account_type)

# Purchase page
@app.route('/purchase/<account_type>', methods=['GET', 'POST'])
def purchase(account_type):
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))

    # Finds the account from the database using the user ID
    user_id = session['user_id']
    account = None
    # Gets the correct account
    if account_type == 'checking':
        account = CheckingAccount.query.filter_by(ca_userID=user_id).first()
        balance_field = 'ca_totalBalance'
        account_id_field = 'ca_accountID'
    elif account_type == 'savings':
        account = SavingsAccount.query.filter_by(sa_userID=user_id).first()
        balance_field = 'sa_totalBalance'
        account_id_field = 'sa_accountID'

    # Checks if the user submitted the form
    if request.method == 'POST':
        # Gets purchase information
        amount = float(request.form['amount'])
        seller = request.form['seller']
        item = request.form['item']

        # Checks if the balance is high enough to purchase that amount
        current_balance = getattr(account, balance_field)
        # Tells the user if it is not
        if amount > current_balance:
            return "<h1>Insufficient Balance</h1>"

        # Updates the account balance to the database
        setattr(account, balance_field, current_balance - amount)
        db.session.commit()

        # Creates a new purchase and adds it to the database
        purchase = Purchases(
            p_seller=seller,
            p_itemPurchased=item,
            p_userID=user_id,
            p_accountID=getattr(account, account_id_field)
        )
        db.session.add(purchase)
        db.session.commit()

        # Redirects to the proper account page
        return redirect(url_for(f'{account_type}_account'))

    # Displays the purchase page
    return render_template('purchase.html', account_type=account_type)

# Transfer page
@app.route('/transfer/<from_account>', methods=['GET', 'POST'])
def transfer(from_account):
    # Checks if the user is logged in or not
    if 'user_id' not in session:
        # Redirects user to the login page if not
        return redirect(url_for('login'))

    # Finds the accounts from the database using the user ID
    user_id = session['user_id']
    from_acc = None
    to_acc = None
    # Gets the correct transferred from account and transferred to account
    if from_account == 'checking':
        from_acc = CheckingAccount.query.filter_by(ca_userID=user_id).first()
        to_acc = SavingsAccount.query.filter_by(sa_userID=user_id).first()
        from_balance_field = 'ca_totalBalance'
        to_balance_field = 'sa_totalBalance'
        to_account = 'savings'
        from_account_id = from_acc.ca_accountID
        to_account_id = to_acc.sa_accountID
    elif from_account == 'savings':
        from_acc = SavingsAccount.query.filter_by(sa_userID=user_id).first()
        to_acc = CheckingAccount.query.filter_by(ca_userID=user_id).first()
        from_balance_field = 'sa_totalBalance'
        to_balance_field = 'ca_totalBalance'
        to_account = 'checking'
        from_account_id = from_acc.sa_accountID
        to_account_id = to_acc.ca_accountID

    # Checks if the user submitted the form
    if request.method == 'POST':
        # Gets transfer amount
        amount = float(request.form['amount'])
        current_from_balance = getattr(from_acc, from_balance_field)

        # Checks if the balance is high enough to transfer that amount
        if amount > current_from_balance:
            # Tells the user if it is not
            return "<h1>Insufficient Balance</h1>"

        # Adjusts account balances to the database
        setattr(from_acc, from_balance_field, current_from_balance - amount)
        setattr(to_acc, to_balance_field, getattr(to_acc, to_balance_field) + amount)
        db.session.commit()

        # Creates a new Money Transfer and adds it to the database
        transfer_record = MoneyTransfers(
            mt_amountTransferred=amount,
            mt_userID=user_id,
            mt_senderAccountID=from_account_id,
            mt_receiverAccountID=to_account_id
        )
        db.session.add(transfer_record)
        db.session.commit()

        # Redirects to the proper account page
        return redirect(url_for(f'{from_account}_account'))

    # Displays the transfer page
    return render_template('transfer.html', from_account=from_account, to_account=to_account)

# Prints errors when the app is run
if __name__ == '__main__':
    app.run(debug=True)
