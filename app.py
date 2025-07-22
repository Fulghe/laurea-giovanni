from flask import Flask, render_template, request, redirect, url_for, session, send_file
from collections import defaultdict, Counter
import os
import zipfile
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersegreto_giovanni'  # Cambialo in produzione
UPLOAD_FOLDER = 'static/uploads'
AUDIO_FOLDER = 'static/audio'
DEDICHE_FILE = 'dediche.txt'
PHOTO_META_FILE = 'photo_meta.txt'
AUDIO_META_FILE = 'audio_meta.txt'
QUIZ_SCORE_FILE = 'quiz_scores.txt'

VOTI_FILE = "voti.txt"

CATEGORIE_VOTO = {
    "🥴 Il più ubriaco": "ubriaco",
    "👗 Il/La meglio vestito/a": "vestito",
    "🎉 Il re / la regina della festa": "festa",
    "📸 Il miglior fotografo": "fotografo",
    "😂 Il più simpatico": "simpatico"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route('/')
def index():
    if 'nickname' in session:
        already_done = False
        if os.path.exists(QUIZ_SCORE_FILE):
            with open(QUIZ_SCORE_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    name, _ = line.strip().split('|')
                    if name == session['nickname']:
                        already_done = True
                        break
        return render_template('index.html', nickname=session['nickname'], quiz_done=already_done)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        session['nickname'] = nickname
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('nickname', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['photo']
        if file:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + file.filename
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            with open(PHOTO_META_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{filename}|{session['nickname']}\n")
            return redirect(url_for('gallery'))
    return render_template('upload.html', nickname=session['nickname'])

@app.route('/dedica', methods=['GET', 'POST'])
def dedica():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = session['nickname']
        messaggio = request.form['messaggio']
        with open(DEDICHE_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{nome}: {messaggio}\n")
        return redirect(url_for('dedica'))
    return render_template('dediche.html', nickname=session['nickname'])


@app.route('/gallery')
def gallery():
    if 'nickname' not in session:
        return redirect(url_for('login'))

    photos = []
    if os.path.exists(PHOTO_META_FILE):
        with open(PHOTO_META_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                filename, nickname = line.strip().split('|')
                photos.append({'filename': filename, 'nickname': nickname})

    with open(DEDICHE_FILE, 'r', encoding='utf-8') as f:
        dediche = f.readlines()

    return render_template('gallery.html', photos=photos, dediche=dediche, nickname=session['nickname'])

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'nickname' not in session:
        return redirect(url_for('login'))

    questions = [
        {
            'question': "In cosa si è laureato Giovanni ?",
            'options': ['Zoologia', 'Psicologia', 'Ingegneria', 'Informatica'],
            'answer': 'Informatica'
        },
        {
            'question': "In che anno Giovanni ha iniziato l'università ?",
            'options': ['2021', '2022', '2023', '2020'],
            'answer': '2022'
        },
        {
            'question': "Qual è stato l'esame più odiato da Giovanni ?",
            'options': ['Analisi 1', 'Fisica', 'Fondamenti di diritto ed economia', 'Ingegneria del software'],
            'answer': 'Analisi 1'
        },
        {
            'question': "Con quanto si è laureato Giovanni ?",
            'options': ['110', '100', '110L', '105'],
            'answer': '110L'
        },
        {
            'question': "Che squadra tifa Giovanni ?",
            'options': ['Inter', 'Milan', 'Juve', 'Roma'],
            'answer': 'Juve'
        },
        {
            'question': "Qual è la bevanda preferita di Giovanni alla festa ?",
            'options': ['Acqua', 'Birra', 'Gin-Tonic', 'Campari'],
            'answer': 'Campari'
        },
        {
            'question': "Cosa farà Giovanni dopo la laurea ?",
            'options': ['Vacanza', 'Studiare', 'Entrare in coma ettilico', 'Dormire'],
            'answer': 'Entrare in coma ettilico'
        },
        {
            'question': "Quale livello di inglese ha Giovanni ?",
            'options': ['C1', 'C2', 'B1', 'B2'],
            'answer': 'B1'
        },
        {
            'question': "Di cosa parla la tesi di Giovanni ?",
            'options': ['Intelligenza artificiale ', 'Connected Car', 'Microcontrollori', 'Come non avere esaurimenti nervosi'],
            'answer': 'Connected Car'
        },
        {
            'question': "Perchè Giovanni ha fatto quest app ?",
            'options': ['È scemo', 'Non aveva impegni', 'È stato obbligato', 'Perchè gli piace programmare'],
            'answer': 'È scemo'
        }
    ]

    if request.method == 'POST':
        score = 0
        for i, q in enumerate(questions):
            user_answer = request.form.get(f'q{i}')
            if user_answer == q['answer']:
                score += 1

        with open(QUIZ_SCORE_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{session['nickname']}|{score}\n")

        scores = []
        if os.path.exists(QUIZ_SCORE_FILE):
            with open(QUIZ_SCORE_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    name, s = line.strip().split('|')
                    scores.append({'nickname': name, 'score': int(s)})
            scores.sort(key=lambda x: x['score'], reverse=True)

        return render_template('quiz_result.html', score=score, total=len(questions), nickname=session['nickname'], scores=scores)

    return render_template('quiz.html', questions=questions, nickname=session['nickname'])

@app.route('/classifica')
def classifica():
    if 'nickname' not in session:
        return redirect(url_for('login'))

    scores = []
    my_score = None

    if os.path.exists(QUIZ_SCORE_FILE):
        with open(QUIZ_SCORE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                name, s = line.strip().split('|')
                score_entry = {'nickname': name, 'score': int(s)}
                scores.append(score_entry)
                if name == session['nickname']:
                    my_score = int(s)
        scores.sort(key=lambda x: x['score'], reverse=True)

    return render_template('quiz_result.html', score=my_score, total=10, nickname=session['nickname'], scores=scores)

@app.route('/vota', methods=['GET', 'POST'])
def vota():
    if 'nickname' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nickname_votante = session['nickname']
        votes_to_add = []

        for categoria_label, key in CATEGORIE_VOTO.items():
            nominato = request.form.get(key, "").strip()
            if nominato:
                votes_to_add.append(f"{key}|{nominato.title()}|{nickname_votante}\n")

        with open(VOTI_FILE, "a", encoding="utf-8") as f:
            f.writelines(votes_to_add)

        return redirect(url_for('voti_classifica'))

    return render_template('vota.html', nickname=session['nickname'], categorie=CATEGORIE_VOTO)

@app.route('/voti')
def voti_classifica():
    if 'nickname' not in session:
        return redirect(url_for('login'))

    classifiche = defaultdict(Counter)

    if os.path.exists(VOTI_FILE):
        with open(VOTI_FILE, "r", encoding="utf-8") as f:
            for line in f:
                categoria, nominato, votante = line.strip().split("|")
                classifiche[categoria][nominato] += 1

    return render_template('classifica_voti.html',
                           nickname=session['nickname'],
                           categorie=CATEGORIE_VOTO,
                           classifiche=classifiche)

@app.route('/admin')
def admin():
    if 'nickname' not in session or session['nickname'] != 'giovifabat0321admin':
        return redirect(url_for('login'))

    # Elenco dei file disponibili
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    audio_dir = os.path.join(app.static_folder, 'audio')
    
    photos = os.listdir(uploads_dir) if os.path.exists(uploads_dir) else []
    audios = os.listdir(audio_dir) if os.path.exists(audio_dir) else []
    
    return render_template('admin.html', 
                           photos=photos, 
                           audios=audios,
                           has_dediche=os.path.exists("dediche.txt"),
                           has_quiz=os.path.exists("quiz_scores.txt"),
                           has_voti=os.path.exists("voti.txt"))

@app.route('/download/foto.zip')
def download_foto_zip():
    if 'nickname' not in session or session['nickname'] != 'giovifabat0321admin':
        return redirect(url_for('login'))

    zip_buffer = io.BytesIO()
    uploads_dir = os.path.join(app.static_folder, 'uploads')

    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                filepath = os.path.join(uploads_dir, filename)
                zipf.write(filepath, arcname=filename)

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip',
                     download_name='foto_laurea_giovanni.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5001)
