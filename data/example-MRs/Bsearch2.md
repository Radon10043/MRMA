```cpp
/**
 * @brief Metamorphic Relation: Multiplying all the numbers (including the numbers in the array and the searching number), then the output should be the same.
 * Source input: A sorted array `vec` and a target `x`.
 * Input relation: Create `vec'` and `x'` by multiplying `vec` and `x` by a positive constant.
 * Output relation: `bin_search(vec, x)` must equal `bin_search(vec', x')`.
 * Rationale: The algorithm's logic depends on ordinal relationships, which are preserved under uniform scaling.
 *
 */
TEST_P(BSearchParamTest, MR1) {
    /* Get source input */
    BSearch2Input input = GetParam();
    vector<int> vec = input.vec;
    int target = input.target;

    /* Get source output */
    int source_out = bin_search(vec, target);

    /* Construct follow-up input */
    int constant = 2;
    vector<int> follow_vec = vec;
    for (int &val : follow_vec)
        val *= constant;
    int follow_target = target * constant;

    /* Get follow-up output */
    int follow_out = bin_search(follow_vec, follow_target);

    /* Verification */
    EXPECT_EQ(source_out, follow_out);
}
```