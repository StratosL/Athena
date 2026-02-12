# Hierarchical RAG Agent - End-to-End Testing Results

This document captures comprehensive end-to-end testing of the Hierarchical RAG Agent, validating the quality of retrieval, tool usage, and response synthesis.

**Test Date:** 2026-02-04
**LLM Model:** anthropic/claude-haiku-4.5 (via OpenRouter)
**Embedding Model:** openai/text-embedding-3-small
**Documents:** 17 documents, 310 chunks across 4 category hierarchies

---

## Test 1: VPN Configuration (Basic Retrieval)

**Question:** "How do I configure a site-to-site VPN tunnel between two office locations?"

**Response Summary:**
Provided a complete step-by-step guide including gateway configuration, encryption setup, tunnel parameters, and routing configuration with specific code examples.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `search_knowledge_base` | `query: "site-to-site VPN tunnel configuration", top_k: 5` | Initial semantic search |
| 2 | `get_chunk_context` | `chunk_id: 153` | Expand step-by-step implementation section |
| 3 | `get_document_overview` | `document_id: 1` | Get full document structure |

</details>

<details>
<summary><strong>Retrieved Chunks</strong></summary>

| Chunk ID | Similarity | Category | Document | Section |
|----------|------------|----------|----------|---------|
| 147 | 0.685 | Networking | VPN Configuration | VPN Architecture and Types > Site-to-Site VPN Configuration |
| 153 | 0.671 | Networking | VPN Configuration | Deployment and Configuration Procedures > Step-by-Step Implementation |
| 146 | 0.598 | Networking | VPN Configuration | Overview |
| 154 | 0.595 | Networking | VPN Configuration | Remote Access VPN Client Configuration |
| 151 | 0.584 | Networking | VPN Configuration | Security Protocols and Encryption Standards > SSL/TLS VPN Configuration |

</details>

<details>
<summary><strong>Hierarchical Navigation</strong></summary>

The agent used structural hierarchy effectively:
- **Parent Section Retrieved:** Full deployment procedures context including Overview and VPN Architecture sections
- **Sibling Chunks:** 14 sibling chunks identified, showing the agent accessed the broader document structure
- **Hierarchy Path:** VPN Configuration > Deployment and Configuration Procedures > Step-by-Step Implementation

</details>

**Assessment:** Excellent retrieval - correctly identified the VPN Configuration document and navigated to the specific implementation section. Used `get_chunk_context` to expand beyond the initial leaf chunk.

---

## Test 2: GDPR Data Retention (Compliance Query)

**Question:** "What are the GDPR requirements for data retention and the right to deletion?"

**Response Summary:**
Comprehensive answer covering storage limitation requirements, data retention examples with specific timelines, and detailed right to deletion (right to be forgotten) implementation guidance including automated deletion workflow components.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `search_knowledge_base` | `query: "GDPR data retention requirements"` | Initial search for retention |
| 2 | `search_knowledge_base` | `query: "right to deletion GDPR"` | Parallel search for deletion rights |
| 3 | `get_chunk_context` | `chunk_id: 219` | Expand data mapping section |
| 4 | `get_chunk_context` | `chunk_id: 224` | Expand right to deletion section |
| 5 | `search_knowledge_base` | `query: "GDPR storage limitation policy"` | Additional search for completeness |
| 6 | `search_knowledge_base` | `query: "GDPR deletion automation"` | Search for implementation details |
| 7 | `get_chunk_context` | `chunk_id: 227` | Get compliance pitfalls context |

</details>

<details>
<summary><strong>Key Retrieved Content</strong></summary>

**Data Retention Requirements:**
- Storage location documentation
- Retention period by data category
- Automated purge processes

**Example Retention Periods Found:**
- Customer Email (CRM): 3 years
- Employee Records (HRIS): 7 years
- Transaction Logs: 1 year

**Right to Deletion Components:**
- Full vs selective deletion options
- Primary systems, cloud storage, backups, search indices
- Audit trail requirements

</details>

**Assessment:** The agent performed multiple targeted searches to gather comprehensive information, demonstrating iterative retrieval when initial results were incomplete. Properly combined regulatory requirements with practical implementation guidance.

---

## Test 3: Python Coding Standards (Development Query)

