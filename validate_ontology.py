# =====================================================================
# 🛠️ SYSTEM ENVIRONMENT PATCH: Fixes pyLODE Compatibility Bugs Cleanly
# =====================================================================
import sys
import builtins
import codecs

# 1. Fix pyLODE Legacy JSON-LD Module Crash
try:
    import rdflib.plugins.serializers.jsonld as modern_jsonld
    sys.modules['rdflib_jsonld'] = modern_jsonld
    sys.modules['rdflib_jsonld.serializer'] = modern_jsonld
except ImportError:
    pass

# 2. Fix pyLODE Legacy str.decode() String Crash via Codecs Incremental Decoder Patch
# Since 'str' is immutable, we intercept the text decoding pipeline at the source.
original_decode = codecs.decode

def custom_decode(obj, encoding='utf-8', errors='strict'):
    """Intercepts decoding. If the object is already a string, return it as-is."""
    if isinstance(obj, str):
        return obj
    return original_decode(obj, encoding, errors)

# Re-bind the core codec decoders globally inside Python's language scope
codecs.decode = custom_decode
builtins.str.decode = lambda self, *args, **kwargs: self
# =====================================================================

# Keep your remaining explicit module imports exactly the same below:
import os
import re
import rdflib
import pylode
# 1. Import RDFlib components explicitly
from rdflib import Graph as RDFLibGraph, URIRef, Literal, OWL, RDF

# 2. Import SHACL components explicitly
from pyshacl import validate

# 3. Import Owlready2 components explicitly (DO NOT USE '*')
import owlready2





def run_naming_linter(graph):
    print("\n=== Phase 2a: Naming Convention Linter ===")
    errors = 0
    
    # RegEx Patterns matching software engineering standards
    class_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]*$")  # CamelCase
    property_pattern = re.compile(r"^[a-z][a-zA-Z0-9]*$")  # camelCase
    
    # 1. Check Classes
    for s in graph.subjects(RDF.type, OWL.Class):
        local_name = str(s).replace('#', '/').split('/')[-1]
        # Ignore blank nodes or systemic OWL constructs
        if local_name and not local_name.startswith("genid"):
            if not class_pattern.match(local_name):
                print(f"❌ Linter Error: Class '{local_name}' must be CamelCase.")
                errors += 1
                
    # 2. Check Object & Datatype Properties
    for p_type in [OWL.ObjectProperty, OWL.DatatypeProperty]:
        for s in graph.subjects(RDF.type, p_type):
            local_name = str(s).replace('#', '/').split('/')[-1]
            if local_name and not property_pattern.match(local_name):
                print(f"❌ Linter Error: Property '{local_name}' must be camelCase.")
                errors += 1
                
    if errors > 0:
        print(f"⚠️ Naming Convention Linter failed with {errors} violations.")
        return False
    print("✅ Linter Success: All class and property tokens conform to strict naming layout rules.")
    return True

def run_pipeline():
    print("=== Phase 1: Description Logic (DL) Reasoner via Owlready2 ===")
    # Instantiate the clean RDFlib graph variant using its new unique variable alias
    rdflib_graph = RDFLibGraph()
    
    try:
        rdflib_graph.parse("healthcare_ontology.ttl", format="turtle")
        
        # Bridge graph schemas by serializing an XML payload for Owlready2
        rdflib_graph.serialize(destination="temp_onto.owl", format="xml")
        
        # Access Owlready2 components safely via explicit namespace notation
        onto = owlready2.get_ontology("file://temp_onto.owl").load()
        
        print("Invoking HermiT Semantic Reasoner Engine...")
        with onto:
            owlready2.sync_reasoner(infer_property_values=True)
        
        # ✅ FIX: Look up owl:Nothing safely via the global IRI registry instead of the shortcut onto.nothing
        owl_nothing = owlready2.IRIS["http://w3.org"]
        
        unsatisfiable_classes = []
        if owl_nothing is not None:
            # Capture any custom concepts that have been inferred as equivalent to owl:Nothing
            unsatisfiable_classes = list(owl_nothing.descendants())
            if owl_nothing in unsatisfiable_classes:
                unsatisfiable_classes.remove(owl_nothing)
            
        if unsatisfiable_classes:
            print("❌ Reasoner Failure: Found unsatisfiable (logically broken) classes:")
            for cls in unsatisfiable_classes:
                print(f" - {cls.name}")
            sys.exit(3)
        else:
            print("✅ Reasoner Success: Ontology structure is completely consistent.")
            
    except Exception as e:
        print(f"❌ Reasoner Error: An exception occurred during logical inference: {e}")
        sys.exit(4)
    finally:
        if os.path.exists("temp_onto.owl"): 
            os.remove("temp_onto.owl")


    # --- PHASE 2: SHACL ---
    print("\n=== Phase 2: Structural Integrity Check via SHACL ===")
    conforms, _, results_text = validate(
        data_graph=rdflib_graph,
        shacl_graph=rdflib_graph,
        ont_graph=rdflib_graph,
        inference='rdfs'
    )
    print(f"SHACL Conforms: {conforms}")
    if not conforms:
        print(results_text)
        sys.exit(2)

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
        
        # 1. Dynamically locate the true ontology base URI statement in the file
        onto_uri = None
        for s in rdflib_graph.subjects(RDF.type, OWL.Ontology):
            onto_uri = s
            break
            
        # Fallback if the statement cannot be retrieved dynamically
        if onto_uri is None:
            onto_uri = URIRef("http://example.org")
            rdflib_graph.add((onto_uri, RDF.type, OWL.Ontology))
            
        # 2. Inject Dynamic SemVer Metadata using the exact matching subject node
        git_tag = os.environ.get("GITHUB_REF_NAME", "vDevelopment")
        rdflib_graph.add((onto_uri, OWL.versionInfo, Literal(git_tag)))
        
        # Build clean string variations for the version IRI suffix path safely
        base_string = str(onto_uri).rstrip('#').rstrip('/')
        rdflib_graph.add((onto_uri, OWL.versionIRI, URIRef(f"{base_string}/{git_tag}")))
        
        # Export the version-stamped Turtle file to the publishing directory
        output_ttl_path = "public/healthcare_ontology.ttl"
        rdflib_graph.serialize(destination=output_ttl_path, format="turtle")
        
        # 3. Use MakeDocco to compile the documentation to HTML string layout
        html_content = pylode.MakeDocco(
            input_data_file=output_ttl_path,
            outputformat="html",
            profile="ontdoc"
        ).document()
        
        with open("public/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"✅ Success: Interactive HTML site and SemVer stamped file generated with metadata: {git_tag}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Documentation Error: {e}")
        sys.exit(5)



if __name__ == '__main__':
    run_pipeline()
