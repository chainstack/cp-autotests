EMPTY_STRING_CASES = ["", " ", "  ", "\t", "\n", "\r"]
NONSTRING_CASES = [123, True, None, [123], {"key": "value"}, [1, 2, 3], 123.45]
NONINTEGER_CASES = [True, None, [123], {"key": "value"}, (1,2,3), {1,2,3}, 123.45, "123", "null", "true", "false"]
WEAK_PASSWORD_CASES = ["123", "abcd", "password", "12345678", "qwerty123", "PASSWORD123", "p@ssword123"]

INVALID_UUID_CASES = ["invalid-uuid", "00000000-0000-0000-0000-000000000000", "123e4567-e89b-12d3-a456-426614174000"]