```cpp
/**
 * @brief Metamorphic Relation: Adding a new point to the set cannot increase the minimum distance.
 * - Source input: A set of 2D points `vec`.
 * - Input relation: Create a new set `vec'` by adding an arbitrary point to `vec`.
 * - Output relation: `closest_distance(vec')` must be less than or equal to `closest_distance(vec)`.
 * - Rationale: The original set of point pairs is a subset of the new, larger set of pairs. The minimum distance found within a superset cannot be greater than the minimum distance found within its subset.
 *
 */
TEST_P(ClosestPairParamTest, MR1) {
    /* Get source input */
    ClosestPairInput input = GetParam();
    vector<pair<int, int>> vec = input.vec;

    /* Get source output */
    float source_out = closest_distance(vec);

    /* Construct follow-up input */
    vector<pair<int, int>> follow_vec = vec;
    follow_vec.push_back({100, 100});

    /* Get follow-up output */
    float follow_out = closest_distance(follow_vec);

    /* Verification */
    EXPECT_GE(source_out, follow_out);
}
```