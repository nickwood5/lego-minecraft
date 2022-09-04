import flask, os
from urllib import request
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_restful import Api
from werkzeug.utils import secure_filename
from uuid import uuid4

app = Flask(__name__)
CORS(app)
api = Api(app)

UPLOAD_FOLDER = '/home/nickwood5/lego_minecraft/uploaded_chunks'
ALLOWED_EXTENSIONS = set(['mca'])

def is_allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_text_response(message):
    return flask.make_response(jsonify({"message": message}))



@app.route("/upload_minecraft_chunk", methods=["POST"])
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



if __name__ == "__main__":
    app.run(debug=True)