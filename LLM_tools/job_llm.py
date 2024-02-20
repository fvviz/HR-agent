import os
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import asyncio
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class JobDescLLM:
     def __init__(self, job_title, job_purpose, educational_qualifications, skill_qualitifications, location, salary, json_file='jd_elements.json') -> None:
          self.job_title = job_title
          self.job_purpose= job_purpose
          self.educational_qualifications = educational_qualifications
          self.skill_qualitifications = skill_qualitifications,
          self.location = location
          self.salary = salary

          self.llm = ChatOpenAI(model='gpt-4', temperature=0.4, openai_api_key=OPENAI_API_KEY)

     def get_chain(self):
          prompt= PromptTemplate(
               input_variables=["job_title", "job_purpose", "educational_qualifications", "location", "salary"],
               template = """
          You work as a HR in a particular company.
          Given certain details about a Job, You are required to provide an accurate job description for this job 

          The details are as follows:

          Job title: {job_title}
          Job purpose: {job_purpose}
          Educational Qualifications: {educational_qualifications}
          Skill qualification: {skill_qualification}
          Location: {location}
          Salary: {salary}
          """
          )

          chain = LLMChain(llm=self.llm, prompt = prompt, output_key="job_description")
          return chain
     

     def get_job_desc(self):
          chain = self.get_chain()
          output = chain.run(job_title=self.job_title, 
                             job_purpose=self.job_purpose, 
                             educational_qualifications= self.educational_qualifications,
                             skill_qualification=self.skill_qualitifications,
                             location= self.location, 
                             salary= self.salary)
          
          return output
          
    

          