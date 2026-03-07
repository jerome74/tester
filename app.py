import random
from flask import Flask, render_template, request, session, redirect, url_for

from questions import questions

app = Flask(__name__)
app.secret_key = 'aip-c01-quiz-secret-key-2026'

QUIZ_SIZE = 75


@app.route('/')
def index():
    return render_template('index.html', total=len(questions), quiz_size=QUIZ_SIZE)


@app.route('/start', methods=['POST'])
def start():
    sampled = random.sample(range(len(questions)), QUIZ_SIZE)
    session['question_indices'] = sampled
    session['current'] = 0
    session['answers'] = {}
    return redirect(url_for('quiz'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'question_indices' not in session:
        return redirect(url_for('index'))

    indices = session['question_indices']
    current = session.get('current', 0)

    if current >= QUIZ_SIZE:
        return redirect(url_for('result'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'next':
            session['current'] = current + 1
            return redirect(url_for('quiz'))

    q_index = indices[current]
    q = questions[q_index]
    answers = session.get('answers', {})
    user_answer = answers.get(str(current))

    return render_template(
        'quiz.html',
        question=q,
        q_num=current + 1,
        total=QUIZ_SIZE,
        user_answer=user_answer,
        verified=False
    )


@app.route('/verify', methods=['POST'])
def verify():
    if 'question_indices' not in session:
        return redirect(url_for('index'))

    current = session.get('current', 0)
    indices = session['question_indices']
    q_index = indices[current]
    q = questions[q_index]

    if q.get('multi'):
        selected = request.form.getlist('answer')
        user_answer = ','.join(sorted(selected))
        correct_set = set(q.get('answers', []))
        is_correct = set(selected) == correct_set and bool(correct_set)
    else:
        user_answer = request.form.get('answer', '')
        is_correct = user_answer.strip() == (q.get('answer') or '').strip()

    answers = session.get('answers', {})
    answers[str(current)] = user_answer
    session['answers'] = answers

    return render_template(
        'quiz.html',
        question=q,
        q_num=current + 1,
        total=QUIZ_SIZE,
        user_answer=user_answer,
        is_correct=is_correct,
        verified=True
    )


@app.route('/result')
def result():
    if 'question_indices' not in session:
        return redirect(url_for('index'))

    indices = session['question_indices']
    answers = session.get('answers', {})
    correct = 0
    details = []

    for i, q_index in enumerate(indices):
        q = questions[q_index]
        user_answer = answers.get(str(i), '')
        # Normalize: compare letter(s) only
        correct_letters = set(a.strip() for a in q['answer'].split(',')) if q['answer'] else set()
        user_letters = set(a.strip() for a in user_answer.split(',')) if user_answer else set()
        is_correct = correct_letters == user_letters and bool(correct_letters)
        if is_correct:
            correct += 1
        details.append({
            'num': i + 1,
            'question': q['question'],
            'options': q['options'],
            'correct_answer': q['answer'],
            'user_answer': user_answer,
            'is_correct': is_correct
        })

    total = QUIZ_SIZE
    percentage = round(correct / total * 100, 1)
    passed = percentage >= 72  # AWS passing score ~72%

    return render_template(
        'result.html',
        correct=correct,
        total=total,
        percentage=percentage,
        passed=passed,
        details=details
    )


@app.route('/end', methods=['POST'])
def end():
    if 'question_indices' not in session:
        return redirect(url_for('index'))
    return redirect(url_for('result'))


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
