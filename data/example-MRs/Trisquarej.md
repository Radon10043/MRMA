```java
// Metamorphic Relation: Assume a', b', c' is the second triangle, if (a,b,c)=(b',a',c'), the output will not change.
// - Source input: The lengths of the three sides of a triangle: `a`, `b`, and `c`.
// - Input relation: Create a follow-up input by swapping the lengths of sides `a` and `b`.
// - Output relation: The result of `triangle_square` for the original and swapped inputs must be identical.
// - Rationale: The properties of a triangle (like its area and type) are independent of the order in which its side lengths are provided.

@ParameterizedTest
@MethodSource("testcaseProvider")
public void test1(int a, int b, int c) {
    /* Get source out */
    Pair<Integer, Double> source_out = TriSquareJ.triangle_square(a, b, c);

    /* Construct follow-up input */
    int follow_a = b, follow_b = a;

    /* Get follow-up output */
    Pair<Integer, Double> follow_out = TriSquareJ.triangle_square(follow_a, follow_b, c);

    /* Verification */
    assertEquals(source_out, follow_out);
}
```