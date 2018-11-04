from flask_wtf import Form

from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError

import sqlite3
from sqlite3 import Error


class NewNoteForm(Form):

    """create a connection to the sqlite db"""
    try:
        con = sqlite3.connect("notes.db")

    except Error as e:
        print(e)
    curr = con.cursor()

    sql = "SELECT id, name FROM priority"
    curr.execute(sql)
    priorities = curr.fetchall()

    sql = "SELECT id,name FROM status"
    curr.execute(sql)
    statii = curr.fetchall()

    con.close()

    title = StringField("Title: ", [validators.InputRequired("Please enter a title.")])
    priority = SelectField("Priority", choices=priorities)
    status = SelectField("Status", choices=statii)
    submit = SubmitField("Add")
