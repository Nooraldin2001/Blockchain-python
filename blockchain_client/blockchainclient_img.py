import hashlib
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
import binascii
from collections import OrderedDict
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import cv2 as cv
import json
import os 
import requests



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'C:\\Noor_work\\4th_y_term_2\\blockchain\\venv\\src\\blockchain_client\\imgs'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/transactions')
def view_transactions():
    return render_template('view_transactions.html')

@app.route('/rigester/img')
def make_transaction():
    return render_template('rigester_img.html')

@app.route('/wallet/new')
def new_wallet():
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()

    response = {
        'private_key': binascii.hexlify(private_key.export_key(format('DER'))).decode('ascii'),
        'public_key': binascii.hexlify(public_key.export_key(format('DER'))).decode('ascii')
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.data
    print(values)
    required = ['confirmation_image_hash', 'confirmation_features_hash', 'confirmation_sender_public_key']
    # if not all(k in values for k in required):
    #     return 'Missing values', 400

    # transaction_results = blockchain.submit_transaction(values['confirmation_image_hash'],
    #                                                     values['confirmation_features_hash'],
    #                                                     values['confirmation_sender_public_key'])
    # if transaction_results == False:
    #     response = {'message': 'Invalid transaction/signature'}
    #     return jsonify(response), 406
    # else:
    response = {'message': 'Transaction will be added to the Block '}
    
    return jsonify(response), 200


def get_surf_features(image):
    #importing the img and converting it to grayscale 
    img = cv.imread(image, cv.IMREAD_GRAYSCALE)
    
    # Create an ORB object here I gonna use ORB instead of SURF because of petant restrictions on surf
    orb = cv.ORB_create()

    # Find keypoints and descriptors directly
    kp, des = orb.detectAndCompute(img,None)
    
    data = serialize_kp_des(kp,des)
    return data

def serialize_kp_des(kp, des):
    # Convert keypoints and descriptors to a dictionary
    data = {
        'keypoints': [keypoint.pt for keypoint in kp],  # Serialize keypoints to their (x, y) coordinates
        'descriptors': des.tolist()  # Convert descriptors to a list
    }
    # Serialize the dictionary to JSON format
    json_data = json.dumps(data, sort_keys=True)

    return json_data

def image_serialize(image_path):
    # Read the image
    img = cv.imread(image_path)
    if img is None:
        raise ValueError("Unable to read the image")

    # Convert image to JSON
    image_json = json.dumps(img.tolist())

    return image_json

def get_hash_key(data):
    hash_object = hashlib.sha256(data.encode())
    return hash_object.hexdigest()

@app.route('/register_image', methods=['POST'])
def register_image():
    owner_id = request.form['owner_id']
    image_file = request.files['image']

    # Save the image file to the "imgs" folder
    if image_file:

        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        # Process the image using the insert_image function
        #blockchain = Blockchain()
        hi, hf = insert_image(image_path, owner_id)

        return jsonify({
            'image_hash': hi,  # Replace with the actual public key
            'features_hash': hf  # Replace with the actual private key
        })
    
    return jsonify({'error': 'No image file provided'})


def insert_image(image, owner_id):
    features = get_surf_features(image)
    hf = get_hash_key(features)
    hi = get_hash_key(image_serialize(image))
    entry = [hf, hi, features, owner_id]
    #blockchain.add_to_blockchain(entry)
    return hi, hf

if __name__ == '__main__':
    # print("Image Hash Key:", hi)
    # print("Features Hash Key:", hf)

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8081, type=int, help="port to listen to")
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)

