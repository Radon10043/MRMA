```java
// Metamorphic Relation: Adding one row, the output should be the same as or larger than the original one.
// - Source input: A binary matrix `matrix`.
// - Input relation: Create `follow_matrix` by adding a new row of ones to `matrix`.
// - Output relation: `maximalRectangle(follow_matrix)` must be greater than or equal to `maximalRectangle(matrix)`.
// - Rationale: Adding a row of ones can only increase or maintain the area of the largest rectangle of ones.
@ParameterizedTest
@MethodSource("testcaseProvider")
public void test1(ArrayList<ArrayList<Integer>> matrix) {
    /* Get source output */
    int source_out = MaxRectangle.maximalRectangle(matrix);

    /* Construct follow-up input */
    int col_num = matrix.get(0).size();
    ArrayList<Integer> nrow = new ArrayList<Integer>(Collections.nCopies(col_num, 1));
    ArrayList<ArrayList<Integer>> follow_matrix = new ArrayList<ArrayList<Integer>>();
    follow_matrix.addAll(matrix);
    follow_matrix.add(nrow);

    /* Get follow-up output */
    int follow_out = MaxRectangle.maximalRectangle(follow_matrix);

    /* Verification */
    assertTrue(follow_out >= source_out);
}
```