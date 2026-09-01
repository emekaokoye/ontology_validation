import sys
from rdflib import Graph
from pyshacl import validate
import pylode

def run_pipeline():
    print("=== Loading Ontology Data ===")
    g = Graph()
    # Ensure healthcare_ontology.ttl is in the same runtime folder
    g.parse("healthcare_ontology.ttl", format="turtle")
    
    print("\n=== Phase 1: Structural Integrity Check via SHACL ===")
    # Validates data triples using integrated shapes and RDFS sub-class inferences
    conforms, results_graph, results_text = validate(
        data_graph=g,
        shacl_graph=g,
        ont_graph=g,
        inference='rdfs'
    )
    
    print(f"SHACL Conforms: {conforms}")
    if not conforms:
        print("Data integrity issues found! Review details below:")
        print(results_text)
    
    print("\n=== Phase 2: Competency Question Verification via SPARQL ===")
    sparql_query = """
    PREFIX ex: <http://example.org>
    PREFIX rdf: <http://w3.org>
    
    SELECT ?patient ?systolicValue
    WHERE {
        ?patient rdf:type ex:Patient ;
                 ex:hasMeasurement ?measurement .
        ?measurement ex:systolic ?systolicValue .
        FILTER (?systolicValue > 130)
    }
    """
    
    qres = g.query(sparql_query)
    
    print("Patients matching CQ (Systolic > 130):")
    passed_patients = []
    for row in qres:
        patient_uri = str(row.patient)
        print(f" - {patient_uri} (Systolic: {row.systolicValue})")
        
        # Check for the expected local name inside the full URI string
        if "PatientCharlie" in patient_uri:
            passed_patients.append("PatientCharlie")
        else:
            # Fallback to keep track of unexpected matches for debugging
            passed_patients.append(patient_uri)
        
    # Assertions for Unit Test outcome tracking
    expected_matches = ["PatientCharlie"]
    actual_matches = sorted(passed_patients)
    
    print("\n=== Test Suite Assertions ===")
    if actual_matches == sorted(expected_matches):
        print("✅ Success: SPARQL unit tests isolated the correct functional targets.")
    else:
        print(f"❌ Failure: Expected {expected_matches}, but identified {actual_matches}")
        sys.exit(1) # Break CI build on unit test functional failure
        
    if not conforms:
        print("\n⚠️ Pipeline Finished with non-blocking schema infractions.")
        sys.exit(2) # Warnings or alert levels can be configured here
    else:
        print("\n🚀 Pipeline Finished Cleanly!")
        sys.exit(0) # Standard exit code signaling absolute build green

    print("\n=== Phase 4: Automated Documentation Generation via pyLODE ===")
    try:
        # Create output distribution directory for GitHub Pages host compilation
        os.makedirs("public", exist_ok=True)
        
        # Invoke pyLODE template compiler engine on the base Turtle file
        html_doc = pylode.PylodeHtml(ontology="healthcare_ontology.ttl")
        html_doc.render(destination="public/index.html")
        
        print("✅ Success: Human-readable documentation successfully written to public/index.html")
        print("\n🚀 Pipeline Finished Cleanly across all Validation and Publishing Targets!")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Documentation Error: Failed to auto-generate HTML templates: {e}")
        sys.exit(5) # Set explicit exit fallback error code target
        

if __name__ == '__main__':
    run_pipeline()
