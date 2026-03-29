from flask import Flask, render_template, request, redirect, session, url_for, flash
from config import db, cursor
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import smtplib
import ssl

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "gym_secret_key")

# =====================
# EMAIL FUNCTION
# =====================
def send_otp_email(to_email, otp):
    sender = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")

    if not sender or not password:
        raise Exception("Email credentials not configured")

    message = f"""Subject: OTP for Password Reset

Your OTP is: {otp}
Valid for 2 minutes.
"""

    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(sender, password)
        server.sendmail(sender, to_email, message)

# =====================
# OTP GENERATOR
# =====================
def generate_otp():
    return str(random.randint(100000, 999999))


# =====================
# HOME
# =====================
@app.route('/')
def home():
    return render_template("user/login.html")


# =====================
# REGISTER
# =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        hashed = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users(name,email,password,phone) VALUES(%s,%s,%s,%s)",
            (name, email, hashed, phone)
        )
        db.commit()

        return redirect('/')

    return render_template("user/register.html")


# =====================
# LOGIN
# =====================
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('identity')  # FIXED
    password = request.form.get('password')

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[3], password):
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        return redirect('/dashboard')

    return render_template("user/login.html", error="Invalid Login")


# =====================
# DASHBOARD
# =====================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    cursor.execute("SELECT * FROM plans")
    plans = cursor.fetchall()

    return render_template("user/dashboard.html", plans=plans)


# =====================
# BUY PLAN
# =====================
@app.route('/buy/<int:plan_id>')
def buy(plan_id):
    if 'user_id' not in session:
        return redirect('/')

    cursor.execute(
        "INSERT INTO memberships(user_id,plan_id,purchase_date) VALUES(%s,%s,%s)",
        (session['user_id'], plan_id, date.today())
    )
    db.commit()

    return redirect('/my_membership')


# =====================
# MEMBERSHIP
# =====================
@app.route('/my_membership')
def my_membership():
    if 'user_id' not in session:
        return redirect('/')

    cursor.execute("""
    SELECT m.id,p.plan_name,p.price,m.purchase_date
    FROM memberships m
    JOIN plans p ON m.plan_id=p.id
    WHERE m.user_id=%s
    """, (session['user_id'],))

    data = cursor.fetchall()
    return render_template("user/membership.html", memberships=data)


# =====================
# LOGOUT
# =====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =====================
# FORGOT PASSWORD
# =====================
@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

    if request.method == "POST":
        email = request.form.get('email')

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template("user/forgot_password.html", error="Email not found")

        otp = generate_otp()

        session['reset_email'] = email
        session['otp'] = otp
        session['otp_time'] = datetime.now()

        try:
            send_otp_email(email, otp)
        except Exception as e:
            return render_template("user/forgot_password.html", error=str(e))

        return redirect('/verify_otp')

    return render_template("user/forgot_password.html")


# =====================
# VERIFY OTP
# =====================
@app.route('/verify_otp', methods=['GET','POST'])
def verify_otp():

    if request.method == "POST":
        user_otp = request.form.get('otp')

        if 'otp_time' not in session:
            return redirect('/forgot_password')

        if datetime.now() > session['otp_time'] + timedelta(minutes=2):
            return render_template("user/verify_otp.html", error="OTP Expired")

        if user_otp == session.get('otp'):
            return redirect('/reset_password')

        return render_template("user/verify_otp.html", error="Invalid OTP")

    return render_template("user/verify_otp.html")


# =====================
# RESEND OTP (FIXED ERROR)
# =====================
@app.route('/resend_otp')
def resend_otp():

    if 'reset_email' not in session:
        return redirect('/forgot_password')

    email = session['reset_email']
    otp = generate_otp()

    session['otp'] = otp
    session['otp_time'] = datetime.now()

    send_otp_email(email, otp)

    flash("OTP resent successfully")
    return redirect('/verify_otp')


# =====================
# RESET PASSWORD
# =====================
@app.route('/reset_password', methods=['GET','POST'])
def reset_password():

    if 'reset_email' not in session:
        return redirect('/forgot_password')

    if request.method == "POST":
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            return render_template("user/reset_password.html", error="Passwords do not match")

        hashed = generate_password_hash(password)

        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (hashed, session['reset_email'])
        )
        db.commit()

        session.clear()
        return redirect('/')

    return render_template("user/reset_password.html")


# =====================
# ADMIN DASHBOARD
# =====================
@app.route('/admin/dashboard')
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM memberships")
    memberships = cursor.fetchone()[0]

    cursor.execute("""
    SELECT SUM(p.price)
    FROM memberships m
    JOIN plans p ON m.plan_id=p.id
    """)

    revenue = cursor.fetchone()[0] or 0

    return render_template(
        "admin/admin_dashboard.html",
        users=users,
        memberships=memberships,
        revenue=revenue
    )


# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(debug=True)