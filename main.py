from flask import Flask, render_template, redirect, request
import sqlite3
from sqlite3 import Error
import secrets
from forms import NewNoteForm

import datetime
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(4)


def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)

    return None


def create_table(con, query):
    """Create a table in the database.

    Note:
        Could be used for other sql

    Args:
        con (Connection): the connection to the database
        query (str): the query to create the new table
    """
    try:
        c = con.cursor()
        c.execute(query)
    except Error as e:
        print(e)


def create_category(con, category):
    sql = """INSERT INTO category(name) VALUES(?);"""
    cur = con.cursor()
    cur.execute(sql, (category,))
    return cur.lastrowid


def create_priority(con, priority):
    sql = """INSERT INTO priority(name) VALUES(?);"""
    cur = con.cursor()
    cur.execute(sql, (priority,))
    return cur.lastrowid


def create_status(con, status):
    sql = """INSERT INTO status(name) VALUES(?);"""
    cur = con.cursor()
    cur.execute(sql, (status,))
    return cur.lastrowid


def create_note(con, note):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    sql = """INSERT INTO note(title, priority_id, status_id, category_id, add_date) VALUES(?,?,?,?,?);"""
    cur = con.cursor()
    cur.execute(sql, note)
    return cur.lastrowid


def select_all_notes():
    con = create_connection('notes.db')
    get_all_notes = """SELECT note.id, note.title, priority.name, status.name, category.name, note.add_date
                FROM note
                INNER JOIN priority ON note.priority_id=priority.id
                INNER JOIN status ON note.status_id=status.id
                INNER JOIN category on note.category_id = category.id
                ORDER BY category_id ASC, status_id ASC, priority_id ASC, add_date ASC;
            """
    get_categories = "SELECT name FROM category"

    cur = con.cursor()

    cur.execute(get_all_notes)
    all_notes = cur.fetchall()

    cur.execute(get_categories)
    categories = cur.fetchall()

    temp_categories = []
    processed = []

    for category in categories:
        temp_categories.append(category[0])
        processed.append([])

    categories = temp_categories
    for note in all_notes:
        index = categories.index(note[4])
        processed[index].append(note)
    con.close()
    return processed, categories


def select_note_by_priority(con, priority):
    sql = "SELECT * FROM note WHERE priority=?"
    cur = con.cursor()
    cur.execute(sql, (priority,))
    rows = cur.fetchall()
    print(rows)
    print("$$$")
    for row in rows:
        print(row)


def demote_note(note_id):
    con = create_connection('notes.db')
    sql = "UPDATE note SET category_id = category_id - 1 WHERE id = ?"
    curr = con.cursor()
    curr.execute(sql, (note_id,))
    con.commit()
    con.close()


def promote_note(note_id):
    con = create_connection('notes.db')
    sql = "UPDATE note SET category_id = category_id + 1 WHERE id = ?"
    curr = con.cursor()
    curr.execute(sql, (note_id,))
    con.commit()
    con.close()


def make_parked(note_id):
    """Change the status of the given note to 'Parked'.

        Args:
            note_id (int): the id of the note to change the status of
        """
    con = create_connection('notes.db')
    sql = "UPDATE note SET status_id = 2 WHERE id = ?"
    curr = con.cursor()
    curr.execute(sql, (note_id,))
    con.commit()
    con.close()


def make_active(note_id):
    """Change the status of the given note to 'Active'.

    Args:
        note_id (int): the id of the note to change the status of
    """
    con = create_connection('notes.db')
    sql = "UPDATE note SET status_id = 1 WHERE id = ?"
    curr = con.cursor()
    curr.execute(sql, (note_id,))
    con.commit()
    con.close()


def increase_priority(note_id):
    """Increases the priority of a note. Won't increase above the maximum priority value.

    Args:
        note_id (int): the id of the note to change the priority of
    """
    con = create_connection('notes.db')
    curr = con.cursor()

    sql = "SELECT priority_id FROM note WHERE id = ?"
    curr.execute(sql, (note_id,))
    rows = curr.fetchall()
    priority = int(rows[0][0])

    sql = "SELECT max(id) FROM priority"
    curr.execute(sql)
    rows = curr.fetchall()
    max_priority = rows[0][0]
    if priority < max_priority:
        sql = "UPDATE note SET priority_id = priority_id + 1 WHERE id = ?"
        curr.execute(sql, (note_id,))
        con.commit()
    con.close()


def decrease_priority(note_id):
    """Decreases the priority of a note. Won't decrease below the minimum priority value.

    Args:
        note_id (int): the id of the note to change the priority of
    """
    con = create_connection('notes.db')
    curr = con.cursor()

    sql = "SELECT priority_id FROM note WHERE id = ?"
    curr.execute(sql, (note_id,))
    rows = curr.fetchall()
    priority = int(rows[0][0])

    sql = "SELECT min(id) FROM priority"
    curr.execute(sql)
    rows = curr.fetchall()
    min_priority = rows[0][0]
    if priority > min_priority:
        sql = "UPDATE note SET priority_id = priority_id - 1 WHERE id = ?"
        curr.execute(sql, (note_id,))
        con.commit()
    con.close()


def delete_note(note_id):
    con = create_connection('notes.db')
    sql = "DELETE FROM note WHERE id=?"
    curr = con.cursor()
    curr.execute(sql, (note_id,))
    con.commit()
    con.close()


