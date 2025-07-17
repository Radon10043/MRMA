```java
// Metamorphic Relation: Add the number of days and seconds with the same length of time to the input time, the output will be the same.
// - Source input: A `DateTime` object `time` and a number of days `days`.
// - Input relation: Calculate the equivalent number of seconds `seconds = days * 24 * 60 * 60`.
// - Output relation: `time.plusDays(days)` must be equal to `time.plusSeconds(seconds)`.
// - Rationale: Adding a duration in days should be equivalent to adding the same duration in seconds.

@ParameterizedTest
@MethodSource("testcaseProvider1")
public void test1(DateTime time, int days) {
    /* Get source output */
    DateTime source_out = time.plusDays(days);

    /* Construct follow-up input */
    int seconds = days * 24 * 60 * 60;

    /* Get follow-up output */
    DateTime follow_out = time.plusSeconds(seconds);

    /* Verification */
    assertTrue(source_out.equals(follow_out));
}
```