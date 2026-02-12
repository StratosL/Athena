# Hierarchical RAG Workshop - Test Questions

These questions are designed to progressively test the hierarchical RAG agent's ability to navigate categorical hierarchies (filtering by topic/category) and structural hierarchies (expanding chunk context via parent/sibling relationships). Each tier increases in difficulty.

> **How to use:** Ask these questions to the agent via `uv run python -m src.cli` and observe which tools it calls, whether it filters by category, and whether it uses `get_chunk_context` or `get_document_overview` to expand answers.

---

## Tier 1: Single-Category, Deep Structural Navigation

These test whether the agent correctly identifies a single category and drills into the chunk hierarchy to find specific details.

### Q1: "What are the IKE Phase 1 and Phase 2 parameters for our site-to-site VPN configuration?"

**Expected behavior:** Route to Infrastructure > Networking, search with category filter, retrieve VPN Configuration chunks.

<details>
<summary>Expected Answer</summary>

The VPN Configuration document specifies distinct parameters for each IKE phase:

**IKE Phase 1:**
- Encryption: AES-256
- Hash: SHA-256 or stronger
- Diffie-Hellman Group: 14 or higher
- Lifetime: 28,800 seconds (8 hours)

**IKE Phase 2:**
- Encryption: AES-256-GCM
- Authentication: SHA-384
- Lifetime: 3,600 seconds (1 hour)

Additionally, the overall IPsec configuration specifies:
- Encryption Algorithm: AES-256-GCM
- Authentication Algorithm: SHA-384
- DH Group: 20
- IKE Version: IKEv2
- Rekey Interval: 3,600 seconds

The tunnel configuration also uses PFS Group 20 and a rekey margin of 540 seconds.

**Source:** VPN Configuration > Security Protocols and Encryption Standards
</details>

---

### Q2: "What is our GDPR breach notification timeline?"

**Expected behavior:** Route to Security > Compliance, search with category filter, retrieve GDPR Compliance Guide chunks about the 72-hour timeline.

<details>
<summary>Expected Answer</summary>

GDPR requires breach notification to supervisory authorities within **72 hours** of discovery. The specific timeline is:

| Time Period | Action | Responsible Party |
|---|---|---|
| **Immediate** | Isolate affected systems, preserve evidence | IT Security |
| **Within 24 hours** | Notify internal stakeholders, begin investigation | CISO, Legal, DPO |
| **Within 48 hours** | Determine scope and risk assessment | Data Protection Team |
| **Within 72 hours** | File breach notification to Supervisory Authority | Legal/DPO |
| **Within 72 hours+** | Notify affected data subjects (if required) | Communications/DPO |

The breach notification to the Supervisory Authority must include:
- Date of discovery
- Nature of breach (unauthorized access, data loss, encryption failure)
- Data categories affected
- Approximate number of affected individuals
- Likely consequences
- Measures taken to mitigate risk
- DPO contact information

Organizations face penalties up to **EUR 20 million or 4% of global annual revenue** (whichever is greater) for violations.

**Source:** GDPR Compliance Guide > Incident Response and Breach Notification
</details>

---

### Q3: "What k6 load test configuration do we use before production deployments?"

**Expected behavior:** Route to Operations > Deployment, search with category filter, retrieve Deployment Checklist chunks with the specific k6 config.

<details>
<summary>Expected Answer</summary>

Before deploying to production, the Deployment Checklist specifies the following k6 load test configuration:

```javascript
export let options = {
  vus: 100,           // 100 virtual users
  duration: '5m',     // 5-minute test duration
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // p95 < 500ms, p99 < 1000ms
    http_req_failed: ['rate<0.05'],                   // Error rate < 5%
  },
};
```

**Key thresholds:**
- **p95 response time** must be under 500ms
- **p99 response time** must be under 1,000ms
- **Error rate** must be below 5%

The load test should simulate **150% of average daily traffic** and the team should monitor response times, error rates, and resource utilization during the test. Baseline performance metrics from the previous production deployment should be established first.

**Source:** Deployment Checklist > Pre-Deployment Testing > Load Testing Requirements
</details>

---

### Q4: "What are our Python naming conventions and which linting tools do we use?"

**Expected behavior:** Route to Development > Python, search with category filter, retrieve Coding Standards chunks.

<details>
<summary>Expected Answer</summary>

**Naming Conventions (PEP 8 compliant):**
- Variables and functions: `lowercase_with_underscores` (snake_case)
- Classes: `PascalCase`
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Private methods/attributes: prefix with single underscore `_private_method`
- Dunder methods: `__method__` for special Python methods only

**Line length:** Maximum 88 characters (Black formatter standard), with 4-space indentation, no tabs.

**Required Linting/Static Analysis Tools:**

| Tool | Purpose | Config File |
|---|---|---|
| pylint | Comprehensive code analysis | `.pylintrc` |
| flake8 | PEP 8 style enforcement | `.flake8` |
| mypy | Static type checking | `mypy.ini` |
| bandit | Security vulnerability scanning | `.bandit` |

