# Semantic Web CI/CD: Automated Ontology Testing & Release Framework

This repository establishes a modern, continuous integration and deployment (CI/CD) pipeline for ontology engineering. It applies traditional software engineering patterns—such as compilation testing, syntax linting, structural type-checking, functional unit testing, and automated generation of visual dashboards—to Semantic Web artifacts.

---

## 🚀 Architectural Vision & Test Stack

Ontology testing and deployment are mapped across four distinct validation and publishing layers inside a fully automated pipeline:

```
[ Git Push / PR / Tag ]│▼┌───────────┐      ❌ Fail (Exit 3) ──► [ Halt Build ]│  Phase 1  │ ─── Description Logic (DL) Compilation Test└─────┬─────┘      (Owlready2 + HermiT Reasoner Engine)│ Pass▼┌───────────┐      ❌ Fail (Exit 2) ──► [ Warn / Alert ]│  Phase 2  │ ─── Data Integrity & Structural Linting└─────┬─────┘      (SHACL Constraints Verification)│ Pass▼┌───────────┐      ❌ Fail (Exit 6) ──► [ Halt Build ]│  Phase 2a │ ─── Naming Convention Syntax Linter└─────┬─────┘      (RegEx CamelCase / camelCase Enforcement)│ Pass▼┌───────────┐      ❌ Fail (Exit 1) ──► [ Halt Build ]│  Phase 3  │ ─── Functional Unit Testing└─────┬─────┘      (SPARQL Competency Question Verification)│ Pass▼┌───────────┐│  Phase 4  │ ─── Living Documentation & Visual Graph Engine└───────────┘      (pyLODE HTML Portal + WebVOWL Interactive Graph)

```

### 1. Phase 1: Semantic Reasoner Compilation (Logic Check)
*   **Engine:** `Owlready2` + **HermiT Description Logic (DL) Reasoner**.
*   **Purpose:** Ensures the graph is logically sound. Contradictory class assertions are classified into `owl:Nothing` (unsatisfiable), automatically breaking the build.

### 2. Phase 2: SHACL Structural Integrity (Type Checking)
*   **Engine:** `pyshacl`
*   **Purpose:** Validates instance data geometry (e.g., enforcing that every `ex:Patient` node contains exactly one valid integer for vital metrics).

### 3. Phase 2a: Naming Convention Linter (Syntax Formatting)
*   **Engine:** Custom Native Python RegEx
*   **Purpose:** Enforces clean, predictable vocabularies across distributed teams. 
    *   **Classes** must strictly follow **`CamelCase`** (e.g., `BloodPressureMeasurement`).
    *   **Properties** must strictly follow **`camelCase`** (e.g., `hasMeasurement`, `systolic`).

### 4. Phase 3: SPARQL Competency Questions (Unit Assertions)
*   **Engine:** `rdflib`
*   **Purpose:** Evaluates controlled mock profiles against target conditions to assert that business and clinical data logic return exact expected outputs.

### 5. Phase 4: Automated Documentation & Living Dashboards
*   **Engine:** `pylode` + **WebVOWL Integration**
*   **Purpose:** Generates a human-readable web experience. When code moves to the main branch, a static website is compiled and deployed to GitHub Pages.

---

## 📂 Project Structure

```text
├── .github/
│   └── workflows/
│       └── ontology_ci.yml     # GitHub Actions fully-automated CI/CD script
├── healthcare_ontology.ttl    # Core ontology asset (Schema, SHACL Shapes, Mock Data)
├── validate_ontology.py       # Python pipeline driver orchestrating linting & tests
├── visual.html                # Client template wrapper for the WebVOWL graph engine
└── README.md                  # System documentation
```

---

## 🌐 Living Documentation & Interactive Dashboards

When changes are merged into the `main` branch or a formal release tag is pushed, the system automatically builds and hosts two distinct documentation planes on **GitHub Pages**:

*   **Interactive Specification Sheets (pyLODE)**:  
    `https://<your-username>.github.io/<your-repository-name>/index.html`
*   **Visual Knowledge Graph Node-Link Model (WebVOWL)**:  
    `https://<your-username>.github.io/<your-repository-name>/graph.html`

---

## 🏷️ Automated Semantic Versioning (Releases)

This framework treats ontology updates identically to software versioning milestones (MAJOR.MINOR.PATCH):
*   **Patch Changes (`1.0.1`)**: Text cleanups or metadata documentation adjustments (`rdfs:comment`).
*   **Minor Changes (`1.1.0`)**: Backwards-compatible schema additions (e.g., a brand new class).
*   **Major Changes (`2.0.0`)**: Structural modifications that disrupt existing queries (e.g., modifying domain rules).

### How to Create a Versioned Release
To push a formal version release, tag your git snapshot from your local machine terminal:
```bash
# 1. Label the local commit history snapshot
git tag v1.2.0

# 2. Push the version tag to GitHub
git push origin v1.2.0
```
**Behind the Scenes:** The GitHub Actions pipeline will intercept the tag, dynamically inject the version metadata (`owl:versionInfo` and `owl:versionIRI`) into the ontology header via Python, compile the production file, and automatically draft a formal **GitHub Release** attaching the standalone `.ttl` asset.

---

## 🛠️ Local Development & Debugging

Ensure you have a **Java Runtime Environment (JRE)** (required by HermiT) and Python 3.11+ configured locally.

### 1. Install Dependencies
```bash
pip install rdflib pyshacl owlready2 pylode
```

### 2. Run Verification Suite
```bash
python validate_ontology.py
```

### 3. Pipeline Exit Directory Reference
*   `0`: Absolute Success
*   `1`: SPARQL Competency Unit Test Failure
*   `2`: SHACL Validation Violation
*   `3`: Reasoner Consistency Contradiction
*   `5`: pyLODE Documentation Compilation Failure
*   `6`: Naming Linter Format Exception