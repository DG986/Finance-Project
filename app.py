import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session["user_id"]

    # 1. Get the user's transactions from the database
    # We group by symbol to sum up the shares for each stock
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id
    )

    # 2. Get the user's current cash balance
    cash_rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_rows[0]["cash"]

    # 3. Initialize variables for portfolio value
    grand_total = cash

    # 4. Iterate over the stocks the user owns to get current data
    for stock in stocks:
        # Use the lookup function to get the current price and name
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total_value"] = stock["price"] * stock["total_shares"]
        grand_total += stock["total_value"]

    # 5. Render the portfolio page, passing all the data to the template
    return render_template("index.html", stocks=stocks, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as in submitting the buy form)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")

        # 1. Validate the user's input
        if not symbol:
            return apology("must provide stock symbol", 400)

        # Check if shares input is valid
        if not shares_str or not shares_str.isdigit() or int(shares_str) <= 0:
            return apology("shares must be a positive integer", 400)

        shares = int(shares_str)

        # 2. Get the stock's current data
        stock = lookup(symbol)
        if not stock:
            return apology("invalid stock symbol", 400)

        # 3. Check if the user can afford the purchase
        user_id = session["user_id"]
        # Get user's cash from the database
        rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = rows[0]["cash"]

        total_cost = shares * stock["price"]

        if user_cash < total_cost:
            return apology("not enough cash", 400)

        # 4. Update the database
        # Subtract the cost from the user's cash
        new_cash_balance = user_cash - total_cost
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_balance, user_id)

        # Add the transaction to the history table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, stock["symbol"], shares, stock["price"])

        # 5. Redirect user to home page
        flash("Bought!") # Optional: Shows a success message
        return redirect("/")

    # User reached route via GET (by clicking a link)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    # Query the database for all transactions for the current user
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", user_id
    )

    # Render the history page, passing the transactions to the template
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as in submitting a form via login.html)
    if request.method == "POST":

        # 1. Get user input from the form
        username = request.form.get("username")
        password = request.form.get("password")

        # 2. Validate the input
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # 3. Query database for the username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # 4. Validate the user's credentials
        # Ensure username exists and password is correct
        # check_password_hash compares the submitted password to the stored hash
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # 5. Remember which user has logged in
        # This line creates the "session", storing the user's ID
        session["user_id"] = rows[0]["id"]

        # 6. Redirect user to home page
        return redirect("/")

    # User reached route via GET (as in clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # This block handles when the user SUBMITS the form
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Make sure a symbol was entered
        if not symbol:
            return apology("must provide symbol", 400)

        # Use the lookup function
        stock = lookup(symbol)

        # Make sure the symbol was valid
        if not stock:
            return apology("invalid stock symbol", 400)

        # Show the results
        return render_template("quoted.html", stock=stock)

    # This block handles when the user FIRST VISITS the page
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as in submitting a form)
    if request.method == "POST":

        # 1. Get user input from the form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # 2. Validate the input
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not confirmation:
            return apology("must confirm password", 400)

        # Ensure password and confirmation match
        elif password != confirmation:
            return apology("passwords do not match", 400)

        # 3. Check if username already exists in the database
        # Query your database for the username. The db.execute should return a list of rows.
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username already exists", 400)

        # 4. If all checks pass, insert the new user into the database
        # Hash the user's password for security before storing it
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        # 5. Log the new user in automatically
        # Query database for newly created user
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # 6. Redirect user to home page
        return redirect("/")

    # User reached route via GET (as in clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    # Get user's stocks for the dropdown menu
    user_stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id
    )

    # User reached route via POST (submitting the sell form)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_to_sell_str = request.form.get("shares")

        # 1. Validate the input
        if not symbol:
            return apology("must select a stock", 400)

        if not shares_to_sell_str or not shares_to_sell_str.isdigit() or int(shares_to_sell_str) <= 0:
            return apology("shares must be a positive integer", 400)

        shares_to_sell = int(shares_to_sell_str)

        # Check if user owns enough shares to sell
        for stock in user_stocks:
            if stock["symbol"] == symbol:
                if stock["total_shares"] < shares_to_sell:
                    return apology("you don't own that many shares", 400)
                break

        # 2. Get current stock data
        quote = lookup(symbol)
        if not quote:
             return apology("error looking up stock", 500) # Should not happen if they own it

        # 3. Update the database
        sale_value = shares_to_sell * quote["price"]

        # Add money back to user's cash
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", sale_value, user_id)

        # Record the sale in transactions by adding a NEGATIVE number of shares
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, symbol, -shares_to_sell, quote["price"])

        # 4. Redirect with a success message
        flash("Sold!")
        return redirect("/")

    # User reached route via GET (clicking the "Sell" link)
    else:
        # Render the sell form, passing in the stocks they own
        return render_template("sell.html", stocks=user_stocks)