These are enforced via **pre-commit hooks** using the pre-commit framework, which runs Black (formatting), flake8 (style), mypy (types), and bandit (security) before every commit.

**Additional standards:**
- All functions must include type hints for parameters and return values
- Google-style docstrings with Args, Returns, and Raises sections
- f-strings for all string formatting (not `%` or `.format()`)
- Catch specific exceptions, never bare `except`

**Source:** Coding Standards > Style and Formatting Standards, Code Quality and Linting
</details>

---

### Q5: "How do we handle data subject access requests under GDPR?"

**Expected behavior:** Route to Security > Compliance > GDPR, retrieve chunks about SAR procedures.

<details>
<summary>Expected Answer</summary>

The GDPR Compliance Guide defines a formal three-phase process for handling data subject access requests (SARs):

**1. Request Intake (Target: 5 business days)**
- Accept requests through multiple channels (email, portal, phone)
- Verify the requestor's identity according to data protection policies
- Log all incoming requests in a centralized tracking system
- Confirm receipt to the data subject

**2. Data Retrieval (Target: 20 business days)**
- Query all systems containing the individual's data
- Extract data in readable, commonly-used format (CSV, PDF)
- Review extracted data for accuracy and completeness
- Redact information about third parties if necessary

**3. Delivery and Verification (Target: 30 business days)**
- Provide data in structured, machine-readable format
- Include metadata about data sources and processing
- Document the delivery method and confirmation
- Archive the complete request file for audit purposes

Beyond access requests, the organization must also support:
- **Right to Rectification** - Allow correction of inaccurate data
- **Right to Restrict Processing** - Temporarily suspend processing
- **Right to Portability** - Export in machine-readable formats
- **Right to Object** - Opt-out of direct marketing/profiling
- **Right to Deletion** - Automated deletion workflows including primary systems, cloud storage, backups (with 90-day retention period), and search indices

**Source:** GDPR Compliance Guide > Data Subject Rights Management
</details>

---

## Tier 2: Cross-Document Within Same Category

These test whether the agent searches multiple documents within the same category to synthesize an answer.

### Q6: "How do our firewall policies interact with our VLAN design?"

**Expected behavior:** Search Infrastructure > Networking, pull results from both Firewall Policies and Network Architecture Guide. Ideally use `get_chunk_context` to expand on relevant chunks from each.

<details>
<summary>Expected Answer</summary>

The Firewall Policies and Network Architecture Guide work together to define network segmentation:

**From Network Architecture Guide - VLAN Design:**
- VLANs isolate traffic by department, function, or security zone
- Numbering scheme: 10-99 for users, 100-199 for infrastructure
- Limit VLAN sizes to 250-500 hosts for optimal ARP performance
- Separate VLANs for user data, voice, video, and management traffic
- Inter-VLAN routing is done via Layer 3 switch with VLAN interfaces
- Access Control Lists (ACLs) control traffic between VLANs:
  ```
  access-list 101 permit ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
  access-list 101 deny ip 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255
  ```

**From Firewall Policies - Zone-Based Segmentation:**
- Five defined security zones: Perimeter, DMZ, Internal, Sensitive, Management
- Zero Trust philosophy: Default DROP, explicit allow rules only
- Firewall rules control inter-zone traffic with specific source/destination subnets
- Example: Application tier (10.1.20.0/24) is allowed TCP 5432 to Database tier (10.1.30.0/24), but database tier outbound is denied to all
- All inter-zone traffic is logged

**How they interact:**
- VLANs provide Layer 2 isolation (logical separation on the switch)
- Firewall policies enforce Layer 3/4 access control between zones
- The VLAN structure maps to firewall zones (e.g., VLAN 10 = Finance Department maps to Internal Zone; database VLANs map to Sensitive Zone)
- Inter-VLAN routing passes through firewall inspection points where policies are enforced
- Both require quarterly reviews and documentation in version control

**Sources:** Network Architecture Guide > VLAN Design and Segmentation, Security and Access Control; Firewall Policies > Designing Effective Firewall Policies, Core Firewall Rule Implementation
</details>

---

### Q7: "What's the difference between our REST and GraphQL API deprecation strategies?"

**Expected behavior:** Search Development > API Design, pull from both REST API Design Guide and GraphQL Best Practices.

<details>
<summary>Expected Answer</summary>

The two API design guides take fundamentally different approaches to deprecation:

**REST API Deprecation Strategy:**
- Uses **URL-based versioning**: `/api/v1/resources` vs `/api/v2/resources`
- Previous versions are supported for **12-18 months**
- Deprecation notices are provided **6 months before sunset**
- Breaking changes are documented in release notes
- Deprecation communicated via HTTP headers:
  ```
  Deprecation: true
  Sunset: Sun, 31 Dec 2024 23:59:59 GMT
  Link: <https://docs.example.com/migration-guide>; rel="deprecation"
  ```

**GraphQL Deprecation Strategy:**
- Does **NOT use API versions** (v1, v2) - instead evolves the schema through additive changes
- Individual fields and types are deprecated using the `@deprecated` directive:
  ```graphql
  name: String! @deprecated(reason: "Use firstName and lastName fields instead")
  ```
