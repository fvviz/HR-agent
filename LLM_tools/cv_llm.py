import os
from langchain.chains import LLMChain, SequentialChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from os.path import join, dirname
from dotenv import load_dotenv
from langchain.output_parsers import StructuredOutputParser, ResponseSchema



import PyPDF2


import os

os.environ["MLFLOW_TRACKING_URI"] = "http://127.0.0.1:8070"
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text



dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class CvLLM:
     def __init__(self, job_title, job_description, pdf_content) -> None:
          self.job_title = job_title
          self.job_description = job_description
          self.llm = ChatOpenAI(model='gpt-4', temperature=0.4, openai_api_key=OPENAI_API_KEY)
          self.cv =  pdf_content
    
     def construct_chain(self):
          response_schemas = [
          ResponseSchema(name="score", description="Score of the CV which is a number between 0 and 100")
          ]
          self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
          response_format = self.output_parser.get_format_instructions()
          prompt= PromptTemplate(
               input_variables=["job_title", "job_description"],
               partial_variables={"response_format": response_format},
               template = """
          You work as a HR in a particular company.
          Given an applicants CV and a descripiton of the job, your job is to  score the applicant on how well they are suited for the job

          The details are as follows:

          Job title: {job_title}
          Job Description: {job_description}

          CV:
          {cv}

          {response_format}
          """
          )

          chain = LLMChain(llm=self.llm, prompt = prompt, output_key="score")
          return chain
    
     
     def get_output(self):
          chain= self.construct_chain()
          output = chain.run(job_title=self.job_title, 
                             job_description=self.job_description,
                             cv=self.cv)
          parsed_output = self.output_parser.parse(output)
          return parsed_output
     
    




          