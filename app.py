from flask import Flask, render_template, request, redirect, session
from config import db, cursor
from datetime import date

app = Flask(__name__)
app.secret_key = "gym_secret_key"


# ---------------------
# HOME
# ---------------------
@app.route('/')
def home():
    return render_template("user/login.html")


# ---------------------
# USER REGISTER
# ---------------------
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        query = "INSERT INTO users(name,email,password,phone) VALUES(%s,%s,%s,%s)"
        values = (name,email,password,phone)

        cursor.execute(query,values)
        db.commit()

        return redirect('/')

    return render_template("user/register.html")


# ---------------------
# USER LOGIN
# ---------------------
@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query,(email,password))

    user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        return redirect('/dashboard')

    return "Invalid Login"


# ---------------------
# USER DASHBOARD
# ---------------------
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/')

    cursor.execute("SELECT * FROM plans")
    plans = cursor.fetchall()

    return render_template("user/dashboard.html",plans=plans)


# ---------------------
# BUY MEMBERSHIP
# ---------------------
@app.route('/buy/<int:plan_id>')
def buy(plan_id):

    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    query = "INSERT INTO memberships(user_id,plan_id,purchase_date) VALUES(%s,%s,%s)"
    values = (user_id,plan_id,date.today())

    cursor.execute(query,values)
    db.commit()

    return redirect('/my_membership')


# ---------------------
# USER MEMBERSHIPS
# ---------------------
@app.route('/my_membership')
def my_membership():

    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    query = """
    SELECT m.id,p.plan_name,p.price,p.duration,m.purchase_date
    FROM memberships m
    JOIN plans p ON m.plan_id=p.id
    WHERE m.user_id=%s
    """

    cursor.execute(query,(user_id,))
    memberships = cursor.fetchall()

    return render_template("user/membership.html",memberships=memberships)


# ---------------------
# USER LOGOUT
# ---------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------------
# ADMIN LOGIN PAGE
# ---------------------
@app.route('/admin')
def admin_login():
    return render_template("admin/admin_login.html")


# ---------------------
# ADMIN LOGIN
# ---------------------
@app.route('/admin_login', methods=['POST'])
def admin_login_post():

    username = request.form['username']
    password = request.form['password']

    query = "SELECT * FROM admin WHERE username=%s AND password=%s"
    cursor.execute(query,(username,password))

    admin = cursor.fetchone()

    if admin:
        session['admin'] = admin[0]
        return redirect('/admin/dashboard')

    return "Invalid Admin Login"


# ---------------------
# ADMIN DASHBOARD
# ---------------------
@app.route('/admin/dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM memberships")
    total_memberships = cursor.fetchone()[0]

    cursor.execute("""
    SELECT SUM(price)
    FROM memberships m
    JOIN plans p ON m.plan_id=p.id
    """)
    revenue = cursor.fetchone()[0]

    if revenue is None:
        revenue = 0

    return render_template(
        "admin/admin_dashboard.html",
        users=total_users,
        memberships=total_memberships,
        revenue=revenue
    )


# ---------------------
# ADMIN USERS
# ---------------------
@app.route('/admin/users')
def view_users():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    return render_template("admin/users.html",users=users)


# ---------------------
# ADMIN PLANS
# ---------------------
@app.route('/admin/plans')
def admin_plans():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("SELECT * FROM plans")
    plans = cursor.fetchall()

    return render_template("admin/plans.html",plans=plans)


# ---------------------
# ADMIN LOGOUT
# ---------------------
@app.route('/admin/logout')
def admin_logout():

    session.pop('admin', None)

    return redirect('/admin')


# ---------------------
# RUN APP
# ---------------------
if __name__ == "__main__":
    app.run(debug=True)