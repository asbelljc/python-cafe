import random
from dataclasses import dataclass  # allows for easy json serialization

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
@dataclass
class Cafe(db.Model):
    # dataclass REQUIRES static typing (otherwise jsonify just returns empty object)
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(250), unique=True, nullable=False)
    map_url: str = db.Column(db.String(500), nullable=False)
    img_url: str = db.Column(db.String(500), nullable=False)
    location: str = db.Column(db.String(250), nullable=False)
    seats: str = db.Column(db.String(250), nullable=False)
    has_toilet: bool = db.Column(db.Boolean, nullable=False)
    has_wifi: bool = db.Column(db.Boolean, nullable=False)
    has_sockets: bool = db.Column(db.Boolean, nullable=False)
    can_take_calls: bool = db.Column(db.Boolean, nullable=False)
    coffee_price: str = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    # get number of rows in db
    row_count = Cafe.query.count()
    # generate random number for skipping records
    random_offset = random.randint(0, row_count - 1)
    # return first record after skip
    random_cafe = Cafe.query.offset(random_offset).first()

    return jsonify(random_cafe), 200


@app.route("/all")
def get_all_cafes():
    cafes = Cafe.query.all()

    return jsonify(cafes), 200


@app.route("/search")
def search():
    location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=location).all()

    if len(cafes) == 0:
        return (
            jsonify(
                error={"Not Found": "Sorry, we don't have a cafe at that location."}
            ),
            404,
        )
    else:
        return jsonify(cafes), 200


@app.route("/new", methods=["POST"])
def add_new_cafe():
    body = request.get_json()
    print(body)

    new_cafe = Cafe(
        name=body["name"],
        map_url=body["map_url"],
        img_url=body["img_url"],
        location=body["location"],
        seats=body["seats"],
        has_toilet=body["has_toilet"],
        has_wifi=body["has_wifi"],
        has_sockets=body["has_sockets"],
        can_take_calls=body["can_take_calls"],
        coffee_price=body["coffee_price"],
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "New cafe successfully added."}), 200


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = Cafe.query.get(cafe_id)

    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()

        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return (
            jsonify(
                error={
                    "Not Found": "Sorry, a cafe with that id was not found in the database."
                }
            ),
            404,
        )


if __name__ == "__main__":
    app.run(debug=True)
