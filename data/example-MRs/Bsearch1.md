```cpp
/**
 * @brief Metamorphic Relation: If we search for a number `x` and then for `x+1`, and both numbers exist in the array, the starting index of `x+1` must be greater than or equal to the ending index of `x` plus one.
 * - Source input: A sorted array `vec` and a target `x`.
 * - Input relation: Create a new target `x' = x + 1`, while the array `vec` remains unchanged.
 * - Output relation: Let `[start, end]` be the output for `get_range(vec, x)` and `[start', end']` be the output for `get_range(vec, x')`. If both `x` and `x'` are found (i.e., `start != -1` and `start' != -1`), then it must hold that `start' >= end + 1`.
 * - Rationale: Because the input array is sorted, all occurrences of `x` must precede all occurrences of `x+1`. Therefore, the last position of `x` must be less than the first position of `x+1`.
 *
 */
TEST_P(GetRangeParamTest, MR1) {
    /* Get source input */
    GetRangeInput input = GetParam();
    vector<int> vec = input.vec;
    int target = input.target;

    /* Get source output */
    vector<int> source_out = get_range(vec, target);

    if (source_out[0] == -1 && source_out[1] == -1)
        return;

    /* Construct follow-up input */
    int follow_target = target + 1;

    /* Get follow-up output */
    vector<int> follow_out = get_range(vec, follow_target);
    if (follow_out[0] == -1 && follow_out[1] == -1)
        return;

    /* Verification */
    EXPECT_LE(source_out[1] + 1, follow_out[0]);
}
```