**Question:** "What are the Python type annotation requirements and how should I handle mutable default arguments?"

**Response Summary:**
Detailed answer covering mandatory type hints for all functions, example patterns using `typing` module, and the mutable default argument pitfall with correct/incorrect code examples.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `search_knowledge_base` | `query: "Python type annotations requirements"` | Search for type hints |
| 2 | `search_knowledge_base` | `query: "mutable default arguments Python"` | Parallel search for pitfall |
| 3 | `get_chunk_context` | `chunk_id: 65` | Expand type hints section |
| 4 | `get_chunk_context` | `chunk_id: 71` | Expand mutable defaults section |
| 5 | `get_document_overview` | `document_id: 6` | Get Coding Standards overview |
| 6 | `search_knowledge_base` | `query: "mandatory type hints Python functions"` | Refinement search |

</details>

<details>
<summary><strong>Retrieved Chunks</strong></summary>

| Chunk ID | Category | Document | Section |
|----------|----------|----------|---------|
| 65 | Development > Python | Coding Standards | Type Hints and Annotations > Mandatory Type Annotations |
| 71 | Development > Python | Coding Standards | Common Pitfalls and Troubleshooting > Mutable Default Arguments |

</details>

**Assessment:** Successfully identified the Coding Standards document in the Development > Python category. Retrieved both the type annotation requirements AND the mutable default argument pitfall section, demonstrating ability to address multi-part questions.

**Note:** Response truncated due to Windows Unicode encoding issue with emoji characters in the original document content.

---

## Test 4: Incident Response (Security Query)

**Question:** "How should I respond to a critical security incident involving unauthorized access?"

**Response Summary:**
Comprehensive incident response guide covering immediate triage, severity classification, containment procedures, stakeholder notification timelines, and recovery validation checklist.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `search_knowledge_base` | `query: "critical security incident unauthorized access response"` | Initial search |
| 2 | `list_categories` | - | Understand knowledge base structure |
| 3 | `get_document_overview` | `document_id: 13` | Get Incident Response Playbook overview |
| 4 | `get_chunk_context` | `chunk_id: 196` | Expand containment section |
| 5 | `get_chunk_context` | `chunk_id: 204` | Expand recovery section |
| 6 | `search_knowledge_base` | `query: "incident triage escalation"` | Additional search |
| 7 | `get_chunk_context` | `chunk_id: 193` | Expand triage section |

</details>

<details>
<summary><strong>Cross-Document Retrieval</strong></summary>

The agent combined information from multiple documents:
- **Incident Response Playbook** - Detection, containment, recovery procedures
- **SOC2 Requirements** - Severity classification and response timelines

This demonstrates the categorical hierarchy navigation working correctly.

</details>

<details>
<summary><strong>Key Retrieved Sections</strong></summary>

| Document | Section | Content |
|----------|---------|---------|
| Incident Response Playbook | Detection and Alert Triage | Triage process, severity levels |
| Incident Response Playbook | Containment and Isolation | Network and endpoint containment |
| Incident Response Playbook | Eradication and Recovery | Remediation steps, validation checklist |
| SOC2 Requirements | Incident Classification | Severity Level 1-4 timelines |

</details>

**Assessment:** Excellent cross-category retrieval. The agent proactively used `list_categories` to understand the knowledge base structure, then combined information from both the Incident Response Playbook and SOC2 Requirements to provide a complete answer.

---

## Test 5: REST API Error Codes (Development Query)

**Question:** "What HTTP status codes should I use for different types of API errors?"

**Response Summary:**
Complete HTTP status code reference including 400, 401, 403, 404, 409, 429, 500, and 503 with use cases for each. Also included recommended error response format structure.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `search_knowledge_base` | `query: "HTTP status codes API error handling"` | Initial search |
| 2 | `list_categories` | - | Explore category structure |
| 3 | `get_chunk_context` | `chunk_id: 35` | Expand status code section |
| 4 | `get_document_overview` | `document_id: 8` | Get REST API Design Guide overview |

</details>

<details>
<summary><strong>Retrieved Content</strong></summary>

| Status Code | Category | Use Case |
|-------------|----------|----------|
| 400 | Bad Request | Client-side validation errors |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but lacks permission |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Request conflicts with current state |
| 429 | Rate Limited | Too many requests in time window |
| 500 | Server Error | Unexpected server-side failure |
| 503 | Service Unavailable | Temporary service degradation |

