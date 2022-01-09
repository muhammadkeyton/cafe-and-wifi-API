from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

from random import choice

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random_cafe():
    all_cafe = db.session.query(Cafe).all()
    random_cafe = choice(all_cafe)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def all_cafe():
    all_cafe = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafe])

@app.route("/search")
def search_cafe():
    location = request.args.get("loc").title()
    cafes = Cafe.query.filter_by(location=location).all()
    if len(cafes) > 1:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes]),200
    elif len(cafes) < 1:
        return jsonify(result={"Notfound":f"sorry we don't have any cafe in {location}"}),404
    else:
        cafe = Cafe.query.filter_by(location=location).first()
        return jsonify(cafe=cafe.to_dict()),200

@app.route("/add",methods=["POST"])
def add_cafe():
    name = request.form["name"]
    map_url = request.form["map_url"]
    img_url = request.form["img_url"]
    location = request.form["location"]
    seats = request.form["seats"]
    has_toilet = bool(request.form["has_toilet"])
    has_wifi = bool(request.form["has_wifi"])
    has_sockets = bool(request.form["has_sockets"])
    can_take_calls = bool(request.form["can_take_calls"])
    coffee_price = request.form["coffee_price"]

    new_cafe = Cafe(name=name,
                    map_url=map_url,
                    img_url=img_url,
                    location=location,
                    seats=seats,
                    has_toilet=has_toilet,
                    has_wifi=has_wifi,
                    has_sockets=has_sockets,
                    can_take_calls=can_take_calls,
                    coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(result={
        "success": "successfully added new cafe to the database"
    }),200


@app.route("/update-price/<id>",methods=["PATCH"])
def update_coffee_price(id):
    cafe = Cafe.query.filter_by(id=id).first()
    if cafe:
        cafe.coffee_price = f'ksh {request.args.get("price")}'
        db.session.commit()
        return jsonify(result={
            "success":f"coffee price for {cafe.name} cafe has been successfully updated."
        }),200
    else:
        return jsonify(result={
            "fail":f"sorry the id {id} doesn't match any cafe in the database."
        }),404

@app.route("/remove-cafe/<id>",methods=["DELETE"])
def delete_cafe(id):
    api_key = request.args.get("api-key")
    if api_key == "delete123":
        cafe = Cafe.query.filter_by(id=id).first()
        if cafe:
            db.session.delete(cafe)
            return jsonify(result={
                'success':f"successfully deleted {cafe.name} from database"
            }),200
        else:
            return jsonify(error=f"cafe with the id {id} can't be deleted because it doesn't exist in the database."),404
    else:
        return jsonify(error="either you didn't provide any api-key or your api-key is not recognized so You are not authorised to delete anything."),403
if __name__ == '__main__':
    app.run(debug=True)
