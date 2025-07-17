```java
// Metamorphic Relation: If the pattern occurred in the original text, adding one character to the end of the source text should result in the same output.
// - Source input: A text string `text` and a pattern string `pattern`.
// - Input relation: Create `text'` by appending an arbitrary character (e.g., 'x') to the end of the original `text`. The `pattern` remains unchanged.
// - Output relation: `Boyer.indexOf(text, pattern)` must equal `Boyer.indexOf(text', pattern)`.
// - Rationale: The Boyer-Moore algorithm searches for the first occurrence of a pattern. If the pattern already exists in the original text, appending characters to the end of the text does not alter the position of that initial occurrence, thus the index should remain the same. This relation applies only if the pattern is found in the original text.
@ParameterizedTest
@MethodSource("testcaseProvider")
public void test1(String text, String pattern) {
    if (text.indexOf(pattern) == -1) {
        return;
    }

    /* Get origin output */
    int origin_res = Boyer.indexOf(text, pattern);

    /* Construct follow-up input */
    String follow_text = text + "x";

    /* Get follow-up output */
    int follow_res = Boyer.indexOf(follow_text, pattern);

    /* Verification */
    assertTrue(follow_res == origin_res);
}
```