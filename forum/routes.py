from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import mysql

forum = Blueprint('forum', __name__, template_folder='templates')

@forum.route('/forum', methods=['GET', 'POST'])
def forum_home():
    cursor = mysql.connection.cursor()
    # Handle patient question submission
    if request.method == 'POST' and 'loggedin' in session and session['role'] == 'patient':
        question = request.form['question']
        user_id = session['id']
        cursor.execute("INSERT INTO forum_questions (user_id, question) VALUES (%s, %s)", (user_id, question))
        mysql.connection.commit()
        flash('Question posted!', 'success')
        return redirect(url_for('forum.forum_home'))
    # Fetch all questions and answers
    cursor.execute("""
        SELECT q.id, q.question, u.name
        FROM forum_questions q
        JOIN user u ON q.user_id = u.userid
        ORDER BY q.id DESC
    """)
    questions = cursor.fetchall()
    # Fetch answers for all questions
    cursor.execute("""
        SELECT a.question_id, a.answer, u.name
        FROM forum_answers a
        JOIN user u ON a.user_id = u.userid
        ORDER BY a.id ASC
    """)
    answers = cursor.fetchall()
    # Organize answers by question_id
    answer_map = {}
    for qid, answer, name in answers:
        answer_map.setdefault(qid, []).append({'answer': answer, 'name': name})
    return render_template('forum/forum_home.html', questions=questions, answer_map=answer_map)

@forum.route('/forum/answer/<int:question_id>', methods=['POST'])
def answer_question(question_id):
    if 'loggedin' in session and session['role'] == 'doctor':
        answer = request.form['answer']
        user_id = session['id']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO forum_answers (question_id, user_id, answer) VALUES (%s, %s, %s)", (question_id, user_id, answer))
        mysql.connection.commit()
        flash('Answer posted!', 'success')
    else:
        flash('Only doctors can answer questions.', 'danger')
    return redirect(url_for('forum.forum_home'))