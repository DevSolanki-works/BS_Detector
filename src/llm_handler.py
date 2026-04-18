# src/llm_handler.py
# ─────────────────────────────────────────────────────────────────────────────
# Wraps the Ollama + LangChain pipeline so app.py stays clean.
# ─────────────────────────────────────────────────────────────────────────────

import json
import re
import subprocess
from typing import Optional

from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from src.prompts import LEGAL_ANALYSIS_SYSTEM_PROMPT, LEGAL_ANALYSIS_USER_TEMPLATE


# ── Supported local models (shown in the Streamlit sidebar) ───────────────────
SUPPORTED_MODELS = {
    "llama3:8b":       "Llama 3 8B  · Fast, great for most contracts",
    "llama3:70b":      "Llama 3 70B · Slower but most accurate",
    "mistral:7b":      "Mistral 7B  · Very fast, good accuracy",
    "gemma2:9b":       "Gemma 2 9B  · Balanced speed/quality",
    "phi3:mini":       "Phi-3 Mini  · Lightest, best for low-RAM machines",
}


def get_available_models() -> list[str]:
    """Ask Ollama which models are actually downloaded on this machine."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split("\n")[1:]   # skip header row
        available = []
        for line in lines:
            parts = line.split()
            if parts:
                model_name = parts[0]
                # keep only models we explicitly support
                if model_name in SUPPORTED_MODELS:
                    available.append(model_name)
        return available if available else list(SUPPORTED_MODELS.keys())[:1]
    except Exception:
        return ["llama3:8b"]   # safe fallback


def build_chain(model_name: str, temperature: float = 0.1):
    """
    Build the LangChain pipeline.
    Low temperature = more deterministic / consistent JSON output.
    """
    llm = OllamaLLM(
        model=model_name,
        temperature=temperature,
        # Request JSON mode when Ollama/model supports it
        format="json",
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(LEGAL_ANALYSIS_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(LEGAL_ANALYSIS_USER_TEMPLATE),
    ])

    return prompt | llm


def parse_llm_output(raw: str) -> dict:
    """
    Robustly extract a JSON object from the LLM response.
    Models sometimes wrap output in ```json … ``` fences even when told not to.
    """
    # Strip markdown fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    # Find the first { … } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    return json.loads(cleaned)


def analyse_contract(contract_text: str, model_name: str = "llama3:8b") -> Optional[dict]:
    """
    Main entry point called by app.py.
    Returns a parsed dict on success, or raises an exception on failure.
    """
    if not contract_text.strip():
        raise ValueError("Contract text cannot be empty.")

    chain = build_chain(model_name)
    raw_output = chain.invoke({"contract_text": contract_text})
    return parse_llm_output(raw_output)
