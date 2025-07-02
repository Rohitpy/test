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

Type here to search
