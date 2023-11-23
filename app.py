from flask import Flask, request, jsonify, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path
from sqlalchemy.sql import func

BASE_DIR = Path(__file__).parent 
DATABASE = BASE_DIR / 'quotes.db'

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class AuthorModel(db.Model):
   __tablename__ = 'authors'
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(32), unique=True)
   quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

   def __init__(self, name):
       self.name = name

   def __repr__(self) -> str:
       return f'author {self.name}'

   def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
    }


class QuoteModel(db.Model):
   __tablename__ = 'quotes'
   id = db.Column(db.Integer, primary_key=True)
   author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
   text = db.Column(db.String(255), unique=False)
   rating = db.Column(db.Integer, unique=False, nullable=False, default=1)
   created = db.Column(db.DateTime(timezone=True), server_default=func.now())

   def __init__(self, author, text, rating=1):
       self.author_id = author.id
       self.text  = text
       self.rating = rating

   def __repr__(self) -> str:
       return f'Quote ({self.author_id}, {self.text}, {self.rating})'

   def to_dict(self):
        return {
            "id": self.id,
            "author": self.author_id.to_dict(),
            "text": self.text,
            "rating": self.rating
    }
   
   def to_dict_by_author(self):
        return {
            "text": self.text,
            "rating": self.rating
    }

   
# Get all authors
@app.route("/authors", methods=['GET'])
def get_all_authors():
    authors = AuthorModel.query.all()
    authors_as_dict = [author.to_dict() for author in authors]
    return jsonify(authors_as_dict), 200

# Get one authors by id
@app.route("/authors/<int:author_id>", methods=['GET'])
def get_authors_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, f"Quote with id={author_id} not found")
    return jsonify(author.to_dict()), 200

# Create new author
@app.post("/authors")
def create_author():
    author_data = request.json
    author = AuthorModel(author_data["name"])
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201

# Update author
@app.put("/authors/<int:id>")
def update_author(id):
    author_data = request.json
    author = AuthorModel.query.get(id)
    if author is None:
        abort(404, f"Quote with id={id} not found")
    for key, value in author_data.items():
        setattr(author, key, value)
    db.session.commit()
    return jsonify(author.to_dict()), 200

# Delete author
@app.delete("/authors/<int:id>")
def delete_author(id):
    author = AuthorModel.query.get(id)
    if author is None:
        abort(404, f"Quote with id={id} not found")
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': f"Quote with id={id} has deleted"}), 200

#  Get quote by author id
@app.route("/authors/<int:author_id>/quotes", methods=['GET'])
def get_quote_by_author(author_id):
    author = AuthorModel.query.get(author_id)
    quotes = QuoteModel.query.filter(QuoteModel.author_id == author.id).all()
    result = [quote.to_dict_by_author() for quote in quotes]
    if len(result) == 0: 
        abort(404, f"Quotes with {author} not found")
    return jsonify(result), 201

#  Create New quote by author
@app.route("/authors/<int:author_id>/quotes", methods=['POST'])
def create_quoted(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        abort(404, f"Quote with id={id} not found")
    new_quote = request.json
    q = QuoteModel(author, **new_quote)
    db.session.add(q)
    db.session.commit()
    return jsonify(new_quote), 201

# Get all quotes
@app.route("/quotes", methods=['GET'])
def get_all_quotes():
    quotes = QuoteModel.query.all()
    quotes_as_dict = [quote.to_dict() for quote in quotes]
    return jsonify(quotes_as_dict), 200

# Get one quotes
@app.route("/quotes/<int:id>", methods=['GET'])
def get_quotes_by_id(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, f"Quote with id={id} not found")
    return jsonify(quote.to_dict()), 200

# Change quotes
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

# Delete quotes
@app.delete("/quotes/<int:id>")
def delete_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        abort(404, f"Quote with id={id} not found")
    db.session.delete(quote)
    db.session.commit()
    return jsonify({'message': f"Quote with id={id} has deleted"}), 200

# Filter quotes
@app.route("/quotes/filter", methods=['GET'])
def qef_quotes_by_filter():
    kwargs = request.args
    quotes = QuoteModel.query.filter_by(**kwargs).all()
    result = [quote.to_dict() for quote in quotes]
    return jsonify(result)


if __name__ == "__main__":
   app.run(debug=True)
