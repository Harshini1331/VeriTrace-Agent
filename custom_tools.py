from simple_agent import SimpleFunctionTool as FunctionTool
from mock_data import MOCK_SEARCH_MAPPING
import sys
import io
import hashlib
import json
import os
import glob

# Load demo docs
DEMO_DOCS_PATH = os.path.join(os.path.dirname(__file__), "demo_docs")
DEMO_DOCS = {}

def load_demo_docs():
    """Loads all files from the demo_docs directory."""
    global DEMO_DOCS
    if not os.path.exists(DEMO_DOCS_PATH):
        print(f"WARNING: Demo docs path not found: {DEMO_DOCS_PATH}")
        return

    for filepath in glob.glob(os.path.join(DEMO_DOCS_PATH, "*")):
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    DEMO_DOCS[os.path.basename(filepath)] = f.read()
            except Exception as e:
                print(f"WARNING: Could not read {filepath}: {e}")

# Load on import
load_demo_docs()

def execute_code(code: str) -> str:
    """
    Executes Python code and returns the stdout.
    """
    # Capture stdout
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    try:
        # minimal sandbox
        exec(code, {'__builtins__': __builtins__, 'hashlib': hashlib, 'json': json, 'print': print})
        result = redirected_output.getvalue()
        if not result:
             result = "Code executed successfully but produced no output."
    except Exception as e:
        result = f"Error executing code: {e}"
    finally:
        sys.stdout = old_stdout
    
    return result

CodeExecutionTool = FunctionTool(
    func=execute_code
)

def search_internal_documents(query: str) -> dict:
    """
    Search internal documents for compliance evidence.
    """
    # Keyword search
    
    best_match = None
    
    # 1. Search demo docs
    for doc_name, content in DEMO_DOCS.items():
        if query.lower() in content.lower() or any(term in content.lower() for term in query.lower().split()):
             # Simple keyword match
             best_match = {"id": doc_name, "text": content}
             break

    # 2. Fallback to mock data
    if not best_match: 
        # Try exact match first
        if query in MOCK_SEARCH_MAPPING:
            best_match = MOCK_SEARCH_MAPPING[query]
        else:
            # Try fuzzy match (if query is in key or key is in query)
            for key, value in MOCK_SEARCH_MAPPING.items():
                if query in key or key in query:
                    best_match = value
                    break

    if best_match:
        results = [{
            "document_id": best_match["id"],
            "excerpt": best_match["text"]
        }]
        return {"status": "success", "report": results}
    else:
        # Fallback for an unexpected query
        return {"status": "error", "report": "No direct evidence found for this check in the simulated database."}

InternalDocSearchTool = FunctionTool(
    func=search_internal_documents
)