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
turn>
<start_of_turn›user
Please convert the SAS code to equivalent Teradata SQL code.
Kend_of turn>
< start_of_turn>model\n\n***
# Request and response models
class ConversionRequest (BaseModel) :
sas_code:
str
additional instructions: str = **
explain: bool = False
include_warnings: bool - True
class ConversionWarning (BaseModel):
severity: str
# 'High', 'Medium',
message: str
line_number: Optionallint] = None
suggestion: Optional(str] = None
" Low'
class ConversionResponse(BaseModel) :
sql code:
str
explanation: Optional[str] = None
warnings: Optional[List[ConversionWarning]] - None execution_time: float
dialect: str = "SQL"
EXPLANATION TEMPLATE - **'‹bos><start_of_turn›system
You are an expert in SAS and Teradata SQL. A user has requested an explanation of how SAS code was converted to Teradata SQL.
SAS code:
'''sas
(sas_code)
'''
SOL code:
'''sql
{sql_code}
'''
Provide a clear explanation of how the SAS code was converted to SQL, highlighting:
1. How procedural SAS logic was converted to set-based SQL operations
2. How SAS functions were mapped to Teradata SQL functions
3. How SAS-specific features were handled in Teradata SOL
4. Any optimizations that were used in the Teradata SQL code
5. Potential performance considerations
6. Any limitations or differences in behavior between the original SAS code and the Teradata SQL
Focus on explaining the conversion decisions and reasoning rather than just describing the code.
‹end_of_turn>
< start_of_turn›user
Please explain how the SAS code was converted to Teradata SQL code.
‹end_of_turn>
«start_of_turn›model\n\n****
# Warning detection template
WARNING_TEMPLATE = "*'<bos><start_of_turn›system
You are an expert in SAS and Teradata SQL conversion.
Analyze this SAS code and identify elements that may be challenging to convert accurately to Teradata SQL:
sas
(sas_code}
Return a JSON array with each potential issue containing:
"severity": string ("High",
"Medium"
, or "Low")
"line": number (approximate line number) or null if not applicable
"message": string (clear explanation of the issue)
"suggestion": string (constructive suggestion for addressing the issue)
Focus on identifying conversion challenges:
- Complex procedural logic that needs set-based alternatives
- SAS-specific functions without direct Teradata SQL equivalents
- Macro processing challenges in an Teradata SQL context
- BY-group processing that needs to be converted to window functions
- RETAIN statements that need alternatives in Teradata SQL
- Format/informat usage that requires special handling in Teradata SQL
- Potential data type differences between SAS and Teradata SQL
Format your entire response as valid JSON only. <end_of_turn>
< start_of_turn›user
Identify potential conversion issues in this SAS code for Teradata SQL.
‹end_of_turn›
‹start_of_turn>model\n\n**"
def identify_conversion warnings(sas_code: str) -> List[ConversionWarning]:
"*"Identify potential conversion issues using LLM"™™
prompt = PromptTemplate(
input_variables=["sas_code"],
template=WARNING_TEMPLATE
)
warning_chain - LLMChain(
11m-11m, prompt-prompt,
try:
result - warning_chain. invoke({"sas_code": sas_code})
warnings_text = result-get ("text", "[]"). strip()
try:
warnings_data = json.loads (warnings_text)
warnings = [1
for w in warnings _data:
warnings.append (ConversionWarning(
severity=w-get ("severity", "Medium"'), message-w-get ("message"
"Unspecified issue"),
line_number=w. get("line"), suggestion-w. get ("suggestion")
return warnings
except json.JSONDecodeError:
return [ConversionWarning(
severity="Medium"
message="Could not analyze potential conversion issues. Manual review recommended." suggestion="Review the generated SQL carefully, especially for complex logic and functions."
except Exception as e:
return [ConversionWarning(
severity="Medium"
message=f"Error analyzing conversion issues: {str (e)}"
suggestion-"Proceed with caution and test the generated Teradata SQL thoroughly."
def convert_sas_to_sq](sas_code: str, additional _instructions: str = "') →> str:
**"Convert SAS code to
Teradata SQL using LLM"™"
prompt - PromptTemplate(
input_variables-["sas_code"
', "additional_instructions"],
template-SAS_TO_SQL_TEMPLATE

conversion_chain = LLChain (
1lm=11m, prompt-prompt,

result = conversion_chain. invoke(i
"sas_code": sas_code,
})
"additional_instructions": additional instructions
return result get ("text", "''). strip()
def generate_explanation(sas_code: str, sql_code: str) -> str:
"*'Generate an explanation of the SAS to Teradata SQL conversion""" prompt - PromptTemplate (
input_variables=["sas_code", "sql_code"],
template-EXPLANATION_TEMPLATE

explanation_chain = LLMChain(
12m=12m,
prompt=prompt,

result = explanation_chain.invoke(
{"sas_code": sas_code, "sql_code": sal_code}
return result.get ("text", ""). strip()
@app.post("/convert", response model=ConversionResponse)
async def convert code request: ConversionRequest) :
*"Convert SAS code to Teradata SQL"""
start_time = time. time()
try:
warnings = None
if request. include warnings:
warnings = identify_conversion warnings (request.sas_code)
sql_code = convert_sas_to_sql(
request. sas_code, request. additional _instructions
# Generate explanation if requested
explanation = None
if request. explain:
explanation = generate_explanation (request.sas_code, sql_code)
except Exception as e:
raise HTTPException( status_code=500,
detail=f"Error during conversion: {str(e)}"
end
_time = time. time ()
return ConversionResponse ( sql_code=sql
_code,
explanation=explanation, warnings=warnings,
execution_time=end_time - start_time, dialect="SQL"
)




