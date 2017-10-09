import ast, os, time, copy
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for, flash
from server import app, errorMSG
from defines import debug
from functions import get
from models import GeneralQuestion, MCQuestion, SurveyResponse,\
					GeneralResponse, MCResponse
from models import Survey, Course, UniUser
from database import db_session, Base
from flask_login import login_user, login_required, current_user, logout_user
from util import SurveyUtil, QuestionUtil

@app.route("/")
def index():
	if (current_user.is_authenticated):
		return render_template("home.html", user=current_user)
	else:
		return redirect(url_for("login"))

@app.route("/home")
def home():
	if (current_user.is_authenticated):
		return render_template("home.html", user=current_user)
	else:
		return redirect(url_for("login"))


@app.route("/submitted")
def submit(): 
	if (current_user.is_authenticated):
		return render_template("completed.html")


#######################################################################
########################## 		LOGIN 	 ##############################
#######################################################################


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		id = request.form['username']
		password = request.form['password']
		user = UniUser.query.get(id)

		if user==None:
			print("nouser")
			return render_template("login.html", invalid=True)

		if password == user.password:
			login_user(user)
			flash('Logged in successfully.')
			next = request.args.get('next')
			return redirect(next or url_for('home'))
		else:
			print("incorrect password")
			return render_template("login.html", invalid=True)

	return render_template("login.html", invalid=False)


@app.route("/logintest")
@login_required
def test():
	# All user attributes can be accessed using the current_user variable
	# which returns None if no logged in user
	print(current_user.is_authenticated)
	print(current_user.password)
	print(current_user.id)
	print(current_user.courses)

	return redirect(url_for("login"))

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("login")

#######################################################################
########################## 	SURVEYS 	###############################
#######################################################################

@app.route("/surveys", methods=["GET", "POST"])
@login_required
def surveys():
	util = SurveyUtil()
	if (current_user.is_authenticated)==False:
		return redirect(url_for("login"))

	if request.method == "GET":
		return util.surveyinfo()
	else:

		#check if an admin and if so, they are permitted to make new surveys!
		surveyform = request.form["surveyformid"]
		if surveyform=='2':
			return util.opensurvey()		

		if(current_user.role == 'admin' or current_user.role == 'staff'):
			if(current_user.role=='admin'):
				if surveyform=='1':
					return util.newsurvey()
				if surveyform=='3':
					return util.removeqsurvey()
				if surveyform=='4':
					return util.addqsurvey()
				if surveyform=='5':
					return util.statussurvey()

			if request.form.getlist("surveyid")==[]:
				errorMSG("routes.surveys","survey doesnt exist")
				return util.surveyinfo()	

			surveyID = request.form["surveyid"]
			survey = Survey.query.filter_by(id=surveyID).first()	
			if(survey==None):
				errorMSG("routes.surveys","survey object is empty")
				return util.surveyinfo()	


			#enrolled staff have access to modify surveys
			if current_user in survey.users and survey.status==1:
				if surveyform=='3':
					return util.removeqsurvey()
				if surveyform=='4':
					return util.addqsurvey()
				if surveyform=='5':
					return util.statussurvey()
		else:
		#students can only answer the survey
			if surveyform=='6':
				return util.answersurvey()

		return util.surveyinfo()


#######################################################################
########################## 	 QUESTIONS 	###############################
#######################################################################

@app.route('/questions', methods=["GET", "POST"])
@login_required
def questions():
	util = QuestionUtil()
	if (current_user.is_authenticated)==False:
		return redirect(url_for("login"))

	if(current_user.role != 'admin'):
		errorMSG("routes.questions","unauthorised user attempted access:",current_user.id)
		return render_template("home.html", user=current_user)

	if request.method == "GET":
		return util.questioninfo()

	questionform = request.form["questionformid"]
	if questionform=='1':
		return util.openquestion()
	if questionform=='2':
		return util.addquestion()
	if questionform=='3':
		return util.removequestion()
	if questionform=='4':
		return util.modifyquestion()

	return util.questioninfo()


























































