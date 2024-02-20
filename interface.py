import streamlit as st
from LLM_tools.job_llm import JobDescLLM
from LLM_tools.gen_form import make_form
from mailing import send_email
from LLM_tools.get_resp import get_user_deets
import pandas as pd

st.set_page_config(
    page_title="Demo-Interface v0.0",
    layout='wide'
)

def deploy(job_title, job_purpose, ed_qual, skill_qual, loc, comp):
    print("Deploying Agent.....")
    job_desc_llm = JobDescLLM(job_title, job_purpose, ed_qual, skill_qual, loc, comp)
    desc = job_desc_llm.get_job_desc()
    forms_link = make_form(job_title, desc, 'form_run.json')

    with open('possible_candidates.txt','r') as f:
        candidates = f.readlines()

    for candidate in candidates:
        print("Mailing to Candidate:", candidate)
        send_email(candidate, f"We are recruiting for: {job_title}", desc+'\n'+'Apply now using:'+forms_link)




st.write("Job Posting Agent Interface")
create,results=st.tabs(['Create post','View results'])

with create:
    job_title=st.text_input("Enter job title")
    job_purpose=st.text_input("Enter job purpose")
    ed_qual=st.text_input("Enter educational qualifications")
    skill_qual=st.text_input("Enter required skills")
    loc=st.text_input("Enter job location")
    comp=st.text_input("Enter salary")


    review=st.button("Deploy")
    if review: 
        deploy(job_title, job_purpose, ed_qual, skill_qual, loc, comp)
with results:
    out = st.table(data=get_user_deets())




