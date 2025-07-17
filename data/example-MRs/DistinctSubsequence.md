```cpp
/**
 * @brief Metamorphic Relation: Add a character to the end of s, the output should be the same or larger.
 * - Source input: A string `s` and a string `t`.
 * - Input relation: Create `s'` by appending an arbitrary character to `s`.
 * - Output relation: `numDistinct(s', t)` must be greater than or equal to `numDistinct(s, t)`.
 * - Rationale: Appending a character to `s` can only increase or maintain the number of ways `t` can be formed as a subsequence, as all original subsequences are preserved.
 *
 */
TEST_P(DistinctSubsequenceParamTest, MR1) {
    /* Get source input */
    DistinctSubsequenceInput input = GetParam();
    string s = input.s, t = input.t;

    /* Get source output */
    int source_out = numDistinct(s, t);

    /* Construct follow-up input */
    string follow_s = s.append("a");

    /* Get follow-up output */
    int follow_out = numDistinct(follow_s, t);

    /* Verification */
    EXPECT_GE(follow_out, source_out);
}
```