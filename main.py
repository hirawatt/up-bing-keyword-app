import streamlit as st
import requests
import base64
import pandas as pd
import json
import dicttoxml

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

form = st.empty()

# Functions
def edit_data(response):
    df = pd.DataFrame(response.json()["webPages"]["value"])
    #df.insert(0, column="select", value="st.selectbox")
    edited_df = st.experimental_data_editor(df)
    return edited_df

def search_bing():
    if query != "":
        # Construct a request
        mkt = 'en-US'
        params = { 'q': query, 'mkt': mkt , 'count': 50}
        headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

        # Call the API
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            progress_text = "Operation in progress. Please wait."
            spinner = st.spinner(text=progress_text)

            #st.subheader("\nHeaders:\n")
            #st.write(response.headers)
            #st.subheader("\nJSON Response:\n")
            #st.json(response.json(), expanded=False)
            
            global xml
            xml = dicttoxml.dicttoxml(response.json(), return_bytes=False)
            st.write("XML Response for `{}`:".format(query))

            st.download_button(
                label="Download XML File",
                data=xml,
                file_name="{}_data.xml".format(query),
                mime="text/plain"
            )
            edited_df = edit_data(response)
            
            #b64 = base64.b64encode
            #html_download = '<a href="data:text/plain;base64;{}" download="{}_data.xml">Download XML File</a>'.format(b64, query)
            #st.markdown(html_download, unsafe_allow_html=True)
            return xml, query
        except Exception as ex:
            raise ex
    else:
        st.info("Enter Keyword for Search")

# Query term(s) to search for
with form.form("Enter Keyword"):
    query = st.text_input("Enter Keyword for Search", value="")
    submit = st.form_submit_button("Submit", on_click=search_bing)