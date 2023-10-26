from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Meta(db.Model):
    __tablename__ = "meta"

    text_id = db.Column('text_id', db.Integer, primary_key=True)
    source = db.Column('source', db.Text)
    text = db.Column('full_text', db.Text)

    # connections
    texts_to_sents = db.relationship("Sents",  uselist=False, primaryjoin="Meta.text_id==Sents.text_id")
    texts_to_words = db.relationship("Words",  uselist=False, primaryjoin="Meta.text_id==Words.text_id")
    texts_to_bi = db.relationship("Bigrams",  uselist=False, primaryjoin="Meta.text_id==Bigrams.text_id")
    texts_to_tri = db.relationship("Trigrams",  uselist=False, primaryjoin="Meta.text_id==Trigrams.text_id")

class Sents(db.Model):
    __tablename__ = "sentences"

    text_id = db.Column(db.Integer, ForeignKey('meta.text_id'))
    sent_id = db.Column('sent_id', db.Integer, primary_key=True)
    sent = db.Column('sent', db.Text)

    sents_to_words = db.relationship("Words", uselist=False, primaryjoin="Sents.sent_id==Words.sent_id")
    sents_to_bi = db.relationship("Bigrams", uselist=False, primaryjoin="Sents.sent_id==Bigrams.sent_id")
    sents_to_tri = db.relationship("Trigrams", uselist=False, primaryjoin="Sents.sent_id==Trigrams.sent_id")

class Words(db.Model):
    __tablename__ = "words"

    text_id = db.Column(db.Integer, ForeignKey('meta.text_id'))
    sent_id = db.Column(db.Integer, ForeignKey('sentences.sent_id'))
    word_id = db.Column('word_id', db.Integer,  primary_key=True)
    word = db.Column('word', db.Text)
    lemma = db.Column('lemma', db.Text)
    pos = db.Column('pos', db.Text)

class Bigrams(db.Model):
    __tablename__ = "bigrams"

    id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.Integer, ForeignKey('meta.text_id'))
    sent_id = db.Column(db.Integer, ForeignKey('sentences.sent_id'))
    word1 = db.Column('word1', db.Text)
    lemma1 = db.Column('lemma1', db.Text)
    pos1 = db.Column('pos1', db.Text)
    word2 = db.Column('word2', db.Text)
    lemma2 = db.Column('lemma2', db.Text)
    pos2 = db.Column('pos2', db.Text)

class Trigrams(db.Model):
    __tablename__ = "trigrams"

    id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.Integer, ForeignKey('meta.text_id'))
    sent_id = db.Column(db.Integer, ForeignKey('sentences.sent_id'))
    word1 = db.Column('word1', db.Text)
    lemma1 = db.Column('lemma1', db.Text)
    pos1 = db.Column('pos1', db.Text)
    word2 = db.Column('word2', db.Text)
    lemma2 = db.Column('lemma2', db.Text)
    pos2 = db.Column('pos2', db.Text)
    word3 = db.Column('word3', db.Text)
    lemma3 = db.Column('lemma3', db.Text)
    pos3 = db.Column('pos3', db.Text)