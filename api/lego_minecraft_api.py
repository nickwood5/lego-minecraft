import flask, os, model_generator
from flask import jsonify, request, Blueprint
from uuid import uuid4

UPLOAD_FOLDER = '/home/nickwood5/lego_minecraft/uploaded_chunks'
GENERATED_MODELS_FOLDER = '/home/nickwood5/lego_minecraft/generated_models'
ALLOWED_EXTENSIONS = set(['mca'])

def is_allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_text_response(message):
    return flask.make_response(jsonify({"message": message}))


lego_minecraft_api = Blueprint('lego_minecraft_api', __name__)


@lego_minecraft_api.route("/lego_minecraft/test", methods=['GET', 'POST'])
def test():
    return create_text_response("Lego Minecraft API online")

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
        file_name = str(file_uuid) + ".mca"
        print(file_name)

        file.save(os.path.join(UPLOAD_FOLDER, file_name))

        return create_text_response("Success")
    else:
        return create_text_response("Invalid file type.")

@lego_minecraft_api.route("/lego_minecraft/access_model/<string:model_name>", methods=['GET', 'POST'])
def access_model(model_name: str):
    file_path = os.path.join(GENERATED_MODELS_FOLDER, model_name + ".ldr")
    try:
        f = open(file_path, "r")
        return f.read()
    except:
        return create_text_response("File not found")