- Deprecated fields remain available for **6+ months before removal**
- Backward compatibility is maintained by:
  - Adding new fields without removing existing ones
  - Making new arguments optional with sensible defaults
  - Creating new query/mutation roots rather than changing existing ones

**Key Difference:** REST versions entire API endpoints, while GraphQL deprecates individual fields within a single evolving schema. REST requires clients to migrate to a new URL path; GraphQL allows gradual field-by-field migration.

**Sources:** REST API Design Guide > Versioning and Backward Compatibility; GraphQL Best Practices > Schema Design and Architecture > Schema Versioning Strategy
</details>

---

### Q8: "How do SOC2 logging requirements compare to what our Observability Guide recommends?"

**Expected behavior:** Search across Security > Compliance (SOC2) and Operations > Monitoring (Observability Guide). This crosses categories.

<details>
<summary>Expected Answer</summary>

**SOC2 Audit Logging Requirements (compliance-driven):**
- Log **all** authentication attempts (success and failure)
- Record administrative actions and configuration changes
- Track data access and modification events
- **Minimum 90-day retention** with searchable retention for **1 year**
- Forward logs to centralized SIEM (e.g., rsyslog to `siem-server:601`)
- Automated alerts for:
  - 5+ failed logins within 15 minutes
  - Privilege escalation attempts
  - Admin access outside business hours
  - Configuration changes to security controls
  - Unauthorized database access
  - Encryption key access/modification

**Observability Guide Recommendations (operational-driven):**
- **Structured JSON logging** with fields: timestamp, level, service, request_id, user_id, message, error_code, context
- Multi-stage log pipeline: Collection (Fluent Bit/Filebeat) > Parsing > Enrichment > Storage > Retention
- Tiered metric retention:
  - 15-second resolution: 15 days
  - 1-minute resolution: 90 days
  - 5-minute resolution: 1 year
  - 1-hour resolution: indefinite
- Distributed tracing with OpenTelemetry for cross-service request tracking
- Sampling: 100% of errors/high-latency, 5-10% probabilistic for high-volume
- Dashboard hierarchy: Status > Service (golden signals) > Infrastructure > Investigative

**Key Overlap:** Both require centralized log aggregation, retention policies, and alert rules. SOC2 mandates minimum retention periods (90 days/1 year), while the Observability Guide's tiered retention (90 days at 1-min, 1 year at 5-min) naturally satisfies this. SOC2 is prescriptive about *what* to log (auth, admin, config changes), while the Observability Guide focuses on *how* to log (structured JSON, pipelines, sampling).

**Sources:** SOC2 Requirements > Security Event Logging and Monitoring; Observability Guide > Logging Architecture, Metrics Collection
</details>

---

### Q9: "Compare our incident response severity levels with our vulnerability management response timelines."

**Expected behavior:** Search Security > Incident Response and Security > Compliance, pulling from both Incident Response Playbook and Vulnerability Management (and possibly SOC2).

<details>
<summary>Expected Answer</summary>

These are two distinct but related frameworks - one reactive (incidents), one proactive (vulnerabilities):

**Incident Response Playbook - Severity & Response Times:**

| Severity | Response Time | Example |
|---|---|---|
| Critical | Immediate (MTTD < 1h, MTTR < 4h) | Active data breach, system outage |
| High | Standard triage | Unauthorized access attempt, malware |
| Medium | Standard triage | Policy violation, suspicious activity |
| Low | Standard triage | Minor anomalies |

KPI targets: MTTD < 1 hour, MTTR < 4 hours, 100% evidence preservation, stakeholder notification < 24 hours.

**SOC2 Incident Classification (more specific):**

| Severity | Response Time | Example |
|---|---|---|
| Level 1 (Critical) | Within 15 minutes | Active data breach, system outage |
| Level 2 (High) | Within 1 hour | Unauthorized access, malware detection |
| Level 3 (Medium) | Within 4 hours | Policy violation, configuration drift |
| Level 4 (Low) | Within 24 hours | Failed backup, incomplete logging |

**Vulnerability Management - Remediation Timelines (CVSS-based):**

| CVSS Score | Severity | Response Time |
|---|---|---|
| 9.0-10.0 | Critical | 24 hours initial response, 7 days to production patch |
| 7.0-8.9 | High | 7 days (reviewed within 24h for active exploitation) |
| 4.0-6.9 | Medium | 30 days (60 days to production) |
| 0.1-3.9 | Low | 90 days |

**Are they aligned?** Partially:
- **Critical:** Incident response (15-minute engagement) is much faster than vulnerability remediation (24-hour initial, 7-day patch). This makes sense - an active incident is more urgent than a discovered vulnerability.
- **Escalation bridge:** Critical vulnerabilities (CVSS 9.0+) trigger the incident response process if active exploitation is detected - immediate notification, incident ticket within 15 minutes, impact meeting within 1 hour, executive notification within 4 hours.
- **Gap:** Vulnerability management uses a priority formula: `(CVSS x 0.4) + (Asset Criticality x 0.3) + (Exploitability x 0.2) + (Exposure x 0.1)` - which may reprioritize a "High" CVSS vuln to "Critical" based on context, but incident response severity doesn't factor in this nuance.

