from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
from os.path import join, dirname, realpath
from pymongo import MongoClient
from bson.json_util import dumps
from werkzeug.utils import secure_filename
import datetime

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
    products = db.products.find()
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

        img1Path = 'uploads/' + img1name
        img2Path = 'uploads/' + img2name

        _id = db.products.insert_one({
            'img1': img1Path,
            'img2': img2Path,
            'name': name,
            'price': price,
            'active': active,
            'date': date
        })

        return jsonify({"message": "Product uploaded successfully", "result": True}), 200


""" def post_image(img_file):
    img = open(img_file, 'rb').read()
    response = requests.post(URL, data=img, headers=headers)
    return response """

"""     img1.save(secure_filename(img1.filename))
    img2.save(secure_filename(img2.filename)) """


""" @app.route('/posts')
def posts():
    _items = db.posts.find({}, {'_id': False})
    return dumps(_items)

def insert():
    post = {"author": "Diego",
            "text": "My first blog post!",
            "tags": ["mongodb", "python", "pymongo"],
            "date": datetime.datetime.utcnow()}
    db.posts.insert_one(post) """

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
