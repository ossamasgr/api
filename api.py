import asyncio
import sys
import xmltodict as xmltodict
import pandas as pd
import json
from flask import Flask,  request , jsonify, send_from_directory,render_template,abort
import os
import nest_asyncio
sys.setrecursionlimit(5000)
nest_asyncio.apply()


#ALLOWED_EXTENSIONS = {'ppt','doc', 'pdf','xml'}
UPLOAD_DIRECTORY = "uploads"



if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

 
api = Flask(__name__) 
api.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY

# def allowed_file(file):
#     return '.' in file and \
#            file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/<path:path>",)  
def get_file(path):
    """Download a file.""" 
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True) 
  

@api.route("/files/<filename>", methods=["POST","GET"])
async def post_file(filename):
    """Upload a file."""
    pathfile = os.path.join(UPLOAD_DIRECTORY, filename)
    
    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    with open(pathfile, "wb")  as fp:
        fp.write(request.data)  
        
    with open(pathfile, encoding='utf_8',) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
    
    with open(pathfile, 'r') as f:
        res = f.read().replace('http://hr.joinvision.com/xml/3_0', 'http://hr.octopeek.com/xml/3_0') 

    with open(pathfile, 'w') as f: 
        f.write(res)
        xml_file.close()
            
        json_data = json.dumps(data_dict)
        
        with open("uploads/data.json", "w", ) as json_file:
            json_file.write(json_data)
            json_file.close() 
        with open('uploads/data.json') as f: 
            d = json.load(f)
        df = pd.json_normalize(d)
        df = df.to_dict('records')
        df = pd.json_normalize(df)
        data = df.to_json("uploads/data.json", orient="records")

    with open('uploads/data.json', 'r') as data_file:
        data = json.load(data_file)

    for element in data:
        element.pop('cv.@xmlns', None)

    for element in data:
        element.pop('cv.binaryDocuments.document', None)
    with open('uploads/data.json', 'w') as data_file:
        data = json.dump(data, data_file)

    with open('uploads/data.json', 'r') as data_file:
        data = json.load(data_file)

    output = pd.DataFrame(data, columns=["cv.personalInformation.firstname",
                                         "cv.personalInformation.lastname",
                                         "cv.personalInformation.gender.code",
                                         "cv.personalInformation.gender.name",
                                         "cv.personalInformation.title",
                                         "cv.personalInformation.isced.code",
                                         "cv.personalInformation.isced.name",
                                         "cv.personalInformation.birthyear",
                                         "cv.personalInformation.civilState"
                                         "cv.personalInformation.address.street",
                                         "cv.personalInformation.address.postcode",
                                         "cv.personalInformation.address.city",
                                         "cv.personalInformation.address.country.code",
                                         "cv.personalInformation.address.country.name",
                                         "cv.personalInformation.address.state",
                                         "cv.personalInformation.email",
                                         "cv.personalInformation.phoneNumber",
                                         "cv.personalInformation.homepage",
                                         "cv.work.phase",
                                         "cv.work.additionalText",
                                         "cv.education.phase",
                                         "cv.education.additionalText",
                                         "cv.additionalInformation.language",
                                         "cv.additionalInformation.competences",
                                         "cv.additionalInformation", ])
    output.to_csv('uploads/data.csv')
    return jsonify(data)
@api.route('/')
def getresponse():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(post_file())
    return result

    # Return 201 CREATED
    
if __name__ == "__main__":
    api.run()
