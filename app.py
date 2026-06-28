from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    blood_type = db.Column(db.String(10))

    number = db.Column(db.String(15))

    dob = db.Column(db.String(20))

    email = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(200), nullable=False)

    is_donor = db.Column(db.Boolean, default=False)

    loc = db.Column(db.String(300), nullable=False)


# CREATE DATABASE

with app.app_context():
    db.create_all()


# REGISTER PAGE

@app.route('/', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['username']
        number = request.form['number']
        blood = request.form['bload']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        loc = request.form['loc']

        # CHECK EXISTING EMAIL

        check_user = User.query.filter_by(email=email).first()

        if check_user:

            flash("Email already exists!")

            return redirect(url_for('register'))

        # HASH PASSWORD

        hashed_password = generate_password_hash(password)

        # NEW USER

        new_user = User(
            name=name,
            blood_type=blood,
            number=number,
            dob=dob,
            email=email,
            password=hashed_password,
            loc=loc.upper()
        )

        db.session.add(new_user)

        db.session.commit()

        flash("Registration Successful!")

        return redirect(url_for('login'))

    return render_template("register.html")



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            donors = User.query.filter_by(is_donor=True).all()

            return render_template(
                "home.html",
                user=user,
                donors=donors
            )

        else:

            flash("Invalid Email or Password!")

            return redirect(url_for('login'))

    return render_template("login.html")



@app.route('/process', methods=['POST'])
def process():

    data = request.get_json()

    email = data.get("email")

    user = User.query.filter_by(email=email).first()

    if user:

        user.is_donor = True

        db.session.commit()

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False
    })

@app.route("/filter", methods=["POST"])
def filter():
    print("Filter endpoint called")
    data = request.get_json() or {}
    loc = data.get('loc')
    bt = data.get('bt')
    query = User.query.filter_by(is_donor=True)
    if loc and bt:
        query = User.query.filter_by(is_donor=True, loc=loc, blood_type=bt)
    elif loc:
        query = User.query.filter_by(is_donor=True, loc=loc)
    elif bt:
        query = User.query.filter_by(is_donor=True, blood_type=bt)
    else:
        print("No filters applied, returning all donors")

    filtered_donors = query.all()
    donors_json = [
        {
            "name": donor.name,
            "blood_type": donor.blood_type,
            "number": donor.number,
            "loc": donor.loc
        }
        for donor in filtered_donors
    ]

    return jsonify({"donors": donors_json})
    

if __name__ == '__main__':
    app.run(debug=True)

