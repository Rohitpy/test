import time
import json
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain_core.language_models.llms import BaseLLM
from langchain_core.pydantic_v1 import root_validator
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import Generation, LLMResult
import requests

class Gemma3LLM(BaseLLM):
    def __init__(self):
        super(Gemma3LLM, self).__init__()
        self.callbacks = None
        self.verbose = False
        self.tags = None
        self.metadata = None
        self.cache = None

    @property
    def _default_params(self) -> Dict[str, Any]:
        return {}

    @root_validator(allow_reuse=True)
    def validate_environment(cls, values: Dict) -> Dict:
        return {}

    @property
    def _llm_type(self) -> str:
        return "vllm"

    def _generate(
        self,
        prompts: List[str],
        params: dict = {'temperature': 0.0, 'top_p': 1.0, 'max_tokens': 40000,
                        'skip_special_tokens': True, 'stop': ['Note', 'Please'], 'frequency_penalty': -1},
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        response = requests.post(
            "http://173.1.125.212:8503/gemma3_generate",
            json={
                "prompt": prompts,
                "kwargs": params
            },
        )
        outputs = response.json()
        generations = []
        for output in outputs:
            text = output['outputs'][0]['text']
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

app = FastAPI(title="DDL Statement Generator", description="Generates DDL statements from user input")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = Gemma3LLM()

# DDL generation prompt template
DDL_TEMPLATE = """<bos><start_of_turn>system
You are an expert in database design and DDL (Data Definition Language) statements. 
Your task is to generate accurate and optimized DDL statements (CREATE TABLE, ALTER TABLE, etc.) based on the user's requirements.

User requirements:
{user_input}

Respond only with the DDL statement. Do not provide any comments or explanations.
<end_of_turn>
<start_of_turn>user
Please generate the DDL statement for the above requirements.
<end_of_turn>
<start_of_turn>model\n\n"""

class DDLRequest(BaseModel):
    user_input: str

class DDLResponse(BaseModel):
    ddl_statement: str
    execution_time: float

def generate_ddl(user_input: str) -> str:
    """Generate DDL statement using LLM"""
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=DDL_TEMPLATE
    )

    ddl_chain = LLMChain(
        llm=llm,
        prompt=prompt,
    )

    result = ddl_chain.invoke({"user_input": user_input})
    return result.get("text", "").strip()

@app.post("/generate_ddl", response_model=DDLResponse)
async def generate_ddl_endpoint(request: DDLRequest):
    """Generate DDL statement from user input"""
    start_time = time.time()
    try:
        ddl_statement = generate_ddl(request.user_input)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during DDL generation: {str(e)}"
        )
    end_time = time.time()
    return DDLResponse(
        ddl_statement=ddl_statement,
        execution_time=end_time - start_time
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DDL Statement Generator",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7002)
