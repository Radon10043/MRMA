```py
@parameterized.expand(gen_tcs_randomly)
def test1(self, img: np.array, angle: float):
    """Metamorphic Relation: Rotating the same image by N degree and N+360 degree will output the same result.
    - Source input: An image `img` and a rotation angle `angle`.
    - Input relation: Create `follow_angle = angle + 360`.
    - Output relation: `ndimage.rotate(img, follow_angle)` must be identical to `ndimage.rotate(img, angle)`.
    - Rationale: Rotating an image by 360 degrees returns it to its original orientation, so adding a 360-degree rotation should not change the final result.
    """
    # Get source output
    source_out = ndimage.rotate(img, angle)

    # Construct follow-up input
    follow_angle = angle + 360

    # Get follow-up output
    follow_out = ndimage.rotate(img, follow_angle)

    # Verification
    self.assertTrue(np.allclose(source_out, follow_out))
```