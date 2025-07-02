import time import json
from typing import Optional, Dict, Any, List, Tuple from fastapi import FastAPI, HTTPException, Query from fastapi.middleware.cors import CORSMiddleware from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate from langchain.chains import LLMChain
from langchain_core. language_models.1lms import BaseLLM from langchain _core-pydantic_vl import root_validator
from langchain_core.callbacks.manager import CallbackManagerForLLMRun from langchain_core.outputs import Generation,LLMResult import requests
class Gemma3LLM(BaseLLM) :|
def
_init (self) :
super (GemmaLLM, self)•_init_()
self.callbacks = None
self.verbose = False
self.tags = None
self.metadata = None
self.cache = None
@property
def _default_params (self) -› Dict[str, Any]:
return t)
@root_validator (allow_reuse-True)
def validate_environment(cls, values: Dict) -› Dict:
return t
@property def
_11m_type(self) -> str:
return "vilm"

def generate( self, prompts: List[strl,
params: dict = {'temperature': 0.0, 'top_p': 1.0, "max_tokens': 1024,
* skip_special_tokens*: True,
'stop': ['Note', 'Please'], 'frequency_penalty': 1.4},
stop: Optional[List[str]] = None,
run_manager: Optional [CallbackManagerForLLMRun] = None,
**kwargs: Any,
) -> LLMResult:
response = requests. post
"http://173.1.125.212:8503/gemma3_generate*, j son=t
"prompt": prompts,
"kwargs": params
outputs = response. json)
generations = []
for output in outputs:
text = output [' outputs '][0]['text']
generations .append([Generation(text=text)])
return LLMResult (generations=generations)
app = FastAPI(title="SAS to Teradata SQL Converter", description="Converts SAS code to Teradata SQL")


