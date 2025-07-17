```cpp
/**
 * @brief Metamorphic Relation: Adding one row with all 'O's to the end of the matrix, then the output should be increased by one row with all 'O's.
 * - Source input: A matrix of characters `source_vec`.
 * - Input relation: Create `follow_vec` by appending a row of 'O's to `source_vec`.
 * - Output relation: The output for `follow_vec` should be the same as the output for `source_vec`, but with an additional row of 'O's at the end.
 * - Rationale: 'O's on the border are never captured. Adding a row of 'O's to the border means they will remain 'O's in the output.
 *
 */
TEST_P(SurroundedRegionParamTest, MR1) {
    /* Get source input */
    SurroundedRegionInput input = GetParam();
    vector<string> source_vec = input.vec;

    /* Get source output */
    vector<string> source_out = surrounded_region(source_vec);

    /* Construct follow-up input */
    int cols = source_vec[0].length();
    vector<string> follow_vec = source_vec;
    follow_vec.push_back(string(cols, 'O'));

    /* Get follow-up output */
    vector<string> follow_out = surrounded_region(follow_vec);

    /* Verification */
    source_out.push_back(string(cols, 'O'));
    EXPECT_EQ(follow_out, source_out);
}
```