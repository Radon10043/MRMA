```cpp
/**
 * @brief Metamorphic Relation: Reversing the source and destination vertices, the length of the shortest path should be the same.
 * - Source input: A set of edges `source_edges`, a source vertex `source_src`, a destination vertex `source_dst`, and the number of vertices `source_n`.
 * - Input relation: Create a follow-up input by swapping the source and destination vertices.
 * - Output relation: `shortest_path(source_edges, follow_src, follow_dst, source_n)` must equal `shortest_path(source_edges, source_src, source_dst, source_n)`.
 * - Rationale: In an undirected graph, the shortest path from a source to a destination is the same length as the path from the destination to the source.
 *
 */
TEST_P(SpwikiParamTest, MR1) {
    /* Get source input */
    SpwikiInput input = GetParam();
    vector<vector<int>> source_edges = input.edges;
    int source_src = input.src, source_dst = input.dst, source_n = input.n;

    /* Get source output */
    int source_out = shortest_path(source_edges, source_src, source_dst, source_n);

    /* Construct follow-up input */
    int follow_src = source_dst, follow_dst = source_src;

    /* Get follow-up output */
    int follow_out = shortest_path(source_edges, follow_src, follow_dst, source_n);

    /* Verification */
    EXPECT_EQ(follow_out, source_out);
}
```