**Sources:** Incident Response Playbook > Key Performance Indicators; SOC2 Requirements > Incident Classification and Timeline; Vulnerability Management > Severity Rating Framework, Incident Response Integration
</details>

---

## Tier 3: Cross-Category Synthesis

These require the agent to pull from multiple categories - the hardest test for hierarchical RAG.

### Q10: "If we detect unauthorized access to personal data in our AWS environment, what's our complete response procedure?"

**Expected behavior:** The agent should search across multiple categories: Security (Incident Response + GDPR), Infrastructure (AWS), and Operations (Alerting). This is the definitive cross-category test.

<details>
<summary>Expected Answer</summary>

This scenario requires coordinating procedures from four different knowledge areas:

**1. Detection (Alerting Setup + AWS):**
- CloudWatch alarms should fire for unusual access patterns (configured with SNS notification to `prod-alerts` topic)
- AWS CloudTrail provides the audit log for all API calls
- Security monitoring should detect via SIEM correlation rules, EDR agents, or UEBA anomalies
- SOC2 alerts trigger on: unauthorized database access attempts, admin access outside business hours, 5+ failed logins in 15 minutes

**2. Immediate Containment (Incident Response Playbook):**
- **Verify alert authenticity** - cross-reference multiple data sources, eliminate false positives
- **Assess severity** - unauthorized access to personal data is Critical (Severity Level 1)
- **Response within 15 minutes** - create incident ticket, notify executive team and legal
- **Network containment:**
  - Isolate affected EC2 instances (disable security group rules or move to isolation VLAN 999)
  - AWS Security Groups can restrict to only incident response team access (SSH/RDP from 10.0.0.0/24)
  - Block C2 domains at firewall and DNS
- **Endpoint containment:**
  - Reset compromised IAM credentials and access keys
  - Force re-authentication across all sessions
  - Terminate suspicious processes

**3. Evidence Collection (Incident Response Playbook):**
- Collect in order of volatility:
  1. Live system state (running processes, network connections, memory dumps)
  2. Filesystem evidence (disk images with SHA256 hash verification)
  3. System logs (CloudTrail logs, application logs, auth logs)
- Use the evidence collection script to capture: `ps auxww`, `netstat`, `ss`, `lastlog`, `lsof`, memory dump
- Maintain chain of custody documentation with hashes and access logs

**4. GDPR Notification Timeline:**
- **Immediate:** Isolate affected systems, preserve evidence (IT Security)
- **Within 24 hours:** Notify internal stakeholders - CISO, Legal, DPO
- **Within 48 hours:** Determine scope - what personal data categories were affected, how many individuals
- **Within 72 hours:** File breach notification to Supervisory Authority including:
  - Nature of breach
  - Data categories and approximate number of affected individuals
  - Likely consequences
  - Measures taken to mitigate risk
  - DPO contact information
- **Within 72 hours+:** Notify affected data subjects if required
- **Within 4 hours:** Executive leadership notification (per Incident Response Playbook)
- **Within 48 hours:** Insurance provider notification

**5. Eradication and Recovery:**
- Apply security patches to affected AWS instances
- Rebuild compromised systems from clean AMIs
- Validate with recovery checklist: malicious processes terminated, C2 blocked, SSH keys sanitized, security patches verified, EDR updated, monitoring enabled
- IAM roles reviewed with least privilege principle

**6. Post-Incident:**
- Executive summary, timeline, root cause analysis, impact assessment, lessons learned
- Update CloudWatch alarm configurations and security group rules
- Conduct security awareness training for affected departments
- GDPR: Maintain breach documentation for minimum 3 years

**Sources:** Incident Response Playbook (containment, evidence, recovery); GDPR Compliance Guide (72-hour notification, breach template); AWS Setup Guide (CloudWatch, Security Groups, IAM); Alerting Setup (detection pipeline); SOC2 Requirements (logging alerts, severity levels)
</details>

---

### Q11: "What security controls span from code development through production deployment?"

**Expected behavior:** The agent needs to search across Development (Coding Standards, Testing), Operations (CI/CD, Deployment Checklist), and Security (SOC2) categories.

<details>
<summary>Expected Answer</summary>

Security controls exist at every stage of the development-to-production pipeline:

**1. Development Phase (Coding Standards):**
- **bandit** - Security vulnerability scanning as a static analysis tool
- **Pre-commit hooks** enforce security scanning before every commit (Black, flake8, mypy, bandit)
- Specific exception handling required - no bare `except` clauses
- Type hints mandatory on all functions (catches type-related bugs)
- Minimum 80% code coverage for unit tests

**2. Testing Phase (Testing Guidelines):**
- **pytest** as primary framework with fixtures and parametrization
- Integration tests verify interactions between components and external systems
- Coverage targets: 80% minimum overall, 90% for critical business logic modules
- Tests run across multiple Python versions (3.8, 3.9, 3.10, 3.11) in CI matrix
- Mocking for external dependencies prevents real API/database calls in unit tests

