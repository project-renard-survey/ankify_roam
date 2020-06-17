import json 
import urllib.request 
import logging
import traceback
import re

logger = logging.getLogger(__name__)

def _create_request_dict(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def _invoke(action, **params):
    requestDict = _create_request_dict(action, **params)
    requestJson = json.dumps(requestDict).encode('utf-8')
    request = urllib.request.Request('http://localhost:8765', requestJson)
    response = json.load(urllib.request.urlopen(request))
    if len(response) != 2:
        raise BadResponse(response, 'response has an unexpected number of fields')
    if 'error' not in response:
        raise BadResponse(response, 'response is missing required error field')
    if 'result' not in response:
        raise BadResponse(response, 'response is missing required result field')
    if response['error'] is not None:
        if response['error'].startswith('model was not found'):
            raise ModelNotFoundError(response['error'])
        elif "cannot create note because it is a duplicate" in response['error']:
            raise DuplicateError(response['error'])
        else:
            raise GenericResponseError(response['error'])
    return response['result']

def upload_all(anki_dicts):
    for anki_dict in anki_dicts:
        upload(anki_dict)

def upload(anki_dict):
    note_id = _get_note_id(anki_dict)
    try:
        if note_id:
            return _update_note(note_id, anki_dict)
        else:
            return _add_note(anki_dict)
    except Exception as e:
        logger.error(f"Encountered the error while uploading uid='{anki_dict['fields']['uid']}'")
        logger.debug(e, exc_info=1)
            
def _add_note(anki_dict):
    return _invoke("addNote", note=anki_dict)

def _update_note(note_id, anki_dict):
    note = {"id":note_id, "fields": anki_dict["fields"]}
    return _invoke("updateNoteFields", note=note)

def get_field_names(note_type):
    return _invoke('modelFieldNames', modelName=note_type)

def _get_note_id(anki_dict):
    res = _invoke('findNotes', query=f"uid:{anki_dict['fields']['uid']}")
    if res:
        return res[0]
    return None

def get_model_names():
    return _invoke("modelNames")

def create_model(model):
    return _invoke("createModel", **model) 

def update_model(model):
    model_template_update = {
        "name": model["modelName"],
        "templates": {t["Name"]: {"Front":t["Front"], "Back":["Back"]} 
                      for t in model["cardTemplates"]}
    }
    res_template = _invoke("updateModelTemplates", model=model_template_update)
    model_styling_update = {
        "name": model["modelName"],
        "css": model["css"]
    }
    res_styling = _invoke("updateModelStyling", model=model_styling_update)
    return [res_template, res_styling]

def load_profile(name):
    return _invoke("loadProfile", name=name)

def create_deck(name):
    return _invoke("createDeck", deck=name)

def delete_deck(name, cards_too=True):
    return _invoke("deleteDecks", decks=[name], cardsToo=cards_too)

class AnkiConnectException(Exception):
    """Base class for exceptions in this module."""
    pass

class BadResponse(AnkiConnectException):
    def __init__(self, response, message):
        self.response = response
        self.message = message

class GenericResponseError(AnkiConnectException):
    def __init__(self, response_error):
        self.response_error = response_error

class ModelNotFoundError(AnkiConnectException):
    def __init__(self, response_error):
        self.response_error = response_error

class DuplicateError(AnkiConnectException):
    def __init__(self, response_error):
        self.response_error = response_error
