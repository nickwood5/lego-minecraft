import flask, os
from urllib import request
from flask_cors import CORS
from flask import Flask, jsonify, request, Blueprint
from flask_restful import Api
from werkzeug.utils import secure_filename
from uuid import uuid4

UPLOAD_FOLDER = '/home/nickwood5/lego_minecraft/uploaded_chunks'
ALLOWED_EXTENSIONS = set(['mca'])

def is_allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_text_response(message):
    return flask.make_response(jsonify({"message": message}))


lego_minecraft_api = Blueprint('lego_minecraft_api', __name__)


@lego_minecraft_api.route("/lego_minecraft/upload_chunk", methods=["POST"])
def receive_minecraft_chunk():
    if "file" not in request.files:
        return create_text_response("Bad request type.")

    file = request.files["file"]
    file_name = file.filename
    if file_name == "":
        return create_text_response("No selected file.")
    
    if file and is_allowed_file(file_name):
        
        file_uuid = uuid4()
        file_name = str(file_uuid) + ".ldr"
        print(file_name)

        file.save(os.path.join(UPLOAD_FOLDER, file_name))

        return create_text_response("Success")
    else:
        return create_text_response("Invalid file type.")