**3. CI/CD Pipeline (CI/CD Pipeline Guide):**
- **Branch protection** - required reviewers before merge to main
- **Parallel test stages** - Unit tests + Code quality (SonarQube) run simultaneously
- **Vulnerability scanning:**
  - `trivy image --severity HIGH,CRITICAL` for container image scanning
  - SonarQube scanner for code-level vulnerabilities
- **Immutable builds** - specific dependency versions, containerized environments
- **Manual approval gate** before production deployment
- **Secrets management** - vault systems, never commit secrets to repositories
- **LDAP/SAML integration** for centralized user management
- **MFA** required for production deployment approvals
- **Audit logging** via SIEM for all credential access

**4. Pre-Deployment (Deployment Checklist):**
- CI/CD pipeline verification: branch protection (2+ reviewers), 80% coverage, zero critical vulnerabilities, signed container images
- Smoke testing: health endpoints (`/health` returns 200), critical API endpoints verified
- Load testing: k6 with 100 VUs, p95<500ms, p99<1000ms, error rate <5%
- Database migrations: backward-compatible, zero-downtime, with tested rollback procedures
- Environment validation script checking compute resources, service status

**5. Production Deployment (Deployment Checklist + SOC2):**
- Rolling deployment: Kubernetes with maxSurge=1, maxUnavailable=0
- Liveness probe (`/health`) and readiness probe (`/ready`) configured
- Enhanced monitoring for first 24 hours with alert thresholds at 75% of critical limits
- SOC2: All configuration changes logged, automated monitoring for unauthorized changes, 24-hour remediation for configuration drift

**6. Ongoing Compliance (SOC2):**
- Quarterly vulnerability scanning + monthly dependency scanning
- Critical vulnerabilities remediated within 15 days, High within 30 days
- Quarterly access reviews with 5-business-day remediation
- MFA on all administrative access
- Log retention: minimum 90 days, 1-year searchable
- Annual disaster recovery test

**Sources:** Coding Standards (bandit, pre-commit); Testing Guidelines (pytest, coverage, CI matrix); CI/CD Pipeline Guide (Trivy, SonarQube, approval gates); Deployment Checklist (smoke tests, load tests, rolling deploy); SOC2 Requirements (access control, vulnerability management, audit logging)
</details>

---

### Q12: "We're migrating a database with EU customer PII to Azure. What compliance, networking, and operational requirements apply?"

**Expected behavior:** Agent should search Infrastructure > Cloud (Azure Migration), Infrastructure > Networking (VPN), Security > Compliance (GDPR + SOC2), and possibly Operations (Deployment Checklist).

<details>
<summary>Expected Answer</summary>

This migration touches four major areas:

**1. Migration Strategy (Azure Migration Plan):**
- A database with PII is likely **Wave 2** (production, non-critical) or **Wave 3** (mission-critical) depending on business criticality
- Use **Azure Site Recovery** for continuous replication with minimal downtime
- Data migration phases:
  - Weeks 1-4: Initial full replication
  - Weeks 5-8: Incremental updates and validation
  - Weeks 9-10: Failover testing and DR verification
  - Weeks 11-12: Final cutover
- Monthly non-disruptive failover tests required
- Cost projection: Current $450K/year > estimated $380K Azure (15-18% savings, 14-month ROI)
- Right-size VMs after 30-day stabilization; use Reserved Instances for 30-50% savings
- **Watch out for:** Undersized target VMs, insufficient storage IOPS, incomplete DNS configuration

**2. Network Security (VPN + Azure Networking):**
- Hub-and-spoke network topology in Azure with dedicated database subnet (10.1.2.0/24)
- Hybrid connectivity via **ExpressRoute** (50 Mbps+ minimum, dual connections) or **Site-to-Site VPN** (IKEv2 with IPsec, VpnGw2+ SKU)
- VPN encryption: AES-256-GCM, SHA-384, DH Group 20, IKEv2
- Azure Firewall and NSGs for layered security
- Azure AD Connect for identity synchronization (password hash sync with 30-minute sync cycle)
- Database subnet must be restricted - only application tier can access it

**3. GDPR Compliance Requirements:**
- **Data Protection Impact Assessment (DPIA)** is mandatory before migration because:
  - Introduction of new technologies (cloud migration)
  - Processing of personal data at scale
- **Data inventory** must document: sources, types, movement, purposes, legal bases, owners
- **Data mapping** the flow: Source > Processing > Azure Storage > Retention Period > Deletion Process
- **Privacy by design:**
  - Database-level encryption (TDE with AES-256)
  - Row-level security policies
  - Role-based access control (RBAC)
  - PII removed from log files
  - Pseudonymization where feasible
- **Data location:** Ensure Azure region keeps data within EU/EEA or has adequate transfer mechanisms
- **Data Processing Agreements** with Microsoft Azure as a data processor
- **Breach notification** capability: 72-hour timeline must be maintained during and after migration
- **Data subject rights** must remain functional throughout migration (access, deletion, portability)

