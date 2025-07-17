```cpp
/**
 * @brief Metamorphic Relation: Adding one same character to the end of A and C, the result will be the same.
 * - Source input: Three strings `A`, `B`, and `C`.
 * - Input relation: Create `A'` by appending a character to `A`, and `C'` by appending the same character to `C`.
 * - Output relation: `is_interleaved(A', B, C')` must equal `is_interleaved(A, B, C)`.
 * - Rationale: If `C` is an interleaving of `A` and `B`, then appending the same character to both `A` and `C` preserves the interleaving property.
 *
 */
TEST_P(InterleavingStringParamTest, MR1) {
    /* Get source input */
    InterleavingStringInput input = GetParam();
    string A = input.A, B = input.B, C = input.C;

    /* Get source output */
    bool source_out = is_interleaved(A, B, C);

    /* Construct follow-up input */
    char ch = 'a';
    string follow_A = A + ch, follow_C = C + ch;

    /* Get follow-up output */
    bool follow_out = is_interleaved(follow_A, B, follow_C);

    /* Verification */
    EXPECT_EQ(source_out, follow_out);
}
```