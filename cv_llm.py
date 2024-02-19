from langchain.chains import LLMChain, SequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


import json
import os
from os.path import join, dirname
from dotenv import load_dotenv
import asyncio

import requests
from io import BytesIO


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    
class BaseCVLLM:
    def __init__(self, cv, job_title,
                  job_description, pdf_path, json_path='cv_elements.json') -> None:
        self.cv = cv
        self.job_title = job_title
        self.job_description = job_description
        self.llm = OpenAI(temperature=0.6, max_tokens=-1, 
                          openai_api_key=OPENAI_API_KEY)
        
        loader = UnstructuredPDFLoader(pdf_path)
        self.pdf_data = loader.load()

        with open(json_path) as elements_file:
               self.elements = json.load(elements_file)

    async def async_generate(self, sqc, inputs):
          resp = await sqc.arun(inputs)
          return resp
    
    async def build_dict(self):
          prompt1 = """
          Given a CV for the Job title: {job_title},
          Analayse the CV and identify the follwing component:
        
         {field}: {field_info}

          Scan the CV for the presence of this field, Identify the segment.
          ONLY Return a json formatted string where the property name is {field} and value is the identied segment
          If you cannot identify the segment, The value of the property should be null.
          -----
          CV:
          {cv}
          -----
          """

          prompt1_template = PromptTemplate(
               input_variables=["job_title" ,"cv", "field", "field_info"],
               template= prompt1
          )

          chain1 = LLMChain(llm = self.llm, prompt=prompt1_template, 
                            output_key="dictionary"
                        )
          
          dict_chain = SequentialChain(
               chains = [chain1],
               input_variables = ["job_title", "cv", "field", "field_info"],
               output_variables = ["dictionary"],
               verbose = False
          )
          
          tasks = []
          for field in self.elements.keys():
               field_info = self.elements[field]
               inputs = {
               "job_title": self.job_title,
               "field": field,
               "field_info": field_info,
               "cv": self.cv
               }

               tasks.append(self.async_generate(dict_chain, inputs))
          results = await asyncio.gather(*tasks)

          elements_dict = {}
          
          for json_stuff in results:
               temp_ = json.loads(json_stuff)
               name_ = list(temp_.keys())[0]
               
               elements_dict[name_] = temp_[name_]
          print(elements_dict)
    
    async def generate_concurrently(self):
          pt = PromptTemplate(
               input_variables=["job_title", "field", "field_info", "field_val", "job_description"],
               template = """
              Your team is evaluating CVs. Your job is to evaluate the {field} in a given CV.
              See how well the provided {field} in this CV in this field is applicable for the job title {job_title}.
              
              The job description of this post will also be provided to you, Use it as a reference to score the provided field: {field}

              Based on this, Score the {field} out of 10. 
              DO NOT BE LENIENT with the scoring, You are free to give a low score if you feel like the provided {field} is not good.
              If the field has been listed as null, give the score as 0
              You are allowed to use decimal values, Return ONLY THE SCORE AND NO OTHER TEXT.

              {field} = {field_info}. 
              ---
              Job description:
              {job_description}
              ---
              This is what has been provided in the applicants CV:

              {field}:

              {field_val}
              ---         
          """
          )
          chain = LLMChain(llm = self.llm,
                           prompt=pt,
                           output_key="score")
          
          sqc = SequentialChain(
               chains = [chain],
               input_variables = ["job_title", "field", "field_info", "field_val", "job_description"],
               output_variables = ["score"],
               verbose = False
          )

          elements_dict = await self.build_dict() 
          tasks = []

          for field in elements_dict.keys():
               field_info = self.elements[field]
               field_val = elements_dict[field]
               inputs = {
               "job_title": self.job_title,
               "field": field,
               "field_info": field_info,
               "field_val": field_val,
               "job_description": self.job_description
               }

               tasks.append(self.async_generate(sqc, inputs))

          results = await asyncio.gather(*tasks)
          results  = [float(i) for  i in results]
          element_wise_score = {}
          
          for score, element in zip(results,elements_dict.keys()):
              element_wise_score[element] = score

          sum_score = sum(results)
          return  sum_score, elements_dict, element_wise_score

class CVranker:
     def __init__(self, cv_links_list: list, job_title: str, job_description: str) -> None:
          self.cvs = [read_pdf(link) for link in cv_links_list]
          self.job_title = job_title,
          self.job_description = job_description 
          self.review_llm = OpenAI(temperature=0.6, openai_api_key=OPENAI_API_KEY)

     def sort_func(self, cvs):
          return cvs['score']
     
     def build_review_llm(self):
          pt = PromptTemplate(
               input_variables=["cv"],
               template = """
                Summarise the CV in a short, clear and concise way. Make sure to retain all the important elements of the CV.
                DO NOT MAKE UP ANY INFORMATION. ONLY USE THE INFORMATION PROVIDED IN THE CV BELOW.
                ---
                CV:
                {cv}        
                ---
                Return ONLY the short summarized CV.
                """
          )

          llmchain = LLMChain(llm = self.review_llm,
                              prompt=pt,
                              output_key="review")
          
          review_llm = SequentialChain(
               chains = [llmchain],
               input_variables=["cv"],
               output_variables=["review"],
               verbose = False
          )

          return review_llm

     async def async_generate_scores(self, cv_llm):
          score, elements_dict = await cv_llm.generate_concurrently()
          return score, elements_dict['Contact Information']
     
     async def async_generate_reviews(self, review_llm, inputs):
          resp = await review_llm.arun(inputs)
          return resp

     async def generate_rankings(self):
          review_tasks = []
          scores_contacts = []
          if self.cvs:
               for cv in self.cvs:  # Changed from self.cv to self.cvs
                    cv_score_llm = BaseCVLLM(job_title=self.job_title,
                                             job_description=self.job_description,
                                             cv=cv)
                    review_llm = self.build_review_llm()
                    score, elem_dict, element_wise_score= await cv_score_llm.generate_concurrently()

                    scores_contacts.append((score, elem_dict['Contact Information'], element_wise_score))
                    review_tasks.append(self.async_generate_reviews(review_llm,
                                                                      {"cv": cv}))
          else:
               print(self.cvs, "no cv")

          summaries = await asyncio.gather(*review_tasks)

          cv_rankings = []
          for num, result in enumerate(scores_contacts):
               cv_info = {}
               cv_info['score'] = result[0]
               cv_info['contact_info'] = result[1]
               cv_info['element_wise_score'] = result[2]
               cv_info['short_summary'] = summaries[num]
               cv_rankings.append(cv_info)

          cv_rankings.sort(key=self.sort_func, reverse=True)
          return cv_rankings
