```java
// Metamorphic Relation: Swapping the terms of a OR or AND operator in the query should not affect the results.
// - Source input: A list of search terms `search_terms`.
// - Input relation: If the query is a binary operation (e.g., A OR B), create `follow_search_terms` by swapping the operands (e.g., B OR A).
// - Output relation: The search results for the original and swapped queries must be identical.
// - Rationale: The logical operators AND and OR are commutative, so the order of operands does not affect the outcome.
@ParameterizedTest
@MethodSource("testcaseProvider")
public void test1(String index_dir, ArrayList<String> search_terms) throws Exception {
    /* Get source output */
    ArrayList<String> source_out = Utils.fullTextSearch(index_dir, search_terms);

    /* Construct follow-up input */
    ArrayList<String> follow_search_terms = new ArrayList<String>();
    follow_search_terms.addAll(search_terms);
    if (search_terms.size() == 3 && (search_terms.get(1).equals("OR") || search_terms.get(1).equals("AND"))) {
        Collections.swap(follow_search_terms, 0, 2);
    }

    /* Get follow-up output */
    ArrayList<String> follow_out = Utils.fullTextSearch(index_dir, follow_search_terms);

    /* Verification */
    assertEquals(source_out, follow_out);
}
```