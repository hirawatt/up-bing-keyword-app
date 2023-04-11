import streamlit as st
import requests
import base64
import pandas as pd
import json
import uuid
import xml.etree.ElementTree as ET

# credentials
page_title = st.secrets['initialize']['page_title']
sidebar_title = st.secrets['initialize']['sidebar_title']

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = st.secrets['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = st.secrets['BING_SEARCH_V7_ENDPOINT']

logo_file = '💰'

# streamlit
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
            progress_text = "Operation in progress. Please wait."

            #st.subheader("\nHeaders:\n")
            #st.write(response.headers)
            #st.subheader("\nJSON Response:\n")
            #st.json(response.json(), expanded=False)
            
            urls = modify_data(response).tolist()
            # Create XML Document

            # Create the root element for the sitemap
            urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

            # Add URLs to the sitemap
            for url in urls:
                # Create a url element for each URL
                url_element = ET.SubElement(urlset, "url")
                # Create a loc element and set its text to the URL
                loc_element = ET.SubElement(url_element, "loc")
                loc_element.text = url

            # Generate the XML sitemap
            sitemap_xml = ET.tostring(urlset, encoding="unicode", method="xml")

            # Print the XML sitemap
            st.write(sitemap_xml)

            # Save the XML sitemap to a file
            with open("sitemap.xml", "w") as file:
                file.write(sitemap_xml)

            st.write("XML Response for `{}`:".format(query))

            st.download_button(
                label="Download XML File",
                data=sitemap_xml,
                file_name="{}_data.xml".format(query),
                mime="application/xml"
            )
            
            return sitemap_xml, query
        except Exception as ex:
            raise ex
    else:
        st.info("Enter Keyword for Search")

# Input Form
with form.form("Enter Keyword"):
    query = st.text_area("Enter Keyword for Search", value="")
    results_per_keyphrase = st.number_input("Enter results per Keyphrase", value=50, min_value=1, max_value=300)
    submit = st.form_submit_button("Submit", on_click=search_bing, args=(results_per_keyphrase, ))

x = uuid.uuid4().hex
#st.write(str(x))

'''
filename = "data/python_data.xml"
with open(filename, "rb") as xml_file:
    #st.write(xml_file.read().decode('UTF-8'))
    b64 = base64.b64encode(xml_file.read()).decode()
href = '<a href="data:application/xml;base64;{}" download="{}_data.xml">Download XML File</a> (right-click and save as &lt;some_name&gt;.csv)'.format(b64, query)
st.markdown(href, unsafe_allow_html=True)
'''