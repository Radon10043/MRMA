```cpp
/**
 * @brief Metamorphic Relation: Adding one integer to the source array, which is identical to one element of the original array, the output should be the same.
 * - Source input: An array of integers `source_vec`.
 * - Input relation: Create `follow_vec` by appending a duplicate of an existing element to `source_vec`.
 * - Output relation: `first_missing_positive(follow_vec)` must equal `first_missing_positive(source_vec)`.
 * - Rationale: The set of unique positive integers remains unchanged when a duplicate element is added, so the first missing positive integer should also remain the same.
 *
 */
TEST_P(FMPInputParamTest, MR1) {
    /* Get source input */
    FMPInput input = GetParam();
    vector<int> source_vec = input.vec;

    /* Get source output */
    int source_out = first_missing_positive(source_vec);

    /* Construct follow-up input */
    vector<int> follow_vec = source_vec;
    follow_vec.push_back(source_vec.front());

    /* Get follow-up output */
    int follow_out = first_missing_positive(follow_vec);

    /* Verification */
    EXPECT_EQ(source_out, follow_out);
}
```