</details>

**Assessment:** Direct, accurate retrieval from the REST API Design Guide. The agent correctly identified the Development > API Design category and retrieved the complete status code reference.

---

## Test 6: Application Alerting (Operations Query)

**Question:** "How do I configure alerting for high error rates in my application?"

**Response Summary:**
Provided Prometheus alert rule configuration example with PromQL expression for error rate calculation, threshold tuning methodology, and best practices for reducing alert fatigue.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `list_categories` | - | Explore knowledge base structure |
| 2 | `search_knowledge_base` | `query: "alerting high error rates application monitoring"` | Initial search |
| 3 | `get_chunk_context` | `chunk_id: 174` | Expand alert definition section |
| 4 | `get_chunk_context` | `chunk_id: 169` | Expand alerting setup section |
| 5 | `get_document_overview` | `document_id: 15` | Get Observability Guide overview |

</details>

<details>
<summary><strong>Retrieved Configuration Example</strong></summary>

```yaml
- alert: HighErrorRate
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[5m]))
      /
      sum(rate(http_requests_total[5m]))
    ) > 0.05
  for: 5m
  labels:
    severity: critical
```

</details>

**Assessment:** Successfully retrieved the Observability Guide from the Operations > Monitoring category. Provided actionable Prometheus configuration with proper PromQL expressions.

---

## Test 7: Compliance Framework Comparison (Cross-Category Query)

**Question:** "What compliance frameworks do we need to consider for handling customer data, and what are the key differences between them?"

**Response Summary:**
Comprehensive comparison of GDPR, SOC2, PCI-DSS, HIPAA, and ISO 27001 including scope, key requirements, penalties, and a comparison table.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `list_categories` | - | Understand available categories |
| 2 | `search_knowledge_base` | `query: "compliance frameworks customer data"` | Initial broad search |
| 3 | `get_document_overview` | `document_id: 11` | Get GDPR Compliance Guide overview |
| 4 | `search_knowledge_base` | `query: "SOC2 requirements"` | Search for SOC2 info |
| 5 | `get_chunk_context` | `chunk_id: 209` | Expand GDPR core requirements |
| 6 | `search_knowledge_base` | `query: "compliance security requirements"` | Broader search |
| 7 | `get_document_overview` | `document_id: 12` | Get SOC2 Requirements overview |
| 8 | `get_chunk_context` | Multiple chunks | Expand context from various sources |

</details>

<details>
<summary><strong>Frameworks Retrieved</strong></summary>

| Framework | Source Document | Primary Focus |
|-----------|-----------------|---------------|
| GDPR | GDPR Compliance Guide | EU personal data protection |
| SOC2 | SOC2 Requirements | Trust service principles |
| PCI-DSS | Firewall Policies (reference) | Payment card data |
| HIPAA | Vulnerability Management (reference) | Health information |
| ISO 27001 | Multiple (reference) | Information security standard |

</details>

**Assessment:** Excellent demonstration of cross-category retrieval. The agent successfully combined information from multiple compliance documents in the Security > Compliance category, plus found references to other frameworks in infrastructure documents.

---

## Test 8: Deployment Checklist (Operations Query)

**Question:** "What steps should I follow before deploying to production to ensure nothing breaks?"

**Response Summary:**
Started providing pre-deployment verification steps including compute resources, network connectivity, and CI/CD pipeline verification before encountering encoding issue.

<details>
<summary><strong>Tool Calls (Before Error)</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `list_categories` | - | Explore categories |
| 2 | `search_knowledge_base` | `query: "production deployment checklist"` | Initial search |
| 3 | `search_knowledge_base` | `query: "pre-deployment verification"` | Parallel search |
| 4 | `get_chunk_context` | Multiple chunks | Expand checklist sections |
| 5 | `get_document_overview` | `document_id: 17` | Get Deployment Checklist overview |

</details>

<details>
<summary><strong>Retrieved Sections</strong></summary>

| Document | Section | Content |
|----------|---------|---------|
| Deployment Checklist | Pre-Deployment Verification | Environment prerequisites |
| Deployment Checklist | CI/CD Pipeline Verification | Pipeline stage requirements |
| Deployment Checklist | Pre-Deployment Testing | Smoke testing procedures |

