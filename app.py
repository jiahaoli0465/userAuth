"""Example flask app that stores passwords hashed with Bcrypt. Yay!"""

from flask import Flask, render_template, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
with app.app_context():
    db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """Show homepage with links to site areas."""
    if not session.get('username'):
        flash(message = 'please login first', category='alert')
        return redirect('/login')
    u = session["username"]


    return render_template("index.html", user = u)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username = username, pwd = password, first_name = first_name, last_name = last_name, email = email)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username

        return redirect('/ ')

    else:
        return render_template("register.html", form=form)
    
@app.route("/login", methods = ['GET', 'POST'])
def login():
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = username  # keep logged in
            return redirect("/")

        else:
            form.username.errors = ["Invalid input"]
            return render_template("login.html", form=form)


    else:
        return render_template("login.html", form=form)
    
@app.route('/users/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404(description="User not found")
    return render_template('profile.html', user = user)

@app.route("/logout")
def logout():
    session.pop("username")
    flash('Logged out successfully!', category='success')
    return redirect('/login')

@app.route('/users/<string:username>/delete', methods=['POST'])
def delete_user(username):
    # Check if the user is logged in and authorized to delete
    if not session.get('username'):
        return jsonify({"message": "Unauthorized access."}), 401

    user = User.query.filter_by(username=username).first_or_404(description="User not found")

    if session['username'] == user.username:
        db.session.delete(user)
        db.session.commit()
        # Redirect or return a success response
        return jsonify({"message": "User deleted successfully."}), 200
    else:
        # Unauthorized if the logged-in user doesn't match the user to be deleted
        return jsonify({"message": "Unauthorized action."}), 401
    
@app.route("/flashdelete")
def flash_delete():
    flash('Account deleted...', category='success')
    return redirect('/login')
