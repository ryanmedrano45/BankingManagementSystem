# Imports the created database
from db import db

# User model
class User(db.Model):
    # Sets the table name
    __tablename__ = 'users'
    # Registers the attributes, which are all required
    u_userID = db.Column(db.Integer, primary_key=True)
    u_firstName = db.Column(db.String(32), nullable=False)
    u_lastName = db.Column(db.String(32), nullable=False)
    u_email = db.Column(db.String(64), nullable=False)
    u_phoneNumber = db.Column(db.String(15), nullable=False)
    u_address = db.Column(db.String(128), nullable=False)
    u_dateOfBirth = db.Column(db.String(32), nullable=False)
    u_password = db.Column(db.String(128), nullable=False)

# Checking Account model
class CheckingAccount(db.Model):
    # Sets the table name
    __tablename__ = 'checkingAccount'
    # Registers the attributes
    ca_accountID = db.Column(db.Integer, primary_key=True)
    ca_userID = db.Column(db.Integer, db.ForeignKey('users.u_userID'))
    ca_totalBalance = db.Column(db.Float)

# Savings Account model
class SavingsAccount(db.Model):
    # Sets the table name
    __tablename__ = 'savingsAccount'
    # Registers the attributes
    sa_accountID = db.Column(db.Integer, primary_key=True)
    sa_userID = db.Column(db.Integer, db.ForeignKey('users.u_userID'))
    sa_totalBalance = db.Column(db.Float)

# Withdrawals model
class Withdrawals(db.Model):
    # Sets the table name
    __tablename__ = 'withdrawals'
    # Registers the attributes
    w_transactionID = db.Column(db.Integer, primary_key=True)
    w_amountWithdrawn = db.Column(db.Float)
    w_userID = db.Column(db.Integer, db.ForeignKey('users.u_userID'))
    w_accountID = db.Column(db.Integer)

# Deposits model
class Deposits(db.Model):
    # Sets the table name
    __tablename__ = 'deposits'
    # Registers the attributes
    d_transactionID = db.Column(db.Integer, primary_key=True)
    d_amountDeposited = db.Column(db.Float)
    d_userID = db.Column(db.Integer, db.ForeignKey('users.u_userID'))
    d_accountID = db.Column(db.Integer)

# Purchases model
class Purchases(db.Model):
    # Sets the table name
    __tablename__ = 'purchases'
    # Registers the attributes
    p_transactionID = db.Column(db.Integer, primary_key=True)
    p_seller = db.Column(db.String(32))
    p_itemPurchased = db.Column(db.String(32))
    p_userID = db.Column(db.Integer, db.ForeignKey('users.u_userID'))
    p_accountID = db.Column(db.Integer)

# Money Transfers model
class MoneyTransfers(db.Model):
    # Sets the table name
    __tablename__ = 'moneyTransfers'
    # Registers the attributes
    mt_transactionID = db.Column(db.Integer, primary_key=True)
    mt_amountTransferred = db.Column(db.Float)
    mt_userID = db.Column(db.Integer)
    mt_senderAccountID = db.Column(db.Integer)
    mt_receiverAccountID = db.Column(db.Integer)