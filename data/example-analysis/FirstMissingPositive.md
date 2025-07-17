user:

```cpp
/**
 * @brief Metamorphic Relation: Adding one integer to the source array, which is identical to one element of the original array, the output should be the same.
 * - Source input: An array of integers `source_vec`.
 * - Input relation: Create `follow_vec` by appending a duplicate of an existing element to `source_vec`.
 * - Output relation: `first_missing_positive(follow_vec)` must equal `first_missing_positive(source_vec)`.
 * - Rationale: The set of unique positive integers remains unchanged when a duplicate element is added, so the first missing positive integer should also remain the same.
 *
 */
TEST_P(FMPInputParamTest, MR1) {
    /* Get source input */
    FMPInput input = GetParam();
    vector<int> source_vec = input.vec;

    /* Get source output */
    int source_out = first_missing_positive(source_vec);

    /* Construct follow-up input */
    vector<int> follow_vec = source_vec;
    follow_vec.push_back(source_vec.front());

    /* Get follow-up output */
    int follow_out = first_missing_positive(follow_vec);

    /* Verification */
    EXPECT_EQ(source_out, follow_out);
}
```

assistant:

Let's analyze the metamorphic relation candidate you provided step by step.

1. Source Input Analysis
The source input for the Software Under Test (SUT), the `first_missing_positive` function, is a `vector<int>` named `source_vec`. The function is designed to find the smallest positive integer that is not present in the vector.

The SUT is expected to handle any `vector<int>`, including those with negative numbers, zeros, duplicates, and unsorted elements. Therefore, any `vector<int>` provided by the test parameter generator is a **valid** input. The test case has a minor precondition that the source vector must not be empty, so that `source_vec.front()` is a valid operation.

2. Input Relation Analysis
The input relation generates a follow-up input (`follow_vec`) by appending a duplicate of the first element (`source_vec.front()`) of the source vector to itself.

This input transformation is **valid**. It produces another `vector<int>`, which is an acceptable input for the SUT. This action directly models the "addition of a duplicate element," which is the core of the metamorphic relation.

3. Output Relation Analysis
The output relation asserts that the result from the source input (`source_out`) must be identical to the result from the follow-up input (`follow_out`).

This output relation is **correct**.

  * **Rationale**: The `first_missing_positive` function's logic is based on the **set of unique positive integers** present in the input array. For example, the arrays `[1, 3, 4]`, `[1, 3, 4, -5, 0]`, and `[1, 1, 3, 4, 3]` all contain the same set of unique positive integers: `{1, 3, 4}`. The first missing positive integer for all of them is `2`.
  * When the follow-up input is created by adding a duplicate of an existing element, the set of unique positive integers within the array does not change.
  * Since the underlying set of relevant numbers is identical for both the source and follow-up inputs, the algorithm's output, which depends solely on this set, must also be identical.
  * Therefore, the assertion `source_out == follow_out` is guaranteed to hold.

In summary, I think the provided metamorphic relation candidate is:

```
valid
```

