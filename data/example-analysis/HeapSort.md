user:

```cpp
/**
 * @brief Metamorphic Relation: Shuffling the elements in the input array, the output will be the same.
 * - Source input: An array of integers `source_vec`.
 * - Input relation: Create `follow_vec` by shuffling the elements of `source_vec`.
 * - Output relation: `heap_sort(follow_vec)` must equal `heap_sort(source_vec)`.
 * - Rationale: A sorting algorithm should produce the same sorted array regardless of the initial order of elements.
 *
 */
TEST_P(HeapSortParamTest, MR1) {
    /* Get source input */
    HeapSortInput input = GetParam();
    vector<int> source_vec = input.vec;

    /* Get source output */
    vector<int> source_out = heap_sort(source_vec);

    /* Construct follow-up input */
    vector<int> follow_vec = source_vec;
    shuffle(follow_vec.begin(), follow_vec.end(), random_device());

    /* Get follow-up output */
    vector<int> follow_out = heap_sort(follow_vec);

    /* Verification */
    EXPECT_EQ(follow_out, source_out);
}
```

assistant:

Let's analyze the metamorphic relation candidate you provided step by step.

1. Source Input Analysis
The source input for the Software Under Test (SUT), the `heap_sort` function, is a `vector<int>` named `source_vec`. The function is designed to sort this vector in non-decreasing order.

The SUT is expected to handle any `vector<int>`, including those with duplicates, negative numbers, or pre-sorted elements. Therefore, any `vector<int>` provided by the test parameter generator is a **valid** input.

2. Input Relation Analysis
The input relation generates a follow-up input (`follow_vec`) by creating a copy of the source vector and then shuffling its elements randomly.

This input transformation is **valid**. It produces another `vector<int>` with the exact same multiset of elements, just in a different permutation. This is a perfect way to test the core property of a sorting algorithm.

3. Output Relation Analysis
The output relation asserts that the result from sorting the source input (`source_out`) must be identical to the result from sorting the shuffled follow-up input (`follow_out`).

This output relation is **correct**.

  * **Rationale**: The fundamental definition of a sorting algorithm is that it takes a collection of items and arranges them into a specific order (e.g., non-decreasing). The final sorted output depends only on the **multiset of elements** in the input collection, not on their initial permutation.
  * Shuffling the input vector changes its permutation but does not change the multiset of elements it contains.
  * Therefore, any correct sorting algorithm must produce the exact same sorted vector for both the original and the shuffled inputs.
  * The assertion `EXPECT_EQ(follow_out, source_out)` correctly verifies this essential property.

In summary, I think the provided metamorphic relation candidate is:

```
valid
```