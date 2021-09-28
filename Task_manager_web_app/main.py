from flask import Flask, request,  render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from flask_marshmallow import Marshmallow
from sqlalchemy.sql.sqltypes import Boolean

#Mostly Flask and SQLite configurations.

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasksql'
db = SQLAlchemy(app)
ma = Marshmallow(app)
id = 0
selectedFolder = 0

#Users class, for the login system to work.

class Users(db.Model):
    id = Column(Integer, primary_key = True)
    username = Column(String(18), nullable = False)
    password = Column(String(50), nullable = False)
    # user_folders = relationship("Folders")

    def __init__(self, username, password):
        self.username = username
        self.password = password

#Folders, these serve as a reference to the frontend app to know where to search for the tasks.

class Folders(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    task_folder = relationship('Tasks', backref='folderid', lazy='dynamic')
    
    def __init__(self, name):
        self.name = name

#Tasks class, every instance of the object Tasks is linked to a folder.

class Tasks(db.Model):
    id = Column(Integer, primary_key = True)
    task = Column(String(50), nullable = False)
    is_completed = Column(Boolean, nullable = False)
    folder = Column(Integer, db.ForeignKey('folders.id'))

    def __init__(self, task, is_completed, selectedFolder):
        self.task = task
        self.is_completed = is_completed
        self.folder = selectedFolder

#The schemas for the server to return info

db.create_all()
class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "task", "is_completed","folder")

class FolderSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")

folder_schema = FolderSchema()
task_schema = TaskSchema()
tasks_schema = TaskSchema(many = True)
folders_schema = FolderSchema(many = True)


#This function creates the folders, by introducing just the folder's name (Commented because it is not finished).

@app.route('/folder', methods = ['POST'])
def create_folder():
    name = request.form.get('name')
    new_folder = Folders(name)
    db.session.add(new_folder)
    db.session.commit()

    return redirect(url_for('page'))

#This function creates the tasks, requiring the user to introduce just the task name (id, completition is False by default and folder is given automatically)

@app.route('/add', methods = ['POST'])
def create_task():
    task = request.form.get('task')
    is_completed = False
    new_task = Tasks(task,is_completed,selectedFolder)
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('page'))

#Here i ask the server for the tasks, it returns and shows the tasks of the selected folder.

@app.route('/', methods = ['GET'])
def get_tasks():

    all_folders = Folders.query.all()
    folders = folders_schema.dump(all_folders)
    selectedtasks = Tasks.query.filter_by(folder=selectedFolder)
    result = tasks_schema.dump(selectedtasks)
    #result = tasks_schema.dump(all_tasks)
    return render_template('main.html', folders = folders, result = result, selectedFolder = selectedFolder)

#This function tells the frontend app the selected folder.

@app.route('/updatefolder/<id>', methods = ['GET'])
def updateFolder(id):
    global selectedFolder
    global result
    selectedFolder = id
    return redirect(url_for('page'))

#This changes the status of the tasks from completed to non completed and vice versa.

@app.route('/tasks/<id>')
def update(id):
    task = Tasks.query.filter_by(id=id).first()
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('page'))

#This function is used to delete the tasks, whether theyre completed or not.

@app.route('/delete/<id>')
def delete(id):
    task = Tasks.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('page'))

#This deletes the entire selected folder, and all the tasks that belong to that folder.

@app.route('/deletefolder/<id>')
def deletefolder(id):
    global selectedFolder
    foldertodelete = Folders.query.filter_by(id=id).first()
    all_tasks = Tasks.query.all()
    for f in all_tasks:
        if f.folder == foldertodelete.id:
            db.session.delete(f)
    db.session.delete(foldertodelete)
    db.session.commit()
    selectedFolder = 0
    return redirect(url_for('page'))

#Default function to show the page.

@app.route('/')
def page():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(app.run(host="0.0.0.0"))






