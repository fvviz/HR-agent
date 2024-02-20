from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import json

import json

def save_dict_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)



SCOPES = "https://www.googleapis.com/auth/drive"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage("token.json")
creds = None
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
  creds = tools.run_flow(flow, store)

form_service = discovery.build(
    "forms",
    "v1",
    http=creds.authorize(Http()),
    discoveryServiceUrl=DISCOVERY_DOC,
    static_discovery=False,
)


def make_form(job_title, description, json_save_path):
    NEW_FORM = {
        "info": {
            "title": f"{job_title} Application"
        }
    }


    update = {
    "requests": [
        {
            "updateFormInfo": {
                "info": {
                    "description": (
                        description
                    )
                },
                "updateMask": "description",
            }
        }
    ]
}   
    
    

    # Request body to add a multiple-choice question
    NEW_QUESTION = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": (
                            "First name"
                        ),
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                },
                            }
                        },
                        
                    },
                    "location": {"index": 0},
                }
            }
        ]
    }


    Q2 = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": (
                            "Last name"
                        ),
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                },
                            }
                        },
                        
                    },
                    "location": {"index": 0},
                }
            }
        ]
    }

    Q3 = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": (
                            "Email Address"
                        ),
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                },
                            }
                        },
                        
                    },
                    "location": {"index": 0},
                }
            }
        ]
    }

    Q4 = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": (
                            "Email Address"
                        ),
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                },
                            }
                        },
                        
                    },
                    "location": {"index": 0},
                }
            }
        ]
    }


    Q5 = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": (
                            "CV link(pdf)"
                        ),
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                },
                            }
                        },
                        
                    },
                    "location": {"index": 0},
                }
            }
        ]
    }


    result = form_service.forms().create(body=NEW_FORM).execute()

    question_setting = (
    form_service.forms()
    .batchUpdate(formId=result["formId"], body=update)
    .execute()
   )

    question_setting = (
        form_service.forms()
        .batchUpdate(formId=result["formId"], body=NEW_QUESTION)
        
        .execute()
    )

    question_setting = (
        form_service.forms()
        .batchUpdate(formId=result["formId"], body=Q2)
        
        .execute()
    )

    question_setting = (
        form_service.forms()
        .batchUpdate(formId=result["formId"], body=Q3)
        
        .execute()
    )

    question_setting = (
        form_service.forms()
        .batchUpdate(formId=result["formId"], body=Q5)
        
        .execute()
    )
    get_result = form_service.forms().get(formId=result["formId"]).execute()
    save_dict_to_json(get_result, json_save_path)
    return get_result['responderUri']
