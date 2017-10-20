import ast, os, time, copy
from datetime import datetime
from flask import Flask, request, flash
from functions import get

#from models import Survey, Course, UniUser, Admin, Staff, Student, Guest
from models import surveys_model, courses_model


from flask_login import login_user, login_required, current_user, logout_user
from abc import ABCMeta, abstractmethod
from classes import course_usage, common


class CreateSurvey:
    'creates a new survey'
    def create_attempt(self):
        courseId = request.form["svycourse"]
        surveyName = request.form["svyname"]
        startDate = request.form["startdate"]
        endDate = request.form["enddate"]

        if CreateSurvey.err_check(courseId,surveyName,startDate,endDate):
            startDate = datetime.strptime(startDate, '%Y/%m/%d')
            endDate = datetime.strptime(endDate, '%Y/%m/%d')
            return current_user.CreateSurvey(courseId,surveyName,startDate,endDate)

        return common.Render.surveys()


    def err_check(courseId='',surveyName='',startDate='',endDate=''):
        'checks a new surveys form fields'
        if surveyName == '':
            flash('Please Enter a Valid Survey Name')
            return False

        if (get.cleanString(str(surveyName)) == False):
            errorMSG("routes.newsurvey", "Invalid Characters in survey name")
            return False

        try:
            startDate = datetime.strptime(startDate, '%Y/%m/%d')
            endDate = datetime.strptime(endDate, '%Y/%m/%d')
        except ValueError:
            flash('Please Enter a Start and Finish Date')
            return False
        
        course = courses_model.Course.query.filter_by(id=courseId).first()    
        if(course == None):
            errorMSG("routes.newsurvey", "course object is empty")
            return False

        if LoadSurvey.load(request.form.getlist('surveyid')):
            errorMSG("routes.newsurvey", "survey already exists!")
            return False

        return True


class OpenSurvey:
    'opens a specific survey to required page'
    def open_attempt(self):

        survey = LoadSurvey.load(request.form.getlist('surveyid'))
        if survey:
            course = course_usage.LoadCourse.load(survey.course_id)  
            if course:
                if survey.status < 2:
                    return current_user.ModifySurvey(survey, course)
                if survey.status == 2:
                    return current_user.AnswerSurvey(survey, course)
                if survey.status == 3:
                    if current_user.role == 'Student' or current_user.role == 'Guest':
                        return current_user.ViewSurveyResults(survey, course)
                    else:
                        #staff and admin go to an overview page still
                        return current_user.ModifySurvey(survey, course)
        else:
            flash("Please Select a Survey to Open")
        return common.Render.surveys()



class LoadSurvey:
    'loads a specific survey'
    def load(surveyID=[]):
        if surveyID:
            survey = surveys_model.Survey.query.filter_by(id=surveyID[0]).first()    
            return survey
        return None



class StatusSurvey:
    'updates the status of the survey'
    def update_attempt(self):
        surveyID = request.form.getlist("surveyid")
        survey = LoadSurvey.load(request.form.getlist('surveyid'))
        course = course_usage.LoadCourse.load(survey.course_id)  
        
        if survey and course: 
            if survey.status == 0:
                return current_user.PushSurvey(survey,course)
            if survey.status == 1:    
                return current_user.PublishSurvey(survey,course)
            if survey.status == 2:
                return current_user.EndSurvey(survey,course)
            if survey.status == 3:
                return current_user.ViewSurveyResults(survey,course) 

        return OpenSurvey().open_attempt() 



class AddQuestionSurvey:
    'adds questions to surveys'
    def add_attempt(self):

        survey_questions = request.form.getlist('question')
        surveyID = request.form.getlist("surveyid")
        survey = LoadSurvey.load(request.form.getlist('surveyid'))
        course = course_usage.LoadCourse.load(survey.course_id)  

        if survey_questions:
            if survey:
                survey_questions = ast.literal_eval(str(survey_questions)[1:-1])
                print(survey_questions)
                return current_user.AddQuestionSurvey(survey_questions,survey,course)
        else:
            flash('No questions selected')
        return OpenSurvey().open_attempt() 



class RemoveQuestionSurvey:
    'removes a question from a survey'
    def remove_attempt(self):
        survey_question = request.form.getlist('question')
        surveyID = request.form.getlist("surveyid")
        survey = LoadSurvey.load(request.form.getlist('surveyid'))
        course = course_usage.LoadCourse.load(survey.course_id)  
        if survey_question:
            survey_question = request.form['question']
            if survey:
                survey_question = ast.literal_eval(survey_question)
                return current_user.RemoveQuestionSurvey(survey_question,survey,course)
        else:
            flash('No questions selected')
        return OpenSurvey().open_attempt()         