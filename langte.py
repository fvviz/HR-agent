
from os.path import join, dirname
from dotenv import load_dotenv
from langchain_openai import OpenAI

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.graphs import NeptuneGraph
import os


from langchain.chains import NeptuneOpenCypherQAChain
from langchain_openai import ChatOpenAI


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")





host = "db-neptune-1.cluster-ct8uogykkkg0.ap-southeast-2.neptune.amazonaws.com"
port = 8182
use_https = True

graph = NeptuneGraph(host=host, port=port, use_https=use_https)

llm = ChatOpenAI(temperature=0, model="gpt-4", openai_api_key=OPENAI_API_KEY)

chain = NeptuneOpenCypherQAChain.from_llm(llm=llm, graph=graph)

chain.run("how many outgoing routes does the Austin airport have?")