def delete_all_notes():
    con = create_connection('notes.db')
    sql = "DELETE FROM note"
    curr = con.cursor()
    curr.execute(sql)
    con.close()


def get_priorities():
    con = create_connection('notes.db')
    sql = "SELECT id, name FROM priority"
    curr = con.cursor()
    curr.execute(sql)
    rows = curr.fetchall()
    con.close()
    return rows


def get_statii():
    con = create_connection('notes.db')
    sql = "SELECT id,name FROM status"
    curr = con.cursor()
    curr.execute(sql)
    rows = curr.fetchall()
    con.close()
    return rows


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/notes')
def notes():
    all_notes, categories = select_all_notes()
    return render_template("notes.html", notes=all_notes, categories=categories)


@app.route('/notes/create')
def add_note():
    form = NewNoteForm()
    return render_template("createnote.html", form=form, priorities=get_priorities(), statii=get_statii())


@app.route('/do_create_note', methods=['POST'])
def do_add_note():
    title = request.form['title']
    status = request.form['status']
    priority = request.form['priority']
    print(title, status, priority)


    return redirect('/notes')


@app.route('/notes/delete/<note_id>')
def delete_note_route(note_id):
    print("delete note {}".format(note_id))
    delete_note(note_id)
    return redirect('/notes')


@app.route('/notes/demote/<note_id>')
def demote_note_route(note_id):
    print("demote note {}".format(note_id))
    demote_note(note_id)
    return redirect('/notes')


@app.route('/notes/promote/<note_id>')
def promote_note_route(note_id):
    print("promote note {}".format(note_id))
    promote_note(note_id)
    return redirect('/notes')


@app.route('/notes/make_parked/<note_id>')
def make_parked_route(note_id):
    make_parked(note_id)
    return redirect('/notes')


@app.route('/notes/make_active/<note_id>')
def make_active_route(note_id):
    make_active(note_id)
    return redirect('/notes')


@app.route('/notes/increase_priority/<note_id>')
def increase_priority_route(note_id):
    increase_priority(note_id)
    return redirect('/notes')


@app.route('/notes/decrease_priority/<note_id>')
def decrease_priority_route(note_id):
    decrease_priority(note_id)
    return redirect('/notes')


def initialise_database(con):
    sql_create_category_table = """ CREATE TABLE IF NOT EXISTS category (
                                           id integer PRIMARY KEY,
                                           name text NOT NULL
                                       ); """

    sql_create_priority_table = """ CREATE TABLE IF NOT EXISTS priority (
                                               id integer PRIMARY KEY,
                                               name text NOT NULL
                                           ); """

    sql_create_status_table = """ CREATE TABLE IF NOT EXISTS status (
                                               id integer PRIMARY KEY,
                                               name text NOT NULL
                                           ); """

    sql_create_note_table = """CREATE TABLE IF NOT EXISTS note (
                                   id integer PRIMARY KEY,
                                   name text NOT NULL,
                                   priority_id integer NOT NULL,
                                   status_id integer NOT NULL,
                                   category_id integer NOT NULL,
                                   add_date text NOT NULL,
                                   FOREIGN KEY (category_id) REFERENCES category (id),
                                   FOREIGN KEY (priority_id) REFERENCES priority (id),
                                   FOREIGN KEY (status_id) REFERENCES status (id)
                                   );"""

    if con is not None:
        create_table(con, sql_create_category_table)
        create_table(con, sql_create_priority_table)
        create_table(con, sql_create_status_table)
        create_table(con, sql_create_note_table)
    else:
        print("Error: no DB connection")


def main():
    # con = create_connection("notes.db")
    # initialise_database(con)
    # with con:
    #     # print("1. Query task by priority:")
    #     # select_task_by_priority(con, 1)
    #     #
    #     # print("2. Query all tasks")
    #     # select_all_tasks(con)
    #     # create a new project
    #
    #     create_status(con, "Active")
    #     create_status(con, "Parked")
    #
    #     create_priority(con, "Low")
    #     create_priority(con, "Normal")
    #     create_priority(con, "High")
    #
    # today = datetime.datetime.today().strftime('%Y-%m-%d')
    #     project_id = create_category(con, "To Do")
    #     project_id = 1
    #     print("ID for project {}: {}".format("To Do",project_id))
    #     # tasks
    #     note_1 = ('Add ability to change status for a note', 2, 1, project_id, today)
    #     note_2 = ('Add ability to change category for a note', 2, 1, project_id, today)
    #
    #     # create tasks
    #     create_note(con, note_1)
    #     create_note(con, note_2)
    #
    #     project_id = create_category(con, "Doing")
    #     project_id = 2
    #     # tasks
    #     note_1 = ('Add ability to add notes', 2, 1, project_id, today)
    #     note_2 = ('Add ability to change category for a note', 2, 1, project_id, today)
    #
    #     # create tasks
    #     create_note(con, note_1)
    #     create_note(con, note_2)
    #
    #     project_id = create_category(con, "Done")
    #     project_id=3
    #     # tasks
    #     note_1 = ('Create/define Sqlite database', 2, 1, project_id, today)
    #     note_2 = ('Define initial routes', 2, 1, project_id, today)
    #
    #     # create tasks
    #     create_note(con, note_1)
    #     create_note(con, note_2)

    app.run(debug=True)


if __name__ == "__main__":
    main()