**4. SOC2 Requirements:**
- **Encryption:** TLS 1.2+ in transit, AES-256 at rest, 90-day key rotation, keys in dedicated KMS
- **Access control:** MFA for admin access, RBAC with least privilege, quarterly access reviews, 24-hour deprovisioning
- **Audit logging:** All auth attempts, admin actions, config changes, data access logged; 90-day minimum retention, 1-year searchable
- **Change control:** All migration steps documented and approved through change management process
- **Configuration management:** Baseline configs documented, automated monitoring for unauthorized changes, 24-hour drift remediation
- **Azure Policy** initiatives to enforce: encryption at rest, NSGs on all subnets, tag governance

**5. Operational Readiness:**
- Azure Monitor configured with VM metrics (CPU, Network, Disk) at 1-minute collection, 90-day retention
- Log Analytics workspace for AzureActivity, SecurityEvent, and Syslog
- Deployment checklist: compute resources verified (+25% buffer), connectivity tested, rollback procedures documented

**Sources:** Azure Migration Plan (strategy, networking, monitoring); VPN Configuration (hybrid tunnel encryption); GDPR Compliance Guide (DPIA, data mapping, encryption, breach notification); SOC2 Requirements (encryption, access control, audit logging)
</details>

---

### Q13: "What steps should I follow before deploying to production?"

**Expected behavior:** Primarily Operations > Deployment (Deployment Checklist + CI/CD Pipeline), but a thorough answer also pulls from Development (Testing Guidelines) and Security (SOC2) for the full picture.

<details>
<summary>Expected Answer</summary>

The Deployment Checklist provides the primary procedure, supplemented by CI/CD and testing standards:

**1. Environment Prerequisites:**
- Verify compute resources: CPU, memory, disk space at minimum **25% above peak usage projections**
- Confirm network connectivity: all required ports open, firewall rules configured
- Test connectivity to dependent services (databases, message queues, external APIs)
- Validate system libraries, runtime versions, and packages installed
- Run environment validation script checking `nproc`, `free -g`, `df`, and service status (postgresql, redis, nginx)

**2. CI/CD Pipeline Verification:**

| Stage | Success Criteria |
|---|---|
| Source Control | Branch protection enabled, 2+ required reviewers |
| Unit Tests | Minimum 80% code coverage (90% for critical modules) |
| Integration Tests | All database migrations succeed |
| Security Scanning | SAST + dependency checks, zero critical vulnerabilities |
| Build Artifacts | Container image signed and scanned |

- All commits merged via approved pull requests
- Security scanning completed (Trivy for containers, SonarQube for code)

**3. Pre-Deployment Testing (in staging mirror of production):**
- **Smoke tests:** Health endpoint returns 200, critical API endpoints (`/api/v1/users`, `/api/v1/services`, `/api/v1/config`) respond
- **Load tests:** k6 with 100 VUs for 5 minutes, p95<500ms, p99<1000ms, error rate <5%
- Simulate 150% of average daily traffic
- Establish baseline from previous deployment for comparison

**4. Database Migration:**
- Deploy schema changes in advance of application code
- Use zero-downtime migration techniques
- Test rollback procedures for every migration
- Create tables backward-compatibly, backfill data separately, add constraints after validation

**5. Deployment Execution:**
- Rolling update: Kubernetes with `maxSurge: 1`, `maxUnavailable: 0`
- Liveness probe on `/health` (30s initial delay, 10s period)
- Readiness probe on `/ready` (10s initial delay, 5s period)
- Manual approval gate for production (CI/CD Pipeline)

**6. Post-Deployment Validation:**
- Increase log verbosity for **24 hours**
- Set alert thresholds at **75% of critical limits**
- Monitor error rates, latency (p95, p99), and resource utilization
- Health checks: application endpoints, CPU <60%, memory <70%, DB query performance, external dependency connectivity

**7. Rollback Procedure (if issues found):**
- Script uses `git describe --tags --abbrev=0 HEAD^` to find previous version
- `kubectl set image` to roll back to previous container tag
- `kubectl rollout status` to verify rollback completion

**Sources:** Deployment Checklist (primary); CI/CD Pipeline Guide (pipeline stages, security scanning); Testing Guidelines (coverage thresholds)
</details>

---

## Tier 4: Broad / Adversarial Queries

These test the agent's judgment about when NOT to filter by category, and its ability to handle deliberately vague or cross-cutting topics.

### Q14: "What does 'encryption' mean across our entire organization?"

**Expected behavior:** This genuinely spans all categories. The agent should search broadly (without category filtering, or across multiple categories) and synthesize encryption requirements from GDPR, SOC2, VPN, AWS, and Azure documents.

<details>
<summary>Expected Answer</summary>

Encryption requirements appear across every major area of our documentation:

**Data at Rest:**
- **GDPR:** Database-level encryption using Transparent Data Encryption (TDE) with AES-256 algorithm
- **SOC2:** AES-256 or equivalent for all sensitive data at rest; separate encryption keys for different data classifications; keys stored in dedicated KMS
- **AWS:** EBS volumes encrypted by default; RDS with encrypted storage (100GB gp2)
- **Azure:** Azure Policy enforces encryption at rest for all storage accounts; Premium SSD with encryption

