import requests
from flask import Flask, request, jsonify, send_file, jsonify, abort, redirect
from functions import getRecordDB ,newRecord, deleteRecord, get_json_data, save_cmdi
from config import config


app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = '/data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# wordt maar 1 keer gedaan na het opstarten
@app.before_first_request
def before_first_request():
    print('initialisatie')




@app.route("/")
def hello_world():
    retStruc = {"app": "Huc Editor service", "version": "0.1"}
    return jsonify(retStruc)


@app.route("/get_json/<filename>", methods=['GET'])
def get_json(filename):
    errorMsg = jsonify({"status": "error"})
    if filename == None:
        return errorMsg
    else:
        data = get_json_data(filename)
    return jsonify(data)

@app.route("/delete_record/<filename>" , methods=['GET'])
def delete(filename):
    response = deleteRecord(filename)
    return jsonify(response)


@app.route("/write_record", methods=['POST'] )
def write_record():
    ccData = request.form["ccData"]
    ccProfileID = request.form["ccProfileID"]
    ccRecordFile = request.form["ccRecordFile"]
    url = config['CMDI_API'] + "create_record"
    data = {"ccData": ccData, "ccProfileID": ccProfileID}
    resp = requests.post(url, data=data)
    save_cmdi(resp.text, ccRecordFile)
    return redirect(config["FRONTEND_URL"])



# hier moet de sqllite database bevraagd worden, om de lijstpagina te genereren
@app.route("/get_cmdi_files")
def getCMDIfiles():
    structure = {'message': 'nothing yet'}
    # data = 'data/'
    status = 'OK'
    # structure = fs_tree_to_dict(data)
    # print(structure)
    structure = getRecordDB()

    response = {"status": status, "structure": structure}
    return jsonify(response)

@app.route("/create_record/<profile>")
def create_record(profile):
    structure = newRecord(profile);
    print(structure)
    return jsonify(structure)










#Start main program

if __name__ == '__main__':
    app.run()

