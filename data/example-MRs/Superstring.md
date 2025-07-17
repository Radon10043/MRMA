```java
// Metamorphic Relation: Adding one string A to the array, and A must be contained in the original array, then the output should be the same.
// - Source input: An array of strings `arr`.
// - Input relation: Create `follow_arr` by adding a duplicate of an existing string to `arr`.
// - Output relation: `shortest_superstring(follow_arr)` must equal `shortest_superstring(arr)`.
// - Rationale: Adding a duplicate string does not introduce any new information to be covered by the superstring, so the shortest superstring remains the same.
@ParameterizedTest
@MethodSource("testcaseProvider")
public void test1(ArrayList<String> arr) {
    /* Get source output */
    String source_out = Superstring.shortest_superstring(arr);

    /* Construct follow-up input */
    ArrayList<String> follow_arr = new ArrayList<String>();
    follow_arr.addAll(arr);
    follow_arr.add(follow_arr.getFirst());

    /* Get follow-up output */
    String follow_out = Superstring.shortest_superstring(follow_arr);

    /* Verification */
    assertEquals(source_out, follow_out);
}
```