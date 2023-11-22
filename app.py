from flask import Flask, request, jsonify, abort
from random import randint



app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}
quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
       "rating" : '4'
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
       "rating" : '5'
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
       "rating" : '4'
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так.",
       "rating" : '3'
   },
]

@app.route("/")
def hello_world():
   return "Hello, World!"

@app.route("/about")
def about():
   return about_me

@app.route("/quotes/filter", methods=['GET'])
def get_quote():
    args = request.args
    list_query = list()
    for quote in quotes:
        if all(args.get(key, type=type(quote[key])) == quote[key] for key in args):
            list_query.append(quote)
    # if len(args) > 1:
    #     for quot in quotes:
    #         if quot['rating'] == args['rating'] and quot['author'] == args['author']:
    #             list_query.append(quot)
    # elif 'rating' in args.keys():
    #     for quot in quotes:
    #         if quot['rating'] == args['rating']:
    #             list_query.append(quot)
    # else:
    #     for quot in quotes:
    #         if quot['author'] == args['author']:
    #             list_query.append(quot)
    return jsonify(list_query)

@app.route("/quotes", methods=['POST'])
def create_quote():
   new_quote = request.json
   last_quote = quotes[-1]
   new_quote['id'] = last_quote['id'] + 1
   if 'rating' not in quotes.keys():
       new_quote['rating'] = 1
   if new_quote['rating'] >= 5:
       new_quote['rating'] = 1
   quotes.append(new_quote)
   return jsonify(new_quote), 201

@app.route("/quotes/<int:id>", methods=['PUT'])
def get_quotes(id):
    if 1 <= id <= len(quotes):
        new_data = request.json
        quotes[id-1].update(new_data)
        return jsonify(quotes[id-1]), 200
    return f"Quote with id={id} not found", 404

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
   if 1 <= id <= len(quotes):
        return f"Quote with id {id} is deleted.", 200
   abort(404, f"Quote with id={id} not found")


@app.route("/quotes/count")
def get_quotes_count():
    return {'count': len(quotes)}, 200

@app.route("/quotes/random")
def get_random_quotes():
    return jsonify(quotes[randint(0, len(quotes)-1)]), 200

if __name__ == "__main__":
   app.run(debug=True)
