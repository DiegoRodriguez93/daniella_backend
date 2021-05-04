from flask import Flask, jsonify, request, send_file
from flask_cors import CORS, cross_origin
import os
from os.path import join, dirname, realpath
from pymongo import MongoClient
from bson.json_util import dumps
from werkzeug.utils import secure_filename
import datetime
import uuid

ALLOWED_EXTENSIONS_FOR_IMAGES = {'jfif', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = join(
    dirname(realpath(__file__)), 'uploads/')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max 16mb
CORS(app)

client = MongoClient(os.environ.get('DB'))
db = client.store


@app.route('/')
def home():
    return jsonify({"welcome": 200}), 200


@app.route('/home-products')
def homeProducts():
    products = db.productos.find({}, {'_id': False}).limit(4)
    return dumps(products)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_FOR_IMAGES


@app.route('/upload-product', methods=['POST'])
def uploadProduct():

    img1 = request.files['img1']
    img2 = request.files['img2']
    name = request.form['name']
    price = request.form['price']
    active = 1
    date = datetime.datetime.utcnow()

    if img1 and img2 and allowed_file(img1.filename) and allowed_file(img2.filename):

        img1name = secure_filename(img1.filename)
        img2name = secure_filename(img2.filename)

        img1.save(os.path.join(app.config['UPLOAD_FOLDER'], img1name))
        img2.save(os.path.join(app.config['UPLOAD_FOLDER'], img2name))

        img1Path = '/uploads/' + img1name
        img2Path = '/uploads/' + img2name

        _id = db.productos.insert_one({
            'id': str(uuid.uuid4()),
            'img1': img1Path,
            'img2': img2Path,
            'name': name,
            'price': price,
            'active': active,
            'date': date
        })

        return jsonify({"message": "Product uploaded successfully", "result": True}), 200


@app.route('/uploads/<image>')
def returnImage(image):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'])+image, attachment_filename=image)
    except Exception as e:
        # TODO: ADD NOT FOUND IMAGE TO RESOLVE FAIL IMAGE REQUEST
        return jsonify({"message": "Image not found", "result": False}), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
