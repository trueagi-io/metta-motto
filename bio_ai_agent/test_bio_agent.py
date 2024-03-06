import os
from pathlib import Path

from hyperon import MeTTa


def is_result_correct(result, correct_value):
    for item in result:
        if correct_value in repr(item):
            return True
    return False


def test_bioaiagent():
    pwd = Path(__file__).parent.parent
    os.chdir(pwd)
    m = MeTTa()
    requests_str = [

        '!(llm &bioaiagent (user "Find the transcripts of gene ENSG00000206014"))',
        '!(llm &bioaiagent (user "Get properties of gene ENSG00000279139"))',
        '!(llm &bioaiagent (user "What are the proteins that gene ENSG00000133710 codes for"))',
        '!(llm &bioaiagent (user "Find the Gene Ontology (GO) categories associated with protein Q13461"))',
        '!(llm &bioaiagent (user "Find the GO categories associated with gene ENSG00000186790"))',
        '!(llm &bioaiagent (user "Find biological process GO categories associated with gene ENSG00000186790"))',
        '!(llm &bioaiagent (user "Find pathways that gene ENSG00000000938 is a subset of"))',
        '''!(llm &bioaiagent (user
            "Find pathways that gene F13A1 is a subset of (use the gene HGNC symbol instead of ensembl id)"))''',
        '''!(llm &bioaiagent (user
            "Find parent pathways of the pathways that FGR  
            gene is a subset of (use the gene HGNC symbol instead of ensembl id)"))''',
        '!(llm &bioaiagent (user "What variants have eqtl association with gene HBM"))',
        '''!(llm &bioaiagent (user
            "What variants have eqtl association with gene HBM and return the properties of the association"))''',
        '!(llm &bioaiagent (user "Get properties of gene SNORD39"))',
        '!(llm &bioaiagent (user "Find the transcripts of gene LINC01409"))',
        '''!(llm &bioaiagent (user 
        "What variants have eqtl association with gene ENSG00000206177 and return the properties of the association"))''',
        '!(llm &bioaiagent (user "Find parent pathways of the pathways that ENSG00000000938  gene is a subset of"))'
    ]

    results = ["(transcript ENST00000533722)", "(gene_name ENSG00000279139)", "(protein Q9NQ38)",
               "(ontology_term GO:2001111)", "(ontology_term GO:0030154)", "(ontology_term GO:0002930)",
               "(pathway R-HSA-9664417)", "(pathway R-HSA-76002)", "(pathway R-HSA-9664407)",
               "(sequence_variant rs74001198)",
               "(p_value (eqtl (sequence_variant rs144775822) (gene ENSG00000206177)) 0.500688)", "(gene_name SNORD39)",
               "(transcript ENST00000443772)",
               "(p_value (eqtl (sequence_variant rs144775822) (gene ENSG00000206177)) 0.500688)",
               "(pathway R-HSA-9664407)"]
    # m.load_module_at_path('motto:sparql_gate')
    m.run("!(import! &self motto)")
    m.run(f'!(bind! &bioaiagent (Agent bio_ai_agent/bio_ai_agent.msa))')
    for i in range(len(requests_str)):
        result = m.run(requests_str[i], True)
        assert is_result_correct(result, results[i]), f"Incorrect result for {requests_str[i]}"


