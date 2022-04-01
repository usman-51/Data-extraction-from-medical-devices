import sys,os 
print('\n\n\n\n\n',os.getcwd())

# sys.path.append('./Flask_app/')
from keras.models import load_model
import numpy as np
import pandas as pd
from .helper_functions import get_lcd, imgs_to_array
import cv2
from PIL import Image
import boto3
from werkzeug.utils import secure_filename

import numpy as np
import time
from .models import User
import datetime

from .db import *
records = return_all_docs_url(mycol)
print('\n\n---------->>>>>>> all records ', records,'\n\n')
# print('\n\n\nall users ::::::::::::::::::::: ',users)
# inserted = db.insert_values(db.mycol, document)



from flask_login import login_required, current_user, login_user
from flask import Flask, request, render_template, redirect,url_for,redirect,Blueprint


app=Flask(__name__)
main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload')
def index11():
    return render_template('index11.html')

# aws credentials
aws_textract = boto3.client(service_name='textract', region_name='<your region>',aws_access_key_id = '<aws access key>'
,aws_secret_access_key = '<aws secret access key>')


#Load CNN model trained on data pre-defined in the paper
model=load_model('./Dataset/best_model.h5')

def predict_vals(files_add, path):
    all_imgs_pred = {}
    for file in files_add:
        if file:
            filename = secure_filename(file.filename)
            file.save(filename)

            # Document
            documentName = filename
            #crop all regions

            if path == 'bp/td':
                preprocessed_img = get_lcd(documentName) # need some changes
                w, h=preprocessed_img.shape
                cv2.imwrite(filename + '_SP.jpg', preprocessed_img[0:int(h/2),0:w])
                cv2.imwrite(filename + '_DP.jpg', preprocessed_img[int(h/2):h,0:w])
                #convert img to ndarray and resize
                X_test = imgs_to_array( [filename+ '_SP.jpg',filename + '_DP.jpg'] )
                os.remove(filename+'_SP.jpg')
                os.remove(filename+'_DP.jpg')

            if path == 'glc/td':
                preprocessed_img = get_lcd(documentName) # need some changes
                w, h=preprocessed_img.shape
                # cv2.imwrite(filename + '_SP.jpg', preprocessed_img[0:int(h/2),0:w])
                cv2.imwrite(filename + '_DP.jpg', preprocessed_img[int(h/2):h,0:w])
                #convert img to ndarray and resize
                X_test = imgs_to_array( [filename+ '_DP.jpg'] )
                os.remove(filename+'_DP.jpg')

            if path == 'glc/md':
                preds = glucose_mobile(documentName)
                all_imgs_pred[documentName] = preds
                os.remove(filename)
                return all_imgs_pred

            if path == 'temp/td':
                preprocessed_img = get_lcd(documentName) # need some changes
                w, h=preprocessed_img.shape
                # cv2.imwrite(filename + '_SP.jpg', preprocessed_img[0:int(h/2),0:w])
                cv2.imwrite(filename + '_DP.jpg', preprocessed_img[int(h/2):h,0:w])
                #convert img to ndarray and resize
                X_test = imgs_to_array( [filename+ '_DP.jpg'] )
                os.remove(filename+'_DP.jpg')

            y_pred = model.predict( X_test )
            
            img_preds = []
            predicted_num = 0
            for i in range(X_test.shape[0]):
                pred_list_i = [np.argmax(pred[i]) for pred in y_pred]
                print('----------->>>>>>>',pred_list_i)
                if path == 'glc/td':
                    predicted_num = str(pred_list_i[0])+str(pred_list_i[-1])
                elif path == 'temp/td':
                    predicted_num = str(pred_list_i[0])+str(pred_list_i[-1])
                else:
                    predicted_num = 100* pred_list_i[0] + 10 * pred_list_i[1] + 1* pred_list_i[2]
                    if predicted_num >= 1000:
                        predicted_num = predicted_num-1000

                img_preds.append(int(predicted_num))
                
            all_imgs_pred[documentName] = img_preds
            os.remove(filename)
            

    # print('\nprediction---->>>>>>> ',all_imgs_pred)
    
    return all_imgs_pred


def glucose_mobile(documentName):
    # Call Amazon Textract
    with open(documentName, "rb") as document:
        response = aws_textract.detect_document_text(
        Document={
            'Bytes': document.read(),
                }
            )
    # Print text

    # print('\n\n--->>>> response ',response)
    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print ('\033[94m' +  item["Text"] + '\033[0m')
            text = text + " " + item["Text"]


    pos = text.find('mg/')
    # print('-------------->>>>>>>>>>>>\n',pos,text)
    text = text.replace('.',' ')
    final_text = [s for s in text[pos-10:pos].split() if s.isdigit()]
    return " ".join(final_text)[:4]






@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    print('asdfadfasdfasdfasd')
    if request.method == 'POST':
        # print("request forms",request.form['deviceDropdown'])
        # print("request forms",request.form['testDropdown'])
        # print('\n\n\n ------->>>>>>> : ',request.files.getlist('myimage'))
        if request.form['deviceDropdown']:
            device_dropdown = request.form['deviceDropdown']

        if request.form['testDropdown']:
            test_dropdown = request.form['testDropdown']

        if request.files.getlist('myimage'):
            files_add = request.files.getlist("myimage")
        
        # if test_dropdown+'/'+device_dropdown == 'bp/td':
        preds = predict_vals(files_add, test_dropdown+'/'+device_dropdown )
        print('\n\n=========>>>>>>>>>>\nFinal Predictions : ',preds)

        # return render_template('loading.html')
    mydict = {}
    mydict['email'] = current_user.email
    mydict['time'] = str(datetime.datetime.now().time())
    mydict['date'] = str(datetime.datetime.now().date())
    mydict['image'] = preds

    # print('\n\n\n---->>> current user', current_user.email )
    print('time :',time.time())
    x = mycol.insert_one(mydict)
    print('inserted',x)
    return render_template('index11.html')

if __name__ == '__main__':
    app.run(debug = True)