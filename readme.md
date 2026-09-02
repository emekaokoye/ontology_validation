# Semantic Web CI/CD: Automated Ontology Testing Framework

This repository establishes a modern, continuous integration (CI) pipeline for ontology engineering. It applies traditional software engineering test patterns—such as compilation testing, schema linting, and functional unit testing—to Semantic Web artifacts.

By treating the ontology as application code, this framework ensures that structural updates, new axioms, or mock datasets do not introduce logical inconsistencies or break downstream queries.

---

## 🚀 Architectural Vision & Test Stack

Ontology testing is mapped across three distinct validation layers inside a fully automated pipeline:
```
[ Git Push / PR ]
	│
	▼
┌───────────┐      ❌ Fail (Exit 3) ──► [ Halt Build ]
│  Phase 1  │ ─── Description Logic (DL) Compilation Test
└─────┬─────┘      (Owlready2 + HermiT Reasoner Engine)
│ Pass
▼
┌───────────┐      ❌ Fail (Exit 2) ──► [ Warn / Alert ]
│  Phase 2  │ ─── Data Integrity & Structural Linting
└─────┬─────┘      (SHACL Constraints Type-Checking)
│ 
Pass
▼
┌───────────┐      ❌ Fail (Exit 1) ──► [ Halt Build ]
│  Phase 3  │ ─── Functional Unit Testing
└───────────┘      (SPARQL Competency Question Verification)
```

### 1. Phase 1: Semantic Reasoner Compilation (Logic Check)
*   **Tool:** `Owlready2` wrapping the **HermiT Description Logic (DL) Reasoner**.
*   **Purpose:** Ensures the graph is logically sound. If any developer creates contradictory class assertions, the reasoner catches the conflict, classifies the entities into `owl:Nothing` (unsatisfiable), and halts the deployment pipeline immediately.

### 2. Phase 2: SHACL Structural Integrity (Type Checking)
*   **Tool:** `pyshacl`
*   **Purpose:** Validates instance data (ABox) geometry against explicit rules. For instance, it enforces that every `ex:Patient` class node has at least one associated `ex:BloodPressureMeasurement` node containing integer datatype properties.

### 3. Phase 3: SPARQL Competency Questions (Unit Assertions)
*   **Tool:** `rdflib`
*   **Purpose:** Validates that the ontology meets business requirements. It translates textual **Competency Questions (CQs)** into execution scripts to assert that queries return exact, expected data matrices against controlled mock data profiles.

---

## 📂 Project Structure

```text
├── .github/
│   └── workflows/
│       └── ontology_ci.yml     # GitHub Actions workflow script
├── healthcare_ontology.ttl    # Core ontology asset (Schema, SHACL Shapes, Mock Data)
├── validate_ontology.py       # Python pipeline driver orchestrating tests
└── README.md                  # System documentation
```

---

## 🛠️ Getting Started (Local Development)

To run the verification suite on your machine before pushing code alterations to your remote repository, ensure you have a **Java Runtime Environment (JRE)** installed (required by the HermiT reasoner engine under the hood) along with Python 3.11+.

### 1. Install Dependencies
```bash
pip install rdflib pyshacl owlready2
```

### 2. Execute the Pipeline Driver
```bash
python validate_ontology.py
```

### 3. Understanding Engine Exit Codes
The script sets strategic shell environment return codes to inform orchestrators of precise runtime boundaries:
*   `0`: Complete success (Structure and data matches logic definitions flawlessly).
*   `1`: Functional Unit Test Failure (SPARQL target mismatches).
*   `2`: Structural Shape Deviation (SHACL validation errors found).
*   `3`: Logical Contradiction Fatal (Reasoner found unsatisfiable compilation errors).

---

## 🤖 Automated CI/CD (GitHub Actions)

The included `.github/workflows/ontology_ci.yml` pipeline runs on every **Push** or **Pull Request** targeting the `main` or `master` branches. 

It handles environment allocation by provisioning a clean Ubuntu shell container, setting up a Python layer, instantiating a Java Environment for HermiT compatibility, installing requirements, and running the test suite automatically. Any pipeline step returning a non-zero exit code stops the branch merge process.

---

## 🌐 Living Documentation Platform

When updates are successfully merged into the `main` branch, the pipeline automatically runs **pyLODE** to generate interactive, human-readable HTML documentation. 

This output is hosted natively on **GitHub Pages** at:
`https://<your-username>.github.io/<your-repository-name>/`

### Documentation Annotations Rule
To ensure high-quality documentation output, always label every new ontology class, property, and relationship using explicit metadata annotations:
*   `rdfs:label`: For the clean human-readable name of the component.
*   `rdfs:comment`: For a detailed textual description explaining why the component exists.


## ✍️ Contribution Workflow

When working with this ontology repo, remember to preserve the testing loop boundaries:
1. **Branch Out:** Always cut a feature branch (`feature/your-addition`) from `main`.
2. **Include Mock Data:** If you introduce a new feature or property type, write a corresponding valid and invalid mock profile inside `healthcare_ontology.ttl`.
3. **Write an Assertion:** Add corresponding testing loops inside `validate_ontology.py` to ensure the entity evaluates cleanly under verification metrics.
4. **Submit PR:** Confirm that GitHub Actions shows a passing green checkmark before requesting peer review.
