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