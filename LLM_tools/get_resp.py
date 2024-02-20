from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import gdown
import json
import os
from LLM_tools.cv_llm import CvLLM, read_pdf

SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage("token.json")
creds = None
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
  creds = tools.run_flow(flow, store)
service = discovery.build(
    "forms",
    "v1",
    http=creds.authorize(Http()),
    discoveryServiceUrl=DISCOVERY_DOC,
    static_discovery=False,
)

json_file = "form_run.json"

with open(json_file, 'r') as f:
  form_data = json.load(f)

form_id = form_data['formId']
cv_link_qid = ''
email_qid = ''

for item in form_data['items']:
  if item['title']== 'CV link(pdf)':
    cv_link_qid = item['questionItem']['question']['questionId']
  elif item['title']== 'Email Address':
    email_qid = item['questionItem']['question']['questionId']

result = service.forms().responses().list(formId=form_id).execute()
job_title = form_data['info']['title']
job_description = form_data['info']['description']



def get_user_deets():
  output = []
  for resp_num, response in enumerate(result['responses']):
    
    answers = response['answers']
    cv_link = answers[cv_link_qid]
    email = answers[email_qid]

    cv_link = cv_link['textAnswers']['answers'][0]['value']
    email = email['textAnswers']['answers'][0]['value']

    pdf_down_path = os.path.join('temp', f'cv{resp_num}.pdf')
    gdown.download(cv_link, pdf_down_path, fuzzy=True, quiet=False )

    pdf_content = read_pdf(pdf_down_path)
    cvllm = CvLLM(job_title, job_description, pdf_content)

    score = cvllm.get_output()['score']

    out =  [email, int(score)]
    output.append(out)
  sorted_list = sorted(output, key=lambda x: x[1], reverse=True)
  return sorted_list













  