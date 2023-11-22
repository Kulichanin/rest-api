import sqlite3

from flask import Flask, request, jsonify, abort, g
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

BASE_DIR = Path(__file__).parent 
DATABASE = BASE_DIR / 'main.db'

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(32), unique=False)
   text = db.Column(db.String(255), unique=False)
   rating = db.Column(db.Integer, unique=False, nullable=False, default=1)

   def __init__(self, author, text, rating):
       self.author = author
       self.text  = text
       self.rating = rating

@app.errorhandler(HTTPException)
def hadle_exception(e):
    return jsonify({'massage': e.description}), e.code

@app.route("/quotes", methods=['GET'])
def get_all_quotes():
    cursor = get_db().cursor()
    select_quote_by_id = f"SELECT * FROM"
    cursor.execute(select_quote_by_id)
    quotes_db = cursor.fetchone()
    keys = ["id", "author", "text", "rating"]
    quotes = [dict(zip(keys, quote_db)) for quote_db in quotes_db]
    return jsonify(quotes)

@app.route("/quotes/<int:id>", methods=['GET'])
def get_quotes_by_id(id):
    cursor = get_db().cursor()
    select_quote_by_id = f"SELECT * FROM quotes WHERE id={id}"
    cursor.execute(select_quote_by_id)
    quotes_db = cursor.fetchone()
    keys = ["id", "author", "text", "rating"]
    if quotes_db is None:
        abort(404, f"Quote with id={id} not found")
    quote = dict(zip(keys, quotes_db))
    return jsonify(quote)

@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    create_quote = f"INSERT INTO quotes (author, text, rating) VALUES ('{new_quote['author']}', '{new_quote['text']}', '{new_quote['rating']}')"
    cursor.execute(create_quote)
    conn.commit()
    new_quote_id = cursor.lastrowid
    new_quote['id'] = new_quote_id
    return jsonify(new_quote), 201

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    if 1 <= id <= cursor.fetchall().count:
        del_quote = f"DELETE FROM quotes WHERE id={id}"
        cursor.execute(del_quote)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(del_quote), 201
    abort(404, f"Quote with id={id} not found")

@app.route("/quotes/<int:id>", methods=['PUT'])
def update_quote(id):
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    update_quote = f"UPDATE quotes SET author='{new_quote['author']}', text='{new_quote['text']}', rating='{new_quote['rating']}' WHERE id={id}"
    cursor.execute(update_quote)
    conn.commit()
    select_quote_by_id = f"SELECT * FROM quotes WHERE id={id}"
    cursor.execute(select_quote_by_id)
    quotes_db = cursor.fetchone()
    keys = ["id", "author", "text", "rating"]
    quote = dict(zip(keys, quotes_db))
    return jsonify(quote)


if __name__ == "__main__":
   app.run(debug=True)
