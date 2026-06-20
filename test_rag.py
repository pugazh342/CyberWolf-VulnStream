from rag.chain import CyberWolfRAGPipeline

def run_tests():
    pipeline = CyberWolfRAGPipeline()

    print("\n⚡ TEST 1: Semantic Search (No Hard Filter)")
    q1 = "Tell me about vulnerabilities that let an attacker execute arbitrary code"
    ans1 = pipeline.execute_analysis(q1)
    print(f"\nResponse:\n{ans1}\n")

    print("\n⚡ TEST 2: Hard Metadata Filter (CISA KEV Only)")
    q2 = "What do we know about Apache?"
    # Only retrieve documents that came out of CISA KEV
    filter2 = {"source": "CISA_KEV"}
    ans2 = pipeline.execute_analysis(q2, metadata_filter=filter2)
    print(f"\nResponse:\n{ans2}\n")

    print("\n⚡ TEST 3: Evaluation Guardrails (Testing Hallucination Protection)")
    q3 = "What is the remediation for Windows Kernel exploit CVE-2024-9999?"
    ans3 = pipeline.execute_analysis(q3)
    print(f"\nResponse:\n{ans3}\n")

if __name__ == "__main__":
    run_tests()