
# Contains the simulated policy rules and internal document chunks.

MOCK_POLICY_CHECKS = [
    "Verify that PII is masked in development and testing environments.", 
    "Verify that user account data is purged within 90 days of closure.",
    "Verify that every PII access is logged to a central, immutable audit database.",
    "Verify that third-party APIs for data processing are documented in the vendor contract database."
]

MOCK_INTERNAL_DOCS = [
    # Document 1: COMPLIANT EVIDENCE for Check 1 (PII Masking)
    {"id": "AUDIT-SYS-DOC", "text": "All internal database queries involving PII trigger a write to the 'ImmutableLedger' table. **No PII is ever used in QA/testing environments.**"},
    
    # Document 2: NON-COMPLIANT EVIDENCE for Check 2 (Retention Limit)
    {"id": "SOP-101", "text": "Our new account closure script marks the account as inactive and deletes the user data after **95 days**. We use a single, mutable log file for all data access events."},
    
    # Document 3: NON-COMPLIANT EVIDENCE for Check 4 (Vendor Compliance)
    {"id": "API-v3-Spec", "text": "The /user-data/ endpoint uses the vendor 'QuickAnalytics' for data processing, but this **is not tracked** in the contracts DB, as it was a rapid integration."},
    
    # Document 4: COMPLIANT EVIDENCE for Check 3 (Audit Log)
    {"id": "LOGGING-ARCH-V1", "text": "All successful PII access events (read or write) generate an entry in the **ImmutableLedger**, which is backed by a secure, append-only database."}
]

# This is the high-accuracy mapping used by the custom tool to simulate vector search results.
MOCK_SEARCH_MAPPING = {
    MOCK_POLICY_CHECKS[0]: MOCK_INTERNAL_DOCS[0], 
    MOCK_POLICY_CHECKS[1]: MOCK_INTERNAL_DOCS[1], 
    MOCK_POLICY_CHECKS[2]: MOCK_INTERNAL_DOCS[3], 
    MOCK_POLICY_CHECKS[3]: MOCK_INTERNAL_DOCS[2], 
}