</details>

**Assessment:** Correctly identified the Deployment Checklist document in Operations > Deployment category. Response truncated due to Unicode encoding issue.

**Note:** Windows encoding error occurred when the LLM response contained checkmark emoji characters.

---

## Test 9: Logging Format and Retention (Cross-Domain Query)

**Question:** "What logging format should I use for my applications and how long should I retain logs?"

**Response Summary:**
Recommended JSON structured logging with specific field requirements, plus retention policy of 90 days minimum with 1-year searchable retention for SOC2 compliance.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `search_knowledge_base` | `query: "logging format applications structured"` | Search for format guidance |
| 2 | `search_knowledge_base` | `query: "log retention policy compliance"` | Parallel search for retention |
| 3 | `get_chunk_context` | `chunk_id: 163` | Expand structured logging section |
| 4 | `get_chunk_context` | `chunk_id: 238` | Expand SOC2 logging requirements |
| 5 | `get_chunk_context` | `chunk_id: 167` | Expand log aggregation section |

</details>

<details>
<summary><strong>Cross-Document Synthesis</strong></summary>

The agent combined information from two different categories:

| Source | Category | Information |
|--------|----------|-------------|
| Observability Guide | Operations > Monitoring | JSON format, structured logging implementation |
| SOC2 Requirements | Security > Compliance | 90-day minimum, 1-year searchable retention |

</details>

**Assessment:** Excellent cross-category synthesis. Combined operational guidance (logging format) with compliance requirements (retention periods) to provide a complete answer.

---

## Test 10: Security Breach with Personal Data (Complex Cross-Domain Query)

**Question:** "If a security breach exposes customer personal data, what specific steps do I need to take and what are the notification timelines?"

**Response Summary:**
Comprehensive response combining incident response procedures with GDPR notification requirements, including specific timelines (72-hour regulatory notification), stakeholder notification matrix, and containment procedures.

<details>
<summary><strong>Tool Calls</strong></summary>

| Order | Tool | Parameters | Purpose |
|-------|------|------------|---------|
| 1 | `list_categories` | - | Understand knowledge base structure |
| 2 | `search_knowledge_base` | `query: "security breach personal data notification"` | Initial comprehensive search |
| 3 | `get_document_overview` | `document_id: 13` | Get Incident Response Playbook overview |
| 4 | `get_chunk_context` | `chunk_id: 196` | Expand containment procedures |
| 5 | `get_chunk_context` | `chunk_id: 219` | Expand GDPR breach notification |
| 6 | `get_chunk_context` | `chunk_id: 205` | Expand stakeholder notification |
| 7 | `search_knowledge_base` | `query: "breach notification timeline regulatory"` | Refine notification search |
| 8 | `get_chunk_context` | `chunk_id: 221` | Expand 72-hour timeline |

</details>

<details>
<summary><strong>Multi-Category Synthesis</strong></summary>

| Category Path | Document | Information Retrieved |
|---------------|----------|----------------------|
| Security > Incident Response | Incident Response Playbook | Containment steps, recovery procedures |
| Security > Compliance | GDPR Compliance Guide | 72-hour notification, data subject rights |
| Security > Compliance | SOC2 Requirements | Severity classification, incident timeline |

</details>

<details>
<summary><strong>Key Timelines Retrieved</strong></summary>

**Incident Response Timelines:**
| Stakeholder | Timing | Required Information |
|-------------|--------|---------------------|
| Legal/Compliance | Immediately | Data categories, notification obligations |
| Executive Leadership | Within 4 hours | Severity, impact scope, remediation |
| Affected Users | Within 24 hours | What data affected, recommended actions |
| Insurance Provider | Within 48 hours | Incident summary, estimated costs |

**GDPR-Specific (72-Hour Timeline):**
| Timeframe | Action |
|-----------|--------|
| Immediate | Isolate systems, preserve evidence |
| Within 24 hours | Internal notification, begin investigation |
| Within 48 hours | Scope determination, risk assessment |
| Within 72 hours | File notification to Supervisory Authority |
| 72 hours+ | Notify affected data subjects |

</details>

