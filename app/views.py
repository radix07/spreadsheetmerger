# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""
import os
from werkzeug import secure_filename
import xlrd

from flask import url_for, request, redirect, render_template, flash, g, session, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, lm
from forms import ExampleForm, LoginForm
from models import User

#OS environment to pick directory
UPLOAD_FOLDER = '/home/ryan/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #Max 16MB files
app.config['ALLOWED_EXTENSIONS'] = set(['xlsx','csv', 'xls'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
               filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    print "Upload function"
    # Get the name of the uploaded file
    file = request.files['file']

    sheet_name = "Sheet1"
    start_row  = 5
    start_col  = 0

    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)


        # Move the file form the temporal folder to
        # the upload folder we setup
        print os.path
        print app.config['UPLOAD_FOLDER']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file

        xls1  = xlrd.open_workbook(app.config['UPLOAD_FOLDER']+"//"+file.filename)
        for sheet in xls1.sheet_names(): #iterate through sheets of workbook
            print sheet
            sheet1 = xls1.sheet_by_name(sheet)

            MaxRows = sheet1.nrows

            MaxColumns = sheet1.ncols

            for rownum in range(start_row,MaxRows):
                print sheet1.cell_value(rownum, 1)

        #don't need to save
        #return redirect(url_for('uploaded_file', filename=filename))
        return "done" 
    else:
        print "invalid file type, handle error"

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print "Uploaded file"
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/list/')
def posts():
	return render_template('list.html')

@app.route('/new/')
@login_required
def new():
	form = ExampleForm()
	return render_template('new.html', form=form)

@app.route('/save/', methods = ['GET','POST'])
@login_required
def save():
	form = ExampleForm()
	if form.validate_on_submit():
		print "salvando os dados:"
		print form.title.data
		print form.content.data
		print form.date.data
		flash('Dados salvos!')
	return render_template('new.html', form=form)

@app.route('/view/<id>/')
def view(id):
	return render_template('view.html')

# === User login methods ===

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        login_user(g.user)

    return render_template('login.html', 
        title = 'Sign In',
        form = form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

# ====================
