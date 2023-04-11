import streamlit as st
import requests
import base64
import pandas as pd
import json
import uuid
import xml.etree.ElementTree as ET
import boto3

# credentials
page_title = st.secrets['initialize']['page_title']
sidebar_title = st.secrets['initialize']['sidebar_title']

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = st.secrets['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = st.secrets['BING_SEARCH_V7_ENDPOINT']

# S3 config
accountid = st.secrets['aws_s3']['accountid']
access_key_id = st.secrets['aws_s3']['access_key_id']
access_key_secret = st.secrets['aws_s3']['access_key_secret']

# S3 buckets setup
@st.cache_resource()
def s3_db():
    s3 = boto3.client('s3',
        endpoint_url = 'https://{}.s3.amazonaws.com/'.format(accountid),
        aws_access_key_id = '{}'.format(access_key_id),
        aws_secret_access_key = '{}'.format(access_key_secret)
    )
    return s3

# streamlit
logo_file = ''
st.set_page_config(
    '{}'.format(page_title),
    '{}'.format(logo_file),
    layout='centered',
    initial_sidebar_state='auto',
    menu_items={
        "About": "{}".format(page_title),
    },
)

# Main Code
st.header("{}".format(page_title))
form = st.container()

# Functions
def modify_data(response):
    #df = pd.DataFrame(response.json()["webPages"]["value"]) # all Data
    #df.insert(0, column="select", value="st.selectbox") # TD - feature select box
    df = pd.DataFrame(response.json()["webPages"]["value"])
    urls = df['url']
    return urls

def input_sanitization(query):
    keywords = query.splitlines()
    return keywords

def search_bing(results_per_keyphrase):
    keywords = input_sanitization(query)
    no_of_keywords = len(keywords)
    if no_of_keywords != 0 :
        # Construct a request
        mkt = 'en-US'
        params = { 'q': query, 'mkt': mkt , 'count': results_per_keyphrase}
        headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

        # Call Bing API
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            #st.json(response.json(), expanded=False)
            
            urls = modify_data(response).tolist()
            # Create XML Document
            urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
            for url in urls:
                url_element = ET.SubElement(urlset, "url")
                loc_element = ET.SubElement(url_element, "loc")
                loc_element.text = url

            # Generate the XML sitemap
            sitemap_xml = ET.tostring(urlset, encoding="unicode", method="xml")

            # Print the XML sitemap
            s3 = s3_db()
            unique_filename = f'{uuid.uuid4()}.xml'
            content_type = 'application/xml'
            s3.put_object(Body=sitemap_xml, Bucket=accountid, Key=unique_filename, ACL='public-read', ContentType=content_type)
            url = f'https://{accountid}.s3.amazonaws.com/{accountid}/{unique_filename}'

            st.write("XML Response for `{}`:".format(query))
            st.code(url, language="text")

            return sitemap_xml, query
        except Exception as ex:
            raise ex
    else:
        st.info("Enter Keyword for Search")

# Input Form
with form.form("Enter Keyword"):
    query = st.text_area("Enter your queries (one per line):")
    requested_count = st.number_input("Enter results per Keyphrase", value=50, min_value=1, max_value=300)
    submit = st.form_submit_button("Search", on_click=search_bing, args=(requested_count, ))