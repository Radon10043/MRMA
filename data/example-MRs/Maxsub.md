```java
// Metamorphic Relation: Reversing input array, the output should be same.
// - Source input: An array of integers `arr`.
// - Input relation: Create `follow_arr` by reversing the order of elements in `arr`.
// - Output relation: `max_sub(follow_arr)` must equal `max_sub(arr)`.
// - Rationale: The maximum subarray sum is independent of the order of elements in the array.
@ParameterizedTest
@MethodSource("testcaseProvider")
public void test1(ArrayList<Integer> arr) {
    /* Get source output */
    int source_out = Maxsub.max_sub(arr);

    /* Construct follow-up input */
    ArrayList<Integer> follow_arr = new ArrayList<Integer>();
    follow_arr.addAll(arr);
    Collections.reverse(follow_arr);

    /* Get follow-up output */
    int follow_out = Maxsub.max_sub(follow_arr);

    /* Verification */
    assertEquals(source_out, follow_out);
}
```