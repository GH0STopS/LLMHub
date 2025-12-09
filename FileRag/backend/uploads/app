from dotenv import load_dotenv
import os
import streamlit as st
import requests

load_dotenv()
API_URL  = os.getenv("API_URL")

print(API_URL)

if "is_uploaded" not in st.session_state:
    st.session_state.is_uploaded = False
if "messages" not in st.session_state:
    st.session_state.messages = []
# isUploaded = False
st.set_page_config(page_title="Rag Chat Bot", layout="centered")
st.title("Chat Bot!")
st.header("Type your query here")
# radio = st.radio("Select",["Hi","Hello"])
# if radio=="Hi":
#     st.multiselect("Select",["Hi","Hello","How Are You?"])
upload = st.file_uploader("Choose a file", accept_multiple_files=False)

if upload is not None:
    st.write(f"{upload.name} selected")
    if st.button("Upload"):
        file = {'file':(upload.name, upload, upload.type)}
        try:
            with st.spinner("uploading..."):
                resp = requests.post(f"{API_URL}/uploadFile", files=file)
                if resp.ok:
                    st.success("upload succesful")
                    st.json(resp.json())
                    st.session_state.is_uploaded = True
                else:
                    st.error(f"upload failed with {resp.status_code}")
        except Exception as e:
            st.error(e)


with st.expander("Chat"):
    user_input = st.chat_input("Type your question here...")
    if user_input:
    
        payload = {"query": user_input}
        try:
            with st.spinner("Thinking..."):
                resp = requests.post(f"{API_URL.rstrip('/')}/query", json=payload)
            if resp.ok:
                data = resp.json()
                answer = data.get("response") or data.get("answer") or data
                st.session_state.messages.append(("user", user_input))
                st.session_state.messages.append(("assistant", str(answer)))
            else:
                st.error(f"Query failed: {resp.status_code} {resp.text}")
        except requests.RequestException as e:
            st.error(f"Network error during query: {e}")
    
    for role, messages in st.session_state.messages:
        if role == "user":
            st.chat_message("user").write(messages)
        elif role == "assistant":
            st.chat_message("ai").write(messages)

# if isUploaded:
#     if st.button("Functions"):
#         try:
#             with st.spinner("Loading..."):
#                 resp = requests.get(f"{API_URL}/function")
#                 if resp.ok:
#                     st.success(resp.json().response)
#                 else:
#                     st.error(resp.status_code)
#         except Exception as e:
#             st.error(e)
#     if st.button("Classes"):
#         with st.spinner("Loading..."):
#             resp = requests.get(f"{API_URL}/class")
#             if resp.ok:
#                 st.success(resp.json().response)
#             else:
#                 st.error(resp.status_code)
#     if st.button("Imports"):
#         with st.spinner("Loading..."):
#             resp = requests.get(f"{API_URL}/import")
#             if resp.ok:
#                 st.success(resp.json().response)
#             else:
#                 st.error(resp.status_code)
#     if st.button("Auth Flow"):
#         with st.spinner("Loading..."):
#             resp = requests.get(f"{API_URL}/authFlow")
#             if resp.ok:
#                 st.success(resp.json().response)
#             else:
#                 st.error(resp.status_code)

#     if st.button("Code Smell"):
#         with st.spinner("Loading..."):
#             resp = requests.get(f"{API_URL}/codeSmell")
#             if resp.ok:
#                 st.success(resp.json().response)
#             else:
#                 st.error(resp.status_code)

def call_simple_get(path: str):
    try:
        with st.spinner("Loading..."):
            resp = requests.get(f"{API_URL.rstrip('/')}/{path}")
        if resp.ok:
            json_data = resp.json()
            
            val = json_data.get("response")
            st.success(val)
        else:
            st.error(f"Request failed: {resp.status_code} {resp.text}")
    except requests.RequestException as e:
        st.error(f"Network error: {e}")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Functions", disabled=not st.session_state.is_uploaded):
        call_simple_get("function")
with col2:
    if st.button("Classes", disabled=not st.session_state.is_uploaded):
        call_simple_get("class")
with col3:
    if st.button("Imports", disabled=not st.session_state.is_uploaded):
        call_simple_get("imports")

col4, col5 = st.columns(2)
with col4:
    if st.button("Auth Flow", disabled=not st.session_state.is_uploaded):
        call_simple_get("authFlow")
with col5:
    if st.button("Code Smell", disabled=not st.session_state.is_uploaded):
        call_simple_get("codeSmell")
