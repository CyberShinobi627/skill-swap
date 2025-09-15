import flask
import smtplib
import random
import os
import sys
import oracledb
from oracledb.exceptions import IntegrityError

# declaring mail and app password as contant
SENDER_MAIL = os.getenv("email", "none")
SENDER_PASS = os.getenv("apppass", "none")

if "none" in [SENDER_MAIL, SENDER_PASS]:
    print("Set email and app password in environment variables.")
    sys.exit()

app = flask.Flask(__name__, template_folder="templates", static_folder="static", static_url_path='/')

@app.route('/')
def index():
    return flask.render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return flask.render_template("register.html")
    
    else:
        """ if "otp" in flask.request.form.keys():
            if flask.request.form["otp"] == otp:
                success = "Successfully registered !!!"
                return flask.render_template("register.html", msg=success)
            
            error = "Inavalid verification code !!!"
            # flask.redirect("/register")
            return flask.render_template("register.html", msg=error) """
        
        # connecting to database
        oracledb.init_oracle_client()
        conn = oracledb.connect(user="shinobi", password="ninja")
        cur = conn.cursor()

        if "user" in flask.request.form.keys():
            full_name = flask.request.form['name']
            age = flask.request.form['age']
            class_year = flask.request.form['year']
            institution = flask.request.form['inst']
            area = flask.request.form['area']
            username = flask.request.form['user']
            password = flask.request.form['pass']
            
            # another approach without using try except
            """ fetch_query = "select username from students"
            cur.execute(fetch_query)
            rows = cur.fetchall()
            usernames = [user[0] for user in rows]
            print(usernames)

            if username in usernames:
                msg = f'username {username} already exist !!!'
                kwargs = {
                    "name": full_name,
                    "age": age,
                    "year": class_year,
                    "inst": institution,
                    "area": area,
                    "error": msg
                }
                return flask.render_template('register.html', **kwargs) """

            insert_query = "insert into students values(:1, :2, :3, :4, :5, :6, :7)"
            val = [full_name, age, class_year, institution, area, username, password]

            try:
                cur.execute(insert_query, val)
            except IntegrityError:
                error = f'username {username} already exist !!!'
                # print(error)
                info = {
                    "name": full_name,
                    "age": age,
                    "year": class_year,
                    "inst": institution,
                    "area": area,
                    "msg": error
                }
                
                return flask.render_template('register.html', **info)
        
        else:
            if flask.request.form["otp"] != otp:
                # success = "Successfully registered !!!"
                error = "Inavalid verification code !!!"
                # flask.redirect("/register")
                return flask.render_template("register.html", msg=error)

            insert_query = "insert into mentors values(:1, :2, :3, :4)"
            val = [name, qualify, mnt_area, email]
            cur.execute(insert_query, val)
        
        conn.commit()
        conn.close()

        success = "Successfully registered !!!"

        return flask.render_template('register.html', msg=success)

@app.route("/verify", methods=["POST"])
def verify():
    # print(flask.request.form.keys())
    if len(flask.request.form.keys()) > 1:
        global name, qualify, mnt_area, email, SENDER_MAIL, SENDER_PASS
        name = flask.request.form["name"]
        qualify = flask.request.form["qualify"]
        mnt_area = flask.request.form["area"]
    
    email = flask.request.form["email"]
    receiver_mail = email
    
    print(receiver_mail)
    client = smtplib.SMTP('smtp.gmail.com', 587)
    client.starttls()
    client.login(SENDER_MAIL, SENDER_PASS)
    global otp
    otp = str(random.randrange(1000, 10000))
    print(otp)
    message = f'Subject: OTP\n{otp}'
    
    client.sendmail(SENDER_MAIL, receiver_mail, message)
    client.quit()

    return flask.render_template('verify.html', resend_mail=receiver_mail)

@app.route("/login")
def login():
    return flask.render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return flask.render_template("dashboard.html")

@app.route("/about")
def about():
    return flask.render_template("about.html")

if __name__ == "__main__":
    app.run("0.0.0.0", 80, True)
