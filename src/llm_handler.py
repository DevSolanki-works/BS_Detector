# src/llm_handler.py  ── Cloud version (Groq API)

import json
import re
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.prompts import LEGAL_ANALYSIS_SYSTEM_PROMPT, LEGAL_ANALYSIS_USER_TEMPLATE

# ── Current active Groq models (updated April 2026) ───────────────────────────
SUPPORTED_MODELS = {
    "llama-3.1-8b-instant":    "Llama 3.1 8B  · Fastest · Best for demos",
    "llama-3.3-70b-versatile": "Llama 3.3 70B · Most accurate",
    "mixtral-8x7b-32768":      "Mixtral 8x7B  · Great for long contracts",
    "gemma2-9b-it":            "Gemma 2 9B    · Balanced speed/quality",
}

def get_available_models() -> list[str]:
    return list(SUPPORTED_MODELS.keys())

def get_model_label(model_name: str) -> str:
    return SUPPORTED_MODELS.get(model_name, model_name)

def build_chain(model_name: str, api_key: str, temperature: float = 0.1):
    llm = ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=temperature,
    )
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(LEGAL_ANALYSIS_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(LEGAL_ANALYSIS_USER_TEMPLATE),
    ])
    return prompt | llm

def parse_llm_output(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)

def analyse_contract(contract_text: str, model_name: str = "llama-3.1-8b-instant", api_key: str = "") -> Optional[dict]:
    if not contract_text.strip():
        raise ValueError("Contract text cannot be empty.")
    if not api_key:
        raise ValueError("Groq API key is missing.")
    chain = build_chain(model_name, api_key, temperature=0.1)
    response = chain.invoke({"contract_text": contract_text})
    raw = response.content if hasattr(response, "content") else str(response)
    return parse_llm_output(raw)