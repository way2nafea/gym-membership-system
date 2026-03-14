from flask import Flask, render_template, request, redirect, session
from config import db, cursor
from datetime import date
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "gym_secret_key")


# ---------------------
# DATABASE CHECK
# ---------------------
try:
    cursor.execute("SELECT 1")
    print("Database connected successfully.")
except Exception as e:
    print("Database connection error:", e)
    exit(1)


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

        try:
            query = "INSERT INTO users(name,email,password,phone) VALUES(%s,%s,%s,%s)"
            cursor.execute(query,(name,email,password,phone))
            db.commit()

            return redirect('/')

        except Exception as e:
            return render_template("user/register.html",error="Registration Failed")

    return render_template("user/register.html")


# ---------------------
# USER LOGIN
# ---------------------
@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    try:
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
        user = cursor.fetchone()
    except:
        return render_template("user/login.html",error="Database Error")

    if user:
        session['user_id'] = user[0]
        return redirect('/dashboard')

    return render_template("user/login.html",error="Invalid Login")


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

    try:
        cursor.execute(
            "INSERT INTO memberships(user_id,plan_id,purchase_date) VALUES(%s,%s,%s)",
            (user_id,plan_id,date.today())
        )
        db.commit()
    except:
        return "Purchase Failed"

    return redirect('/my_membership')


# ---------------------
# USER MEMBERSHIP
# ---------------------
@app.route('/my_membership')
def my_membership():

    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']

    query = """
    SELECT m.id,p.plan_name,p.price,m.purchase_date
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


# =====================
# ADMIN SECTION
# =====================


# ---------------------
# ADMIN LOGIN PAGE
# ---------------------
@app.route('/admin')
def admin_login():

    return render_template("admin/admin_login.html")


# ---------------------
# ADMIN LOGIN
# ---------------------
@app.route('/admin_login',methods=['POST'])
def admin_login_post():

    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        "SELECT * FROM admin WHERE username=%s AND password=%s",
        (username,password)
    )

    admin = cursor.fetchone()

    if admin:
        session['admin'] = admin[0]
        return redirect('/admin/dashboard')

    return render_template("admin/admin_login.html",error="Invalid Login")


# ---------------------
# ADMIN DASHBOARD
# ---------------------
@app.route('/admin/dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    try:

        # total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        # memberships
        cursor.execute("SELECT COUNT(*) FROM memberships")
        total_memberships = cursor.fetchone()[0]

        # revenue
        cursor.execute("""
        SELECT SUM(p.price)
        FROM memberships m
        JOIN plans p ON m.plan_id = p.id
        """)
        revenue = cursor.fetchone()[0] or 0


        # chart data
        cursor.execute("""
        SELECT p.plan_name, COUNT(m.id)
        FROM plans p
        LEFT JOIN memberships m ON p.id = m.plan_id
        GROUP BY p.plan_name
        """)

        data = cursor.fetchall()

        plan_names = [row[0] for row in data]
        plan_values = [row[1] for row in data]


    except Exception as e:
        return "Database Error"

    return render_template(
        "admin/admin_dashboard.html",
        users=total_users,
        memberships=total_memberships,
        revenue=revenue,
        plan_names=plan_names,
        plan_values=plan_values
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
# ADD PLAN
# ---------------------
@app.route('/admin/add_plan',methods=['POST'])
def add_plan():

    if 'admin' not in session:
        return redirect('/admin')

    plan_name = request.form['plan_name']
    price = request.form['price']

    cursor.execute(
        "INSERT INTO plans(plan_name,price) VALUES(%s,%s)",
        (plan_name,price)
    )

    db.commit()

    return redirect('/admin/plans')


# ---------------------
# DELETE PLAN
# ---------------------
@app.route('/admin/delete_plan/<int:plan_id>')
def delete_plan(plan_id):

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("DELETE FROM plans WHERE id=%s",(plan_id,))
    db.commit()

    return redirect('/admin/plans')


# ---------------------
# ADMIN MEMBERSHIPS
# ---------------------
@app.route('/admin/memberships')
def admin_memberships():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("""
    SELECT m.id,u.name,p.plan_name,p.price,m.purchase_date
    FROM memberships m
    JOIN users u ON m.user_id=u.id
    JOIN plans p ON m.plan_id=p.id
    """)

    memberships = cursor.fetchall()

    return render_template("admin/memberships.html",memberships=memberships)


# ---------------------
# ADMIN REPORTS
# ---------------------
@app.route('/admin/reports')
def admin_reports():

    if 'admin' not in session:
        return redirect('/admin')

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM memberships")
    total_memberships = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM plans")
    total_plans = cursor.fetchone()[0]

    cursor.execute("""
    SELECT SUM(p.price)
    FROM memberships m
    JOIN plans p ON m.plan_id=p.id
    """)

    total_revenue = cursor.fetchone()[0] or 0

    return render_template(
        "admin/reports.html",
        total_users=total_users,
        total_memberships=total_memberships,
        total_plans=total_plans,
        total_revenue=total_revenue
    )


# ---------------------
# ADMIN LOGOUT
# ---------------------
@app.route('/admin/logout')
def admin_logout():

    session.pop('admin',None)

    return redirect('/admin')


# ---------------------
# RUN APP
# ---------------------
if __name__ == "__main__":
    app.run(debug=True)