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




#Initialize LLM
11m = GemmaBLLM)
# Primary conversion template
SAS_TO_SQL_TEMPLATE = ***<bos><start_of_turn›system
You are an expert in both SAS and Teradata SQL. Your task is to
convert SAS code to equivalent Teradata SQL code.
SAS code:
innsas
isas_code,
Your goal is to create accurate, maintainable Teradata SQL code that preserves the functionality of the original SAS code.
{additional_ instruction}
When translating to Teradata SQL, pay special attention to:
1. Converting procedural SAS logic (especially DATA steps) to set-based SQL operations
2. Using appropriate syntax for window functions
3. Converting SAS functions to Teradata SQL functions
4. Creating temporary tables for intermediate data
5. Converting SAS macros and variables appropriately
6. Implementing appropriate JOIN operations where needed
Include detailed comments in the Teradata SQL code to explain your conversion decisions, especially for complex transformations. ‹ end_of_turn>
‹start_of_turn›user
Please convert the SAS code to equivalent Teradata SOL code.


