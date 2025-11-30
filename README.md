# VeriTrace Agent - Automated Compliance Auditing

**VeriTrace** is a multi-agent system designed to automate the compliance audit lifecycle. It uses a team of specialized AI agents to orchestrate, retrieve, verify, and report on compliance checks against internal policy documents.

## Problem Statement
Highly regulated industries like finance, healthcare, and enterprise SaaS live under constant pressure to stay compliant with evolving data, privacy, and security regulations. Manual audits are slow, expensive, and error-prone. VeriTrace solves this by automating the verification of complex regulations against massive internal knowledge bases.

## Architecture
The system consists of four specialized agents:
1.  **PolicyOrchestrator**: Dynamically breaks down high-level policies into atomic, testable checks.
2.  **RetrieverAgent**: Searches internal documentation (simulated vector DB) for relevant evidence.
3.  **ComplianceVerifier**: Uses reasoning to compare policy rules against evidence and output structured verdicts (`COMPLIANT`, `NON_COMPLIANT`, `NEEDS_REVIEW`).
4.  **ReportingAgent**: Aggregates findings into JSON/CSV reports and cryptographically hashes the result for auditability.

## Tech Stack
-   **Python 3.8+**
-   **Google Gemini API** (`gemini-2.0-flash-exp`)
-   **Pydantic** (Data Validation)
-   **Custom Tooling** (Document Search, Code Execution)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/veritrace-agent.git
    cd veritrace-agent
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

## Usage

Run the main application to start the audit simulation:

```bash
python main_app.py
```

The agent will:
1.  Read the `demo_docs/policy_document.txt`.
2.  Extract compliance checks.
3.  Search for evidence in `demo_docs/`.
4.  Generate `audit_report.json` and `audit_report.csv`.

## Project Structure
-   `main_app.py`: Core logic and agent orchestration.
-   `simple_agent.py`: Custom LLM agent framework.
-   `custom_tools.py`: Tools for document search and code execution.
-   `demo_docs/`: Sample policy documents and evidence files (SQL, YAML, Markdown).

## Future Improvements
-   Integration with real Vector DBs (Chroma/Pinecone).
-   Human-in-the-loop UI for `NEEDS_REVIEW` verdicts.
-   Multi-modal evidence analysis (screenshots, diagrams).
