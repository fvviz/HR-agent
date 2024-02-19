import streamlit as st

st.set_page_config(
    page_title="Demo-Interface v0.0",
    layout='wide'
)

st.write("Demo Interface v0.0")



create,results=st.tabs(['Create post','View results'])

with create:
    job_title=st.text_input("Enter job title")
    job_description=st.text_input("Enter job purpose")
    ed_qual=st.text_input("Enter educational qualifications")
    skill_qual=st.text_input("Enter required skills")
    loc=st.text_input("Enter job location")
    comp=st.text_input("Enter salary")


    review=st.button("Deploy")


