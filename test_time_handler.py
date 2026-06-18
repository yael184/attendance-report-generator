"""
Test script for time format handling.
This tests the new time_handler utilities without needing OCR dependencies.
"""

import sys
sys.path.insert(0, 'd:\\יעל\\practicode\\attendance-report-generator')

from utils.time_handler import normalize_time, is_valid_time_format, is_valid_hours_value

def test_normalize_time():
    """Test the normalize_time function with various formats."""
    test_cases = [
        # (input, expected_output, description)
        ("6.30", "06:30", "Dot format - single digit hour"),
        ("18.30", "18:30", "Dot format - double digit hour"),
        ("6:30", "06:30", "Colon format - single digit hour"),
        ("18:30", "18:30", "Colon format - double digit hour"),
        ("630", "06:30", "No separator - 3 digits"),
        ("1830", "18:30", "No separator - 4 digits"),
        ("8:04", "08:04", "Colon with leading zero needed"),
        ("8.04", "08:04", "Dot with leading zero needed"),
    ]
    
    print("=" * 60)
    print("Testing normalize_time function")
    print("=" * 60)
    
    all_passed = True
    for input_val, expected, description in test_cases:
        result = normalize_time(input_val)
        passed = result == expected
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | {description}")
        print(f"     Input: {input_val} -> Output: {result} (Expected: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_is_valid_time_format():
    """Test the is_valid_time_format function."""
    test_cases = [
        # (input, expected_result, description)
        ("6.30", True, "Valid dot format"),
        ("18.30", True, "Valid dot format"),
        ("6:30", True, "Valid colon format"),
        ("18:30", True, "Valid colon format"),
        ("630", True, "Valid 3-digit format"),
        ("1830", True, "Valid 4-digit format"),
        ("25.30", False, "Invalid hour (25)"),
        ("18.70", False, "Invalid minute (70)"),
        ("350", True, "Valid - could be 3-digit"),
        ("3.5", False, "Invalid minute (5 - too short)"),
        ("11:08", True, "Valid time format"),
        ("297", True, "Valid - could be time"),
    ]
    
    print("\n" + "=" * 60)
    print("Testing is_valid_time_format function")
    print("=" * 60)
    
    all_passed = True
    for input_val, expected, description in test_cases:
        result = is_valid_time_format(input_val)
        passed = result == expected
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | {description}")
        print(f"     Input: {input_val} -> Result: {result} (Expected: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_is_valid_hours_value():
    """Test the is_valid_hours_value function."""
    test_cases = [
        # (input, expected_result, description)
        ("6.50", True, "Valid hours (6.5)"),
        ("350", True, "Valid hours in centminutes (3.5)"),
        ("288", True, "Valid hours in centminutes"),
        ("1440", True, "Valid max hours (1440 minutes)"),
        ("0", True, "Valid zero hours"),
        ("11:08", False, "Invalid - time format"),
        ("25", False, "Invalid - too high for hours"),
        ("1500", False, "Invalid - exceeds 1440"),
    ]
    
    print("\n" + "=" * 60)
    print("Testing is_valid_hours_value function")
    print("=" * 60)
    
    all_passed = True
    for input_val, expected, description in test_cases:
        result = is_valid_hours_value(input_val)
        passed = result == expected
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | {description}")
        print(f"     Input: {input_val} -> Result: {result} (Expected: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    results = []
    
    results.append(("normalize_time", test_normalize_time()))
    results.append(("is_valid_time_format", test_is_valid_time_format()))
    results.append(("is_valid_hours_value", test_is_valid_hours_value()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED!")
        sys.exit(1)
