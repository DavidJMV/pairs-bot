

from signals import generate_signal

# Define a set of test cases: (z-score, current position) → expected action
test_cases = [
    (2.5, 0, (-1, 'enter_short')),
    (-2.5, 0, ( 1, 'enter_long' )),
    ( 0.2,  1, ( 0, 'exit'       )),
    (-0.2, -1, ( 0, 'exit'       )),
    ( 3.5,  0, (-1, 'enter_short')),  # still enter at extreme
    ( 5.0,  1, ( 0, 'exit'       )),  # exit on |z| > max_threshold
    ( 0.0,  0, ( 0, None         )),  # no action if flat and inside band
]

# Run tests
for z, pos, expected in test_cases:
    result = generate_signal(z, pos)
    status = "PASS" if result == expected else "FAIL"
    print(f"Test z={z:4.1f}, pos={pos:+d}: got {result}, expected {expected} → {status}")