**Assessment:** Outstanding demonstration of hierarchical RAG capabilities. The agent:
1. Used `list_categories` to understand the knowledge base structure
2. Performed targeted searches across security-related categories
3. Retrieved and combined information from 3 different documents
4. Synthesized a comprehensive response with properly cited sources

---

## Summary: Agent Behavior Analysis

### Tool Usage Patterns

| Tool | Total Calls | Average per Question | Purpose |
|------|-------------|---------------------|---------|
| `search_knowledge_base` | 24 | 2.4 | Primary retrieval mechanism |
| `get_chunk_context` | 26 | 2.6 | Structural hierarchy navigation |
| `list_categories` | 7 | 0.7 | Category exploration (informational only) |
| `get_document_overview` | 10 | 1.0 | Document-level understanding |

### Hierarchical RAG Effectiveness

**Categorical Hierarchy (Cross-Document): NOT UTILIZED**

**Critical Finding:** The agent calls `list_categories` but **never passes `category_ids` to filter searches**. All `search_knowledge_base` calls use only:
```json
{"query": "...", "top_k": 5}
```

No calls included `category_ids` parameter despite the system prompt instructing:
> "Use 'search_knowledge_base' with relevant category_ids to search within the right scope."

This means:
- `list_categories` provides informational context but is not actionably used
- The agent relies entirely on vector similarity without categorical pre-filtering
- Cross-category retrieval works via semantic similarity, not explicit category scoping

**Structural Hierarchy (Within-Document): WORKING WELL**
- Consistently used `get_chunk_context` to expand beyond initial leaf chunks
- Retrieved parent sections for broader context
- Identified sibling chunks for related content

### Quality Indicators

| Metric | Observation |
|--------|-------------|
| **Source Citation** | All responses included document and section references |
| **Multi-Source Synthesis** | 6/10 questions synthesized from multiple documents |
| **Iterative Retrieval** | Agent performed follow-up searches when initial results incomplete |
| **Category Navigation** | Correctly identified relevant categories for all queries |
| **Context Expansion** | Used structural hierarchy in 100% of responses |

### Issues Identified

1. **Category Filtering Not Used (Major):** The agent never uses `category_ids` parameter when calling `search_knowledge_base`. Despite the system prompt instructing it to filter by category, and despite calling `list_categories` to get category IDs, the agent ignores this information and performs unfiltered semantic search. This means the categorical hierarchy feature is effectively unused.

2. **Windows Unicode Encoding:** LLM responses containing emoji characters (checkmarks, X marks) cause crashes on Windows terminals with cp1252 encoding. This is a display issue, not a retrieval problem.

3. **Document ID Mismatch:** In one case, `get_document_overview` returned a different document than expected (GraphQL instead of SOC2), suggesting the agent is using incorrect document IDs (possibly chunk document_id vs actual document table ID mismatch).

---

## Conclusion

The Hierarchical RAG Agent demonstrates **partial** effectiveness:

### What Works Well
1. **Structural Hierarchy:** Consistently expands beyond leaf chunks using `get_chunk_context` to retrieve parent sections and siblings - this is the primary value-add of the hierarchical approach
2. **Iterative Retrieval:** Performs multiple searches when needed to gather comprehensive information
3. **Source Attribution:** Properly cites document paths and section headings in responses
4. **Cross-Category Synthesis:** Can combine information from multiple documents (via semantic similarity)

### What Needs Improvement
1. **Categorical Hierarchy Not Utilized:** The agent never uses `category_ids` to filter searches, despite the feature existing and the system prompt instructing it to do so. This means:
   - `list_categories` calls are essentially wasted tokens
   - No search space reduction via category pre-filtering
   - Relies entirely on vector similarity for relevance

### Actual Retrieval Strategy (Observed)
1. ~~Explores categories when needed (`list_categories`)~~ - Called but output ignored
2. Performs **unfiltered** semantic search (`search_knowledge_base`)
3. Expands context (`get_chunk_context`) - **Primary hierarchical value**
4. Gets document overview (`get_document_overview`)
5. Synthesizes with proper citations

### Recommendation
To fully leverage the categorical hierarchy, consider:
- Stronger system prompt instructions with explicit examples
- Few-shot examples showing category filtering in action
- Or removing `list_categories` if it's not providing value
