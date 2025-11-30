from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from simple_agent import SimpleLlmAgent as LlmAgent
from custom_tools import InternalDocSearchTool, CodeExecutionTool
from mock_data import MOCK_POLICY_CHECKS
import json
import csv
from typing import List

class ComplianceVerdict(BaseModel):
    """The structured output for the Verifier Agent's final decision."""
    policy_rule: str = Field(description="The specific compliance rule being checked.")
    document_id: str = Field(description="The ID of the internal document providing the evidence.")
    verdict: str = Field(description="The compliance status: 'COMPLIANT', 'NON-COMPLIANT', or 'NEEDS_REVIEW'.")
    reasoning: str = Field(description="The step-by-step logical argument for the verdict based *only* on the evidence provided.")
    confidence: float = Field(description="A numerical confidence score (0.0 to 1.0) in the verdict.")

class ComplianceCheckList(BaseModel):
    """A list of atomic compliance checks extracted from a policy document."""
    checks: List[str] = Field(description="A list of atomic, verifiable compliance checks extracted from the policy document.")

# Initialize tools
CodeTool = CodeExecutionTool

# Agent Definitions

# Orchestrator Agent
OrchestratorAgent = LlmAgent(
    model='gemini-2.0-flash-exp',
    name="PolicyOrchestrator",
    description="Decomposes a full compliance document into a list of atomic, verifiable compliance checks.",
    instruction="""You are the Policy Orchestrator. Your role is to take a full regulation and output 
    a list of concise, atomic policy checks for the system to process.
    Output MUST be a JSON object with a single field 'checks' which is a list of strings.
    Example: {"checks": ["Check 1", "Check 2"]}"""
)

# Retriever Agent
RetrieverAgent = LlmAgent(
    model='gemini-2.0-flash-exp',
    name="RetrieverAgent",
    description="A specialist in executing the internal document search tool to find relevant evidence quickly.",
    tools=[InternalDocSearchTool],
    instruction="""You are a specialized Retriever Agent. Your ONLY job is to use the 'InternalDocSearchTool' to find evidence.
    1. You MUST call 'InternalDocSearchTool' with the exact query you received.
    2. You MUST NOT hallucinate or make up evidence.
    3. You MUST NOT answer from your own knowledge.
    4. After calling the tool, output the result as a JSON object with 'evidence_text' and 'document_id'.
    5. If the tool returns no evidence, report that."""
)

# Verifier Agent
VerifierAgent = LlmAgent(
    model='gemini-2.0-flash-exp',
    name="ComplianceVerifier",
    description="A legal expert that compares a single policy rule against retrieved evidence and outputs a structured, auditable verdict.",
    instruction="""You are the Compliance Verifier. Your task is to compare the Policy Rule against the Retrieved Evidence. 
    Your output MUST be a valid JSON object matching the schema.
    
    Example Output:
    {
        "policy_rule": "Verify that X is Y",
        "document_id": "doc_123",
        "verdict": "COMPLIANT",
        "reasoning": "The evidence explicitly states that X is Y.",
        "confidence": 1.0
    }

    POLICY RULE: {policy_rule}
    RETRIEVED EVIDENCE: {evidence}
    """
)

# Reporting Agent
ReportingAgent = LlmAgent(
    model='gemini-2.0-flash-exp',
    name="ReportingAgent",
    description="Aggregates all individual verdicts, flags NON-COMPLIANT items, and generates a final audit report. Uses code to hash the report.",
    tools=[CodeTool],
    instruction="You are a Reporting Agent. Generate comprehensive reports. When asked to hash text, use the CodeExecutionTool and output ONLY the hash."
)

# Workflow Execution