**Data in Transit:**
- **SOC2:** TLS 1.2 or higher for all data in transit
- **VPN (IPsec):** AES-256-GCM encryption, SHA-384 authentication, IKEv2, DH Group 20
- **VPN (SSL/TLS):** TLS 1.2 or 1.3, cipher suite TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, SHA-256 certificates, HSTS enabled
- **REST API:** Security headers include `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- **Azure:** ExpressRoute or Site-to-Site VPN with IKEv2 + IPsec encryption for hybrid connectivity

**Key Management:**
- **SOC2:** 90-day key rotation; separate keys by data classification; dedicated Key Management System (KMS)
- **SOC2 pitfall:** Never store encryption keys in configuration files or code repos - use environment variables or KMS
- **SOC2:** Automate certificate renewal at least 30 days before expiration
- **VPN:** Self-signed certificates with 90-day validity; certificate renewal scheduled 30 days before expiration; annual credential rotation

**Access Control for Encrypted Resources:**
- **GDPR:** Row-level security policies; role-based access (PERSONAL_DATA_HANDLER role with limited grants)
- **SOC2:** MFA for all administrative access; quarterly access reviews; 24-hour deprovisioning
- **Firewall Policies:** Database tier restricted to application subnet only (port 5432 from 10.1.20.0/24)

**Compliance Requirements:**
- **PCI-DSS:** Documented encryption protecting cardholder data
- **HIPAA:** Encryption with audit trails for protected health information
- **SOC2:** Type II audit requires 6+ months of operational logs proving encryption controls
- **GDPR:** Encryption is a required technical safeguard; failure can result in penalties up to EUR 20M or 4% of global revenue

**Sources:** GDPR Compliance Guide (TDE, AES-256, row-level security); SOC2 Requirements (TLS 1.2+, AES-256, key rotation, KMS); VPN Configuration (AES-256-GCM, IPsec, TLS); AWS Setup Guide (EBS encryption, encrypted RDS); Azure Migration Plan (encryption policy, ExpressRoute); REST API Design Guide (HSTS); Firewall Policies (PCI-DSS, HIPAA, SOC2 references)
</details>

---

### Q15: "What monitoring and alerting do we have?"

**Expected behavior:** Deliberately vague. The agent should primarily search Operations > Monitoring (Alerting Setup + Observability Guide) but may also pull from AWS (CloudWatch), Azure (Azure Monitor), and Deployment Checklist (post-deployment monitoring).

<details>
<summary>Expected Answer</summary>

Our monitoring and alerting spans several layers:

**Alert Architecture (Alerting Setup):**
- Pipeline: Data Collection > Rule Evaluation > State Management > Notification Routing > Escalation
- Core stack: Prometheus/CloudWatch (metrics), Alertmanager/PagerDuty (routing), Email/Slack/SMS (delivery)

**Key Alert Rules:**
- **HighMemoryUsage:** Memory >85% for 5 minutes (warning, platform team)
- **ServiceDown:** `up == 0` for 2 minutes (critical, backend team)
- **DiskSpaceCritical:** <10% free disk for 10 minutes (critical, infrastructure team)
- **HighErrorRate:** >5% HTTP 5xx errors for 5 minutes (critical)
- **PodMemoryUsageHigh:** Container memory >85% for 10 minutes (warning)

**Notification Routing:**
- Critical severity > PagerDuty (1-hour repeat interval)
- Warning severity > Slack (team-specific channels)
- Infrastructure alerts > Email (2-hour repeat)
- Inhibition rules: suppress HighLatency when ServiceDown is firing

**Observability Stack (Observability Guide):**
- **Metrics:** Prometheus with 15-second scrape interval; golden signals (latency, traffic, errors, saturation)
- **Logging:** Structured JSON logs; pipeline via Fluent Bit/Filebeat; tiered retention (15 days raw > 90 days 1-min > 1 year 5-min > indefinite 1-hour)
- **Tracing:** OpenTelemetry with OTLP receivers; Jaeger for storage; sampling: 100% errors, 100% slow (>1000ms), 10% probabilistic for high-volume
- **Dashboards:** Hierarchical - Status (red/yellow/green) > Service (golden signals) > Infrastructure (resources) > Investigative (detailed)

**Cloud-Specific Monitoring:**
- **AWS:** CloudWatch alarms (e.g., CPU >80% for 2 evaluation periods at 5-minute intervals), SNS notifications to `prod-alerts`
- **Azure:** Azure Monitor with VM metrics at 1-minute collection, 90-day retention; Log Analytics workspace for AzureActivity, SecurityEvent, Syslog

**Post-Deployment Monitoring (Deployment Checklist):**
- First 24 hours: increased log verbosity
- Alert thresholds set at 75% of critical limits
- Monitor: error rates, latency percentiles (p95, p99), resource utilization, business-critical metrics

**Alert Quality Metrics:**
- Alert volume, duration, false positive rate (target <5%), MTAA, MTTR

**Sources:** Alerting Setup (rules, routing, suppression); Observability Guide (metrics, logs, traces, dashboards); AWS Setup Guide (CloudWatch); Azure Migration Plan (Azure Monitor); Deployment Checklist (post-deployment monitoring)
</details>

---

### Q16: "How should we handle a critical vulnerability that's being actively exploited?"

**Expected behavior:** Primary focus on Security > Incident Response (Vulnerability Management + Incident Response Playbook), but should also touch SOC2 severity levels, and potentially Alerting Setup for detection.

<details>
<summary>Expected Answer</summary>

An actively exploited critical vulnerability triggers both the vulnerability management and incident response processes simultaneously:

**1. Detection and Escalation (Vulnerability Management):**
- Cross-reference against CISA Known Exploited Vulnerabilities (KEV) catalog
- Check commercial threat intelligence feeds and SIEM/IDS logs
- Use the CISA KEV checking script to match discovered CVEs against active exploitation list
- **Critical vulnerabilities (CVSS 9.0+) trigger immediate escalation:**
  1. Immediate notification to security incident response team
  2. Incident ticket creation within **15 minutes**
  3. Impact assessment meeting within **1 hour**
  4. Executive notification within **4 hours** (if customer data at risk)

**2. Activate Incident Response (Incident Response Playbook):**
- This is **Severity Level 1 (Critical)** per SOC2 classification - response within 15 minutes
- **Immediate containment:**
  - Network isolation: disable switch ports or move affected hosts to isolation VLAN 999
  - Endpoint isolation: disconnect from network, disable wireless
  - Credential reset: reset compromised accounts, force re-authentication
  - Block exploitation vectors at firewall and DNS
- **Evidence collection** (in order of volatility):
  1. Live system state: processes, memory, network connections
  2. Filesystem: disk images with hash verification
  3. Logs: system, application, auth logs

**3. Remediation (Vulnerability Management):**
- **Patch management workflow:**
  1. Patch release from vendor
  2. Testing phase (2-3 days - expedited for critical)
  3. Approval phase (1-2 days)
  4. Staging deployment (1-2 days)
  5. Production phased rollout
  6. Validation (re-scan 24-48 hours post-patch)
- Target: **7 days to production** for critical vulnerabilities
- **If no patch available**, implement compensating controls:
  - WAF rules to block malicious payloads
  - Network segmentation to limit exposure
  - Enhanced monitoring on affected systems
  - Document in remediation ticket with review date

**4. Validation and Closure:**
- Automated re-scanning 24-48 hours post-remediation
- Functional testing to confirm systems operate normally
- Regression testing to verify patch doesn't introduce new issues
- Recovery validation checklist: all malicious processes terminated, C2 blocked, patches verified, EDR updated, monitoring enabled

**5. Post-Incident (Incident Response Playbook):**
- Update detection signatures based on observed IOCs
- Enhance logging and monitoring for identified gaps
- Security awareness training
- Review and update access controls
- Document: executive summary, timeline, root cause analysis, impact assessment, lessons learned

**Stakeholder Notifications:**
- Executive leadership: within 4 hours of containment
- Legal/Compliance: immediately for breaches
- Affected users: within 24 hours
- Regulatory bodies: per requirements (72 hours for GDPR if personal data involved)
- Insurance provider: within 48 hours

**Key Metrics to Track:**
- MTTD < 7 days (vulnerability detection)
- MTTR < 7 days (critical vulnerability remediation)
- Remediation rate: 100% for critical
- False positive rate: < 5%
- Scan coverage: 100% of in-scope assets

**Sources:** Vulnerability Management (CVSS, CISA KEV, patch workflow, compensating controls); Incident Response Playbook (containment, evidence, recovery, notifications); SOC2 Requirements (severity levels, logging alerts)
</details>

---

## Scoring Guide

Use this rubric to evaluate the agent's responses:

| Criteria | Points | What to Look For |
|---|---|---|
| **Category Identification** | /3 | Did the agent call `list_categories` and identify the right category? |
| **Category Filtering** | /3 | Did `search_knowledge_base` use `category_ids` parameter? |
| **Relevant Chunks Retrieved** | /3 | Did the search results contain the right document/section? |
| **Context Expansion** | /3 | Did the agent use `get_chunk_context` or `get_document_overview`? |
| **Answer Accuracy** | /4 | Are the specific facts, numbers, and details correct? |
| **Cross-Document Synthesis** | /4 | For Tier 2+, did the answer combine information from multiple documents? |
| **Source Citation** | /2 | Did the agent cite document titles and sections? |
| **Total** | **/22** | |

**Tier expectations:**
- **Tier 1** (Q1-Q5): Should score 15+ with strong category filtering and accurate detail retrieval
- **Tier 2** (Q6-Q9): Should score 12+ with multi-document synthesis within or across categories
- **Tier 3** (Q10-Q13): Should score 10+ demonstrating true cross-category search and synthesis
- **Tier 4** (Q14-Q16): Evaluates judgment - agent should know when to search broadly vs. narrowly
