import json
from flask import Flask, request, jsonify
from flasgger import Swagger
from flasgger.utils import swag_from
from flasgger import LazyString, LazyJSONEncoder
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for
import os
import csv
import base64
from io import BytesIO
import boto3


ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

output={}
app = Flask(__name__)

@app.route("/")

def index():
    print(app.config)
    return "MetaData & Data API"


@app.route("/MetaData-file-API", methods=["POST"])

def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp

    file = request.files['file']

    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_name= file.filename
        file_name = file_name.split(".")

        if file_name[1] == 'txt':
            metadata_txt = {}
            data_txt={}
            file_tmp = request.files['file'].read()
            file_tmp = file_tmp.decode("utf8")
            metadata_txt['file name']=file_name[0]
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            metadata_txt['file size']=file_length
            metadata_txt['file type']=file_name[1]
            
            output['File Data']= file_tmp
            output['File MetaData'] = metadata_txt
            return jsonify(output)
        elif file_name[1] == 'csv':
            metadata_csv={}
            fileString = file.read().decode('utf-8')
            datafile = [{k: v for k, v in row.items()} for row in csv.DictReader(fileString.splitlines(), skipinitialspace=True)]
            metadata_csv['file name']=file_name[0]
            metadata_csv['file type']=file_name[1]
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            metadata_csv['file size']= file_length
            output['File Data']= datafile
            output['File MetaData'] = metadata_csv
            return jsonify(output)

        elif file_name[1]=='png':
            metadata_png={}
            encoded_string = base64.b64encode(file.read())
            encoded_string = encoded_string.decode('utf-8')
            metadata_png['file name']=file_name[0]
            file.seek(0,os.SEEK_END)
            file_length = file.tell()
            metadata_png['file type']=file_name[1]
            metadata_png['file size']= file_length          
            #encoded_string = base64.b64encode(file.read().decode('utf-8'))
            output['File data']=encoded_string
            output['File Metadata']=metadata_png
            return jsonify(output)
   
    else:
        resp = jsonify({'message' : 'Allowed file types are txt, csv, png'})
        resp.status_code = 400
        return resp

