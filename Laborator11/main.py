from flask import Flask, request, jsonify, abort
import os
import time
from pathlib import Path


app = Flask(__name__)

BASE_DIR = Path(__file__).parent.absolute()
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'files') 

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

UPLOAD_FOLDER = 'C:\\Users\\gabri\\Desktop\\temp_folder'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

#listarea continutului unui director
@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        return jsonify({'files': files})
    except Exception as e:
        abort(404, description = "The server cannot find the requested resource")


#listarea continutului unui fisier text, specificat prin nume
@app.route('/files/<string:filename>', methods=['GET'])
def get_file_content(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)    
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({'filename': filename, 'content': content})
    except Exception as e:
        abort(404, description = "The server cannot find the requested resource")

#crearea unui fisier specificat prin nume si continut
#aceasta metoda este folosita si pentru modificarea continutului
#unui fisier specificat prin nume
@app.route('/files/<string:filename>', methods =['PUT'])
def create_file(filename):
    try:
        data = request.get_json()
        content = data.get('content')
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return jsonify({'message': 'The file has been created/updated successfully', 'filename': filename})
    except Exception as e:
        abort(400, description = "Invalid request message")



#crearea unui fisier specificat prin continut
@app.route('/files', methods = ['POST'])
def create_file_post():

    try:

        content = request.get_json().get('content')

        # generate a random file name like 'file_1625097600.txt'
        filename = f"file_{int(time.time())}.txt"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return jsonify({
            "message": "The file has been created succesfully",
            "filename": filename 
        }), 201

    except Exception as e:
        abort(400, description = "Invalid request message")


#stergerea unui fisier specificat prin nume
@app.route('/files/<string:filename>', methods = ['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        os.remove(file_path)
        return jsonify({'message': 'The file has been deleted succesfully', 'filename': filename})
    except Exception as e:
        abort(404, description = "The server cannot find the requested resource")

@app.errorhandler(400)
@app.errorhandler(404)
def handle_errors(error):
    return jsonify({'error': error.description}), error.code

if __name__ == '__main__':
    app.run(debug=True)