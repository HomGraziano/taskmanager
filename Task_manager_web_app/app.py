from os import name
from flask import Flask , redirect
import sqlite3
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String , Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.schema import ForeignKey
from flask_restful import Resource, Api
from forms import taskForm , folderForm
from flask_bootstrap import Bootstrap

conector = sqlite3.connect("test.db")

app =Flask(__name__)
app.config['SECRET_KEY'] = "\x05\r\xfdj>BT\x16i\\2|4;\x16\x0cz\xa9\xe86\xc2\xfd\xc9\xf2\x8f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'
api=Api(app)
Bootstrap(app)
db = SQLAlchemy(app)
activeFolder = 0

db.init_app(app)

class Users(db.Model):
    id = Column(Integer, primary_key=True)
    username= Column(String(12), nullable=False)
    password = Column(String(50), nullable=False)
    user_folders=relationship("Folders")

class Folders(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    children = relationship("Task", backref="folder_Task")
    user = Column(Integer , ForeignKey("users.id"))

class Task(db.Model):
    id = Column(Integer, primary_key=True)
    task = Column(String(50), nullable=False)
    folder = Column(Integer, ForeignKey("folders.id"))

"""
with app.app_context():
    db.init_app(app)
    db.create_all()
"""


"""
class add_task(Resource):


api.add_resource(add_task,"/add_task")
"""

@app.route("/", methods=["GET","POST"])
def main():
    
    folders = Folders.query.filter_by(user=1).all()
    if int(activeFolder) != 0 :
        form = taskForm()
        tasks = Task.query.filter_by(folder=int(activeFolder))
        if form.validate_on_submit():
            new_task=Task(task = form.task.data , folder=activeFolder)
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        return render_template ("folder.html" , tasks=tasks , form = form)
    form=folderForm()
    if form.validate_on_submit():
            new_folder=Folders(name = form.folder.data , user=1)
            db.session.add(new_folder)
            db.session.commit()
            return redirect("/")
    return render_template("main.html" , folders = folders , activeFolder = int(activeFolder) , form=form )

@app.route("/folder/<int:folder>" , methods=["GET", "POST"])
def folder(folder):
    global activeFolder
    activeFolder = folder
    return redirect("/")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    folder = Folders.query
    return render_template ("dashboard.html" , folders=folder)


@app.route("/delete/task/<int:task>")
def deleteTask(task):
    taskToDelete=Task.query.get_or_404(task)
    db.session.delete(taskToDelete)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__" :
    app.run(debug=True)