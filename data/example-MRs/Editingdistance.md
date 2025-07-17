```cpp
/**
 * @brief Metamorphic Relation: Add a character to the end of str1 (the character is not exist in str2), the output should be the same or larger.
 * - Source input: Two strings, `str1` and `str2`.
 * - Input relation: Create `str1'` by appending a character to `str1` that does not appear in `str2`.
 * - Output relation: `edit_dist(str1', str2)` must be greater than or equal to `edit_dist(str1, str2)`.
 * - Rationale: Appending a character to `str1` that is absent in `str2` increases the dissimilarity, thus the edit distance can only increase or stay the same.
 *
 */
TEST_P(EditingdistanceParamTest, MR1) {
    /* Get source input */
    EditingdistanceInput input = GetParam();
    string str1 = input.str1, str2 = input.str2;

    /* Get source output */
    int source_out = edit_dist(str1, str2);

    /* Construct follow-up input */
    char c = 'a';
    while (c <= 'z' && str2.find(c) != string::npos)
        c++;
    if (c > 'z')
        return;
    string follow_str1 = str1 + c;

    /* Get follow-up output */
    int follow_out = edit_dist(follow_str1, str2);

    /* Verification */
    EXPECT_GE(follow_out, source_out);
}
```