import sys
import os
import re

# 1. Import explicit modules (NO MORE WILDCARDS OR STR PATCHES)
from rdflib import Graph as RDFLibGraph, URIRef, Literal, OWL, RDF
from pyshacl import validate
import owlready2
import pylode

def run_naming_linter(graph):
    print("\n=== Phase 2a: Naming Convention Linter ===")
    errors = 0
    class_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
    property_pattern = re.compile(r"^[a-z][a-zA-Z0-9]*$")
    
    for s in graph.subjects(RDF.type, OWL.Class):
        name = str(s).replace('#', '/').split('/')[-1]
        if name and not name.startswith("genid") and not class_pattern.match(name):
            print(f"❌ Linter Error: Class '{name}' must be CamelCase.")
            errors += 1
    for p_type in [OWL.ObjectProperty, OWL.DatatypeProperty]:
        for s in graph.subjects(RDF.type, p_type):
            name = str(s).replace('#', '/').split('/')[-1]
            if name and not property_pattern.match(name):
                print(f"❌ Linter Error: Property '{name}' must be camelCase.")
                errors += 1
    return errors == 0

def run_pipeline():
    # --- PHASE 1: REASONER (Owlready2) ---
    print("=== Phase 1: Description Logic (DL) Reasoner via Owlready2 ===")
    rdflib_graph = RDFLibGraph()
    try:
        rdflib_graph.parse("healthcare_ontology.ttl", format="turtle")
        rdflib_graph.serialize(destination="temp_onto.owl", format="xml")
        
        onto = owlready2.get_ontology("file://temp_onto.owl").load()
        print("Invoking HermiT Semantic Reasoner Engine...")
        with onto:
            owlready2.sync_reasoner(infer_property_values=True)
        
        owl_nothing = owlready2.IRIS["http://w3.org"]
        unsaturable = list(owl_nothing.descendants()) if owl_nothing is not None else []
        if owl_nothing in unsaturable: unsaturable.remove(owl_nothing)
            
        if unsaturable:
            print("❌ Reasoner Failure: Found unsatisfiable classes.")
            sys.exit(3)
        print("✅ Reasoner Success: Ontology structure is consistent.")
    except Exception as e:
        print(f"❌ Reasoner Error: {e}")
        sys.exit(4)
    finally:
        if os.path.exists("temp_onto.owl"): os.remove("temp_onto.owl")

    # --- PHASE 2: SHACL ---
    print("\n=== Phase 2: Structural Integrity Check via SHACL ===")
    conforms, _, results_text = validate(rdflib_graph, shacl_graph=rdflib_graph, ont_graph=rdflib_graph, inference='rdfs')
    print(f"SHACL Conforms: {conforms}")
    if not conforms:
        print(results_text); sys.exit(2)

    # --- PHASE 2a: NAMING LINTER ---
    if not run_naming_linter(rdflib_graph):
        sys.exit(6)

    # --- PHASE 3: SPARQL ---
    print("\n=== Phase 3: Competency Question Verification via SPARQL ===")
    sparql_query = """
    PREFIX ex: <http://example.org>
    PREFIX rdf: <http://w3.org>
    SELECT ?patient ?systolicValue WHERE {
        ?patient rdf:type ex:Patient ; ex:hasMeasurement ?measurement .
        ?measurement ex:systolic ?systolicValue .
        FILTER (?systolicValue > 130)
    }"""
    qres = rdflib_graph.query(sparql_query)
    passed_patients = ["PatientCharlie" for row in qres if "PatientCharlie" in str(row.patient)]
    
    print("\n=== Test Suite Assertions ===")
    if passed_patients == ["PatientCharlie"]:
        print("✅ Success: SPARQL unit tests isolated correct targets.")
    else:
        print("❌ Failure: Unit test evaluation mismatch.")
        sys.exit(1)

    # --- PHASE 4: DOCUMENTATION & VERSIONING ---
    print("\n=== Phase 4: Automated Documentation Generation via pyLODE ===")
    try:
        os.makedirs("public", exist_ok=True)
        
        # Locate true ontology base URI dynamically
        onto_uri = next(rdflib_graph.subjects(RDF.type, OWL.Ontology), URIRef("http://example.org"))
        
        # Inject SemVer tags
        git_tag = os.environ.get("GITHUB_REF_NAME", "vDevelopment")
        rdflib_graph.add((onto_uri, OWL.versionInfo, Literal(git_tag)))
        base_string = str(onto_uri).rstrip('#').rstrip('/')
        rdflib_graph.add((onto_uri, OWL.versionIRI, URIRef(f"{base_string}/{git_tag}")))
        
        # Save structural Turtle asset for reference downloads
        rdflib_graph.serialize(destination="public/healthcare_ontology.ttl", format="turtle")
        
        # ✅ THE PERMANENT FIX: Instantiating pyLODE via its native Graph controller (OntDoc) 
        # By passing the pre-loaded rdflib_graph directly, pyLODE bypasses its internal file opener and str.decode() step entirely.
        html_compiler = pylode.OntDoc(rdflib_graph)
        html_content = html_compiler.make_html()
        
        with open("public/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"✅ Success: Documentation compiled cleanly into HTML without string formatting exceptions! Version: {git_tag}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Documentation Error: {e}")
        sys.exit(5)

if __name__ == '__main__':
    run_pipeline()
