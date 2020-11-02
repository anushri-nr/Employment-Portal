from flask import Flask,render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'jobseeker_login'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'employer_login'

@login_manager.user_loader
def load_user(user_id):
    return jssign.query.get(int(user_id))

@login_manager.user_loader
def load_user(user_id):
    return empsign.query.get(int(user_id))

class jssign(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    contact_number = db.Column(db.Integer)
    password = db.Column(db.String(50))
    city = db.Column(db.String(30))
    highest_education = db.Column(db.String(70))

class empsign(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(100), unique = True)
    contact_number = db.Column(db.Integer)
    password = db.Column(db.String(50))
    city = db.Column(db.String(30))
    company_name = db.Column(db.String(150))
    industry = db.Column(db.String(150))
    current_designation = db.Column(db.String(50))
    job_post = db.relationship('employer_job_post', backref='author', lazy =  True)

class employer_job_post(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.String(40))
    required_skills = db.Column(db.String(50))
    salary = db.Column(db.Integer)
    vacancy = db.Column(db.Integer)
    description = db.Column(db.String(250))
    employer_id = db.Column(db.Integer, db.ForeignKey('empsign.id'), nullable=False)

class applied(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name  = db.Column(db.String(20))
    contact_number = db.Column(db.Integer)
    




@app.route("/")
def index():
    return render_template("index.html")

@app.route("/jobseeker_login")
def jobseeker_login():
    return render_template("JobSeekerLogin.html")

@app.route("/jobseeker_signup")
def jobseeker_signup():
    return render_template("JobSeekerSignup.html")

@app.route("/jobseeker_signup", methods = ['POST'])
def jobseeker_post():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    password = request.form.get("password")
    city = request.form.get("city")
    education = request.form.get("education")

    jobseeker = jssign.query.filter_by(first_name=first_name, last_name=last_name, contact_number=phone).first()
    if jobseeker:
        return redirect(url_for("jobseeker_login"))

    new_jobseeker = jssign(first_name=first_name, last_name=last_name, contact_number=phone, password=generate_password_hash(password, method="sha256"), city=city, highest_education=education)
    db.session.add(new_jobseeker)
    db.session.commit()
    return redirect(url_for("jobseeker_login"))

@app.route("/joobseeker_login", methods = ['POST'])
def jobseeker_login_post():
      phone = request.form.get("phone")
      password = request.form.get("password")
      remember = True if request.form.get('remember') else False

      jobseeker = jssign.query.filter_by(contact_number=phone).first()

      if not jobseeker or not check_password_hash(jobseeker.password, password):
          return redirect(url_for("jobseeker_login"))

      login_user(jobseeker, remember=remember) 
      return redirect(url_for("jobseeker_profile"))


@app.route("/employer_login")
def employer_login():
    return render_template("EmployerLogin.html")

@app.route("/employer_signup")
def employer_signup():
    return render_template("EmployerSignup.html")

@app.route("/employer_signup", methods = ['POST'])
def employer_post():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    city = request.form.get("city")
    company_name = request.form.get("company_name")
    industry=request.form.get("industry")
    curr_des = request.form.get("curr_des")
    
    employer = empsign.query.filter_by(email=email, company_name=company_name).first()
    if employer:
        return redirect(url_for("employer_login"))

    new_employer = empsign(first_name=first_name, last_name=last_name, email=email,contact_number=phone, password=generate_password_hash(password, method="sha256"), city=city, company_name=company_name,industry=industry, current_designation=curr_des)
    db.session.add(new_employer)
    db.session.commit()
    return redirect(url_for("employer_login"))

@app.route("/employer_login", methods = ['POST'])
def employer_login_post():
      email = request.form.get("email")
      password = request.form.get("password")
      remember = True if request.form.get('remember') else False

      employer = empsign.query.filter_by(email=email).first()

      if not employer or not check_password_hash(employer.password, password):
          return redirect(url_for("employer_login"))

      login_user(employer, remember=remember) 
      return redirect(url_for("employer_profile"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/employer_profile")
@login_required
def employer_profile():
    # ppl_applied = applied.query().all()

    return render_template("employer_profile.html",first_name = current_user.first_name,last_name = current_user.last_name,company_name=current_user.company_name,designation=current_user.current_designation)

@app.route("/employer_profile", methods = ['POST'])
@login_required
def employer_profile_post():

    job = request.form.get("job")
    required_skills = request.form.get("required_skills")
    salary = request.form.get("salary")
    vacancy = request.form.get("vacancy")
    description = request.form.get("description")

    new_job = employer_job_post(job=job, required_skills=required_skills, salary=salary, vacancy=vacancy, description=description)
    db.session.add(new_job)
    db.session.commit()    

    return redirect(url_for("employer_profile"))

@app.route("/jobseeker_profile")
@login_required
def jobseeker_profile():
    return render_template("JobSeeker_Profile.html", first_name = current_user.first_name)

@app.route("/jobseeker_profile")
@login_required
def jobseeker_profile_post():
    skill = request.form.get("skill")
    city = request.form.get("city")

    jobs_offered = employer_job_post.query.filter_by(required_skills = skills)
    return render_template("JobSeeker_Profile.html", jobs_offered=jobs_offered)

@app.route("/jobseeker_profile")
@login_required
def on_apply():
    apply = applied(first_name=current_user.first_name, last_name=current_user.last_name, contact_number = current_user.contact_number)
    db.session.add(apply)
    db.session.commit()
    flash("Your application is submitted")
    return redirect(url_for('jobseeker_profile_post'))




if __name__ == "__main__":
    app.run(debug=True, port=1409)