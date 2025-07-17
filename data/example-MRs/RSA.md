```cpp
/**
 * @brief Metamorphic Relation: Keeping p, q and e the same, giving a new plaintext which is equals to m + p*q, the ciphertext is the same.
 * - Source input: A message `m`, and RSA parameters `e`, `p`, `q`.
 * - Input relation: Create a new message `follow_m = m + p * q`.
 * - Output relation: `candp(follow_m, e, p, q)` must equal `candp(m, e, p, q)`.
 * - Rationale: Due to the modular arithmetic properties of RSA, `(m + p*q) mod (p*q)` is equivalent to `m mod (p*q)`, resulting in the same ciphertext.
 *
 */
TEST_P(RSAParamTest, MR1) {
    /* Get source input */
    RSAInput input = GetParam();
    int m = input.m, e = input.e, p = input.p, q = input.q;

    /* Get source output */
    long long source_out = candp(m, e, p, q);

    /* Construct follow-up input */
    int follow_m = m + p * q;

    /* Get follow-up output */
    long long follow_out = candp(follow_m, e, p, q);

    /* Verification */
    ASSERT_EQ(source_out, follow_out);
}
```