def run_veritrace_audit(policy_document_path: str) -> str:
    """
    Orchestrates the compliance audit workflow using sequential agent calls.
    """
    print(f"--- Starting VeriTrace Audit for: {policy_document_path} ---")
    
    # Read Policy Document
    try:
        with open(policy_document_path, 'r', encoding='utf-8') as f:
            policy_content = f.read()
    except Exception as e:
        return f"Error reading policy document: {e}"

    trace_log = []
    final_verdicts: List[ComplianceVerdict] = []
    
    # Orchestration
    print("\n[PHASE 0]: Orchestrating Checks...")
    orch_result = OrchestratorAgent.act(input=f"Extract checks from:\n{policy_content}", output_schema=ComplianceCheckList)
    trace_log.append({"step": "Orchestration", "result": orch_result.text, "metadata": orch_result.metadata})
    
    if orch_result.result:
        initial_checks = orch_result.result[0].value.checks
        print(f"   -> Extracted {len(initial_checks)} checks.")
    else:
        print("   !!! Orchestration Failed. Using fallback checks.")
        initial_checks = ["Verify that backups are retained for at least 90 days."]

    
    # In a fully deployed ADK system, this would be a LoopAgent over the Orchestrator's output.
    for i, check in enumerate(initial_checks):
        print(f"\n[CHECK {i+1}/{len(initial_checks)}]: {check}")
        
        # Retrieval
        try:
            retrieval_result = RetrieverAgent.act(input=check)
            trace_log.append({"step": f"Retrieval-{i}", "check": check, "result": retrieval_result.text, "metadata": retrieval_result.metadata})
            
            evidence_json = retrieval_result.text # JSON string from custom_tools.py
            print(f"DEBUG: Retriever Output: {evidence_json}")
            
            # Clean up json if needed (sometimes it has markdown blocks)
            if "```json" in evidence_json:
                evidence_json = evidence_json.split("```json")[1].split("```")[0]
            elif "```" in evidence_json:
                evidence_json = evidence_json.split("```")[1].split("```")[0]
                
            try:
                evidence_data = json.loads(evidence_json)
                evidence_text = evidence_data.get('evidence_text', "No evidence found.")
                doc_id = evidence_data.get('document_id', "N/A")
            except json.JSONDecodeError:
                evidence_text = evidence_json
                doc_id = "Unknown"
            
            print(f"   -> Retrieved evidence from: {doc_id}")
            
            # Verification
            verifier_input_str = f"POLICY RULE: {check}\nRETRIEVED EVIDENCE: {evidence_text}"
            
            verdict_response = VerifierAgent.act(
                input=verifier_input_str,
                output_schema=ComplianceVerdict
            )
            trace_log.append({"step": f"Verification-{i}", "check": check, "result": verdict_response.text, "metadata": verdict_response.metadata})
            
            # Extract the Pydantic object (demonstrates robust data handling)
            if verdict_response.result:
                verdict_object: ComplianceVerdict = verdict_response.result[0].value
                
                print(f"   -> VERDICT: {verdict_object.verdict} (Confidence: {verdict_object.confidence:.2f})")
                print(f"   -> Reasoning: {verdict_object.reasoning[:80]}...")
                
                final_verdicts.append(verdict_object)
            else:
                print(f"   !!! Verification Failed: No result returned. Response: {verdict_response.text}")
            
        except Exception as e:
            print(f"   !!! Audit Failed for check {check}: {e}")

    # Reporting
    summary_prompt = "Generate a comprehensive, executive summary of the audit findings. List all NON-COMPLIANT items and their specific remediation steps based on the reasoning provided. \n\nVERDICTS: " + json.dumps([v.model_dump() for v in final_verdicts])
    
    # Hash the report
    code_hash_prompt = "Generate the SHA-256 hash for the following text: " + summary_prompt
    hash_result = ReportingAgent.act(input=code_hash_prompt)
    trace_log.append({"step": "Hashing", "result": hash_result.text, "metadata": hash_result.metadata})
    
    final_report_text = ReportingAgent.act(input=summary_prompt).text
    trace_log.append({"step": "Reporting", "result": final_report_text, "metadata": final_report_text}) # Metadata might be missing here if not returned by act, assuming simple_agent update handles it.
    
    # Export reports
    # 1. JSON Report
    report_data = {
        "timestamp": "2025-11-30",
        "policy_document": policy_document_path,
        "verdicts": [v.model_dump() for v in final_verdicts],
        "report_hash": hash_result.text,
        "trace_log": trace_log
    }
    with open("audit_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
        
    # 2. CSV Export
    with open("audit_report.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Policy Rule", "Verdict", "Confidence", "Document ID", "Reasoning"])
        for v in final_verdicts:
            writer.writerow([v.policy_rule, v.verdict, v.confidence, v.document_id, v.reasoning])

    return final_report_text + f"\n\n--- AUDIT VERIFICATION HASH (Code Execution Tool) ---\nReport Hash: {hash_result.text}"

if __name__ == "__main__":
    from mock_data import MOCK_POLICY_CHECKS # Re-import here for execution

    # The main execution block
    final_audit_report = run_veritrace_audit(
        policy_document_path="demo_docs/policy_document.txt"
    )
    
    print("\n" + "="*80)
    print("FINAL AUDIT REPORT")
    print("="*80)
    print(final_audit_report)
