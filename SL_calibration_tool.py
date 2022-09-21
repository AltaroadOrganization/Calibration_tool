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

#get AWS access key and secret key
ACCESS_KEY = st.secrets["my_access_key"]["ACCESS_KEY"]
SECRET_KEY = st.secrets["my_access_key"]["SECRET_KEY"]


#function to load the dict to a S3 bucket
def read_write_S3(bucket_name, the_dict, access_key, secret_key):
    '''
    this function adds a "new simulator user file" to a bucket
    '''
    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3 = session.resource('s3')
    heure=the_dict['date_heure'].replace('/','_').replace(' ','_')
    object = s3.Object(bucket_name, 'calibration_tool/calibration_userfile_{}.txt'.format(heure))
    #df=pd.DataFrame.from_dict(the_dict)
    result = object.put(Body=str(the_dict))

def show():
    #all the inputs and outputs are saved in a dict
    simulator_dict={}

    Image_title=Image.open("Banner_Linkedin.png")
    st.image(Image_title)

    col1, col2 = st.columns([1, 1])
    image = Image.open("logo.png")
    now = datetime.datetime.utcnow()
    result = now + datetime.timedelta(hours=2)
    date_heure = result.strftime("%d/%m/%Y %H:%M:%S")
    date = result.strftime("%d/%m/%Y")
    heure = result.strftime("%H:%M:%S")
    st.caption("début de session - Date et heure : {}".format(date_heure))
    simulator_dict['date_heure']=date_heure

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

if __name__ == "__main__":

    initial_passage_dict = {
            "name_user": "",
            "truck_mass": 0,
            "passage_speed":0,
            "truck_plate": "unknown",
            "user_comments": "",
            "truck_speed":0,
            "numero_passage":0,
            "pushed_state":False
        }

    #gestion de session state
    for my_key in initial_passage_dict.keys():
        if my_key not in st.session_state:
            st.session_state[my_key] = initial_dict[my_key]

    calibration_passage_dict=show()

    #gestion de session state
    for my_key in initial_passage_dict.keys():
        if my_key not in st.session_state:
            st.session_state[my_key] = initial_passage_dict[my_key]
        else:
            try:
                st.session_state[my_key]=calibration_passage_dict[my_key]
            except:
                st.session_state[my_key] = initial_passage_dict[my_key]

    if "pushed_state" not in st.session_state:
        st.session_state.pushed_state = False

