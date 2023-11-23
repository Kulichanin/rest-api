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

   def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text
    }

@app.errorhandler(HTTPException)
def hadle_exception(e):
    return jsonify({'massage': e.description}), e.code

@app.route("/quotes", methods=['GET'])
def get_all_quotes():
    quotes = QuoteModel.query.all()
    quotes_as_dict = [quote.to_dict() for quote in quotes]
    return jsonify(quotes_as_dict), 200

@app.route("/quotes/<int:id>", methods=['GET'])
def get_quotes_by_id(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, f"Quote with id={id} not found")
    return jsonify(quote.to_dict()), 200

@app.post("/quotes")
def create_quote():
    quote_data = request.json
    quote = QuoteModel(quote_data["author"], quote_data["text"], quote_data["rating"])
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 201

@app.put("/quotes/<int:id>")
def update_quote(id):
    quote_data = request.json
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, f"Quote with id={id} not found")
    for key, value in quote_data.items():
        setattr(quote, key, value)
    db.session.commit()
    return jsonify(quote.to_dict()), 200

@app.delete("/quotes/<int:id>")
def delete_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, f"Quote with id={id} not found")
    db.session.delete(quote)
    db.session.commit()
    return jsonify({'message': f"Quote with id={quote.to_dict()} has deleted"}), 200


if __name__ == "__main__":
   app.run(debug=True)
