from flask import Flask, render_template, request, redirect, url_for
from models import db, Meta, Sents, Words, Bigrams, Trigrams
import os
import spacy
from sqlalchemy import func

nlp = spacy.load("ru_core_news_sm")

current_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_dir, 'anecdote.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

def lemmatization(word):
    for token in nlp(word):
        return(token.lemma_)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        lemma1 = request.form.get('lemma1')
        word1 = request.form.get('word1')
        pos1 = request.form.get('pos1')
        
        lemma2 = request.form.get('lemma2')
        word2 = request.form.get('word2')
        pos2 = request.form.get('pos2')

        lemma3 = request.form.get('lemma3')
        word3 = request.form.get('word3')
        pos3 = request.form.get('pos3')
        
        return redirect(url_for('results', 
                                lemma1=lemma1, word1=word1, pos1=pos1,
                                lemma2=lemma2, word2=word2, pos2=pos2,
                                lemma3=lemma3, word3=word3, pos3=pos3))
    
    return render_template('search.html')


@app.route('/results', methods=['GET', 'POST'])
def results():

    search = ""
    
    lemma1 = request.args.get('lemma1')
    word1 = request.args.get('word1')
    pos1 = request.args.get('pos1')

    lemma2 = request.args.get('lemma2')
    word2 = request.args.get('word2')
    pos2 = request.args.get('pos2')

    lemma3 = request.args.get('lemma3')
    word3 = request.args.get('word3')
    pos3 = request.args.get('pos3')


    if lemma3 or word3 or pos3:
        query = db.session.query(Trigrams)\
            .join(Meta, Meta.text_id == Trigrams.text_id)\
            .join(Sents, (Sents.sent_id == Trigrams.sent_id) & (Sents.text_id == Trigrams.text_id))
        
        if lemma1:
            query = query.filter(Trigrams.lemma1 == lemmatization(lemma1))
            search += lemma1

        if word1:
            query = query.filter(func.lower(Trigrams.word1) == word1.lower())
            if not lemma1:
                search += word1
            else:
                search += ', '
                search += word1
        if pos1:
            query = query.filter(Trigrams.pos1 == pos1)

            if not lemma1 and not word1:
                search += pos1
            else:
                search += ', '
                search += pos1
        
        search += ' + '
        if lemma2:
            query = query.filter(Trigrams.lemma2 == lemmatization(lemma2))
            search += lemma2
        if word2:
            query = query.filter(func.lower(Trigrams.word2) == word2.lower())
            if not lemma2:
                search += word2
            else:
                search += ', '
                search += word2
        if pos2:
            query = query.filter(Trigrams.pos2 == pos2)
            if not lemma2 and not word2:
                search += pos2
            else:
                search += ', '
                search += pos2
        
        search += ' + '
        if lemma3:
            query = query.filter(Trigrams.lemma3 == lemmatization(lemma3))
            search += lemma3
        if word3:
            query = query.filter(func.lower(Trigrams.word3) == word3.lower())
            if not lemma3:
                search += word3
            else:
                search += ', '
                search += word3
        if pos3:
            query = query.filter(Trigrams.pos3 == pos3)
            if not lemma3 and not word3:
                search += pos3
            else:
                search += ', '
                search += pos3
    
    elif lemma2 or word2 or pos2:
        query = db.session.query(Bigrams)\
            .join(Meta, Meta.text_id == Bigrams.text_id)\
            .join(Sents, (Sents.sent_id == Bigrams.sent_id) & (Sents.text_id == Bigrams.text_id))

        if lemma1:
            query = query.filter(Bigrams.lemma1 == lemmatization(lemma1))
            search += lemma1
        if word1:
            query = query.filter(func.lower(Bigrams.word1) == word1.lower())
            if not lemma1:
                search += word1
            else:
                search += ', '
                search += word1
        if pos1:
            query = query.filter(Bigrams.pos1 == pos1)
            if not lemma1 and not word1:
                search += pos1
            else:
                search += ', '
                search += pos1

        search += ' + '
        if lemma2:
            query = query.filter(Bigrams.lemma2 == lemmatization(lemma2))
            search += lemma2
        if word2:
            query = query.filter(func.lower(Bigrams.word2) == word2.lower())
            if not lemma2:
                search += word2
            else:
                search += ', '
                search += word2
        if pos2:
            query = query.filter(Bigrams.pos2 == pos2)
            if not lemma2 and not word2:
                search += pos2
            else:
                search += ', '
                search += pos2

    else:
        query = db.session.query(Words)\
        .join(Meta, Meta.text_id == Words.text_id)\
        .join(Sents, (Sents.sent_id == Words.sent_id) & (Sents.text_id == Words.text_id))

        if lemma1:
            query = query.filter(Words.lemma == lemmatization(lemma1))
            search += lemma1
        if word1:
            query = query.filter(func.lower(Words.word) == word1.lower())
            if not lemma1:
                search += word1
            else:
                search += ', '
                search += word1
        if pos1:
            query = query.filter(Words.pos == pos1)
            if not lemma1 and not word1:
                search += pos1
            else:
                search += ', '
                search += pos1

    query = query.with_entities(Meta.source, Sents.sent)
    results = query.all()

    return render_template("results.html", results=results, search=search)

if __name__ == '__main__':
    app.run(debug=True)
