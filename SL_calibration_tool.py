import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
from csv import writer
from fpdf import FPDF
import math
import random
import datetime
import re
import boto3
#import cv2
from PIL import Image
import numpy as np
import io
import os

#get AWS access key and secret key
ACCESS_KEY = st.secrets["my_access_key"]["ACCESS_KEY"]
SECRET_KEY = st.secrets["my_access_key"]["SECRET_KEY"]

#function to load the dict to a S3 bucket
def read_write_S3(bucket_name, the_dict, timestamp_image, access_key, secret_key):
    '''
    this function adds a "new simulator user file" to a bucket
    '''
    try:
        session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        s3 = session.resource('s3')
        now = datetime.datetime.utcnow()
        result = now + datetime.timedelta(hours=2)
        date_heure = result.strftime("%d/%m/%Y %H:%M:%S")

        #save the dict
        the_dict["date_heure"]=date_heure
        the_dict["timestamp"]=int(datetime.datetime.timestamp(now)+3600*2)
        object = s3.Object(bucket_name, 'calibration_tool/calibration_userfile_{}.txt'.format(str(the_dict["timestamp"])))
        #df=pd.DataFrame.from_dict(the_dict)
        result = object.put(Body=str(the_dict))
        the_dict["pushed_state"]=True

        #save the image
        if timestamp_image!='empty':
            file_name='./passage_image_{}.jpg'.format(timestamp_image)
            key_name='calibration_tool/passage_image_{}.jpg'.format(str(the_dict["timestamp"]))
            s3=session.client("s3")
            s3.upload_file(file_name, bucket_name, key_name)
            the_dict["has_image"] = True
        else:
            the_dict["has_image"] = False
            pass
        return the_dict
    except Exception as e:
        st.write("Erreur de sauvegarde sur S3")
        return the_dict

def show():
    #all the inputs and outputs are saved in a dict
    calibration_passage_dict={}

    Image_title=Image.open("Banner_Linkedin.png")
    st.image(Image_title)

    col1, col2 = st.columns([1, 1])
    image = Image.open("logo.png")
    now = datetime.datetime.utcnow()
    result = now + datetime.timedelta(hours=2)
    date_heure = result.strftime("%d/%m/%Y %H:%M:%S")
    date = result.strftime("%d/%m/%Y")
    heure = result.strftime("%H:%M:%S")
    st.caption("d??but de session - Date et heure : {}".format(date_heure))
    bucket_name = 'dataset-altaroad-public'

    with col1:
        original_title = '''
        <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Sen">
        <p style="font-family:Sen; color:#f37121; letter-spacing: -1px; line-height: 1.2; font-size: 40px;">Outil de calibration terrain</p>
        </head>
        '''
        st.markdown(original_title, unsafe_allow_html=True)
    with col2:
        st.image(image)

    st.write("")
    st.write("Cet outil permet de sauver un timestamp de passage de calibration dans S3")

    st.subheader("Utilisateur")
    calibration_passage_dict["client_name"]=st.text_input("Nom du client","")
    calibration_passage_dict["user_name"]=st.text_input("Nom d'utilisateur","")
    calibration_passage_dict["user_comments"]=st.text_input("Commentaires (trajectoire...)","")

    st.subheader("Passage")
    calibration_passage_dict["truck_plate"]=st.text_input("Plaque immatriculation Camion","XX111YY")
    calibration_passage_dict["truck_mass"]=st.text_input("Masse (kg)","000000")
    calibration_passage_dict["truck_speed"]=st.text_input("Vitesse (km/h)","000")
    calibration_passage_dict["numero_passage"]=st.text_input("Num??ro de passage","1")

    #take an image
    img_file_buffer = st.camera_input("Take a picture")

    if img_file_buffer is not None:
        timestamp_image=int(datetime.datetime.timestamp(now) + 3600 * 2)
        timestamp_image='1'
        # To read image file buffer with OpenCV:
        img = Image.open(img_file_buffer)
        # save the image
        img.convert('RGB')
        img.save('./passage_image_{}.jpg'.format(timestamp_image))
    else:
        img=np.array([])
        timestamp_image='empty'

    if st.button(label="Pousser sur S3"):
        read_write_S3(bucket_name, calibration_passage_dict, timestamp_image, ACCESS_KEY, SECRET_KEY)
        st.write(calibration_passage_dict)

    return calibration_passage_dict, img

if __name__ == "__main__":

    initial_passage_dict = {
            "user_name": "",
            "client_name":"",
            "truck_mass": 0,
            "truck_plate": "unknown",
            "user_comments": "",
            "truck_speed":0,
            "numero_passage":0,
            "pushed_state":False,
            "date_heure":"",
            "timestamp":"",
            "has_image":False
            }

    calibration_passage_dict, img=show()

