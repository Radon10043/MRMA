```cpp
/**
 * @brief Metamorphic Relation: Adding a useless key row (all 0s, these cannot open any lock) to the end of the matrix, then the output will not change.
 * - Source input: A matrix `matrix` representing keys and locks.
 * - Input relation: Create `follow_matrix` by appending a row of zeros to `matrix`.
 * - Output relation: `KLP(follow_matrix)` must equal `KLP(source_out)`.
 * - Rationale: A key represented by a row of zeros cannot open any locks, so adding it to the set of available keys does not change the solution to the key-lock problem.
 *
 */
TEST_P(KLPParamTest, MR1) {
    /* Get source input */
    KLPInput input = GetParam();
    vector<vector<int>> matrix = input.matrix;

    /* Get source output */
    vector<int> source_out = KLP(matrix);

    /* Construct follow-up input */
    vector<vector<int>> follow_matrix = matrix;
    follow_matrix.push_back(vector<int>(follow_matrix[0].size()));

    /* Get follow-up output */
    vector<int> follow_out = KLP(follow_matrix);

    /* Verification */
    EXPECT_EQ(source_out, follow_out);
}
```