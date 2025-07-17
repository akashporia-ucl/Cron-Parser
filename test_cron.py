import pytest
import sys
from cron import (
    is_in_range, validate_cron_expression, parse_cron_expression,
    generate_step_value, expand_cron_field, display_cron_expression, main,
    FIELD_RANGES
)
from unittest.mock import patch

# Tests for is_in_range
def test_is_in_range_with_single_value():
    """Test valid single minute value"""
    assert is_in_range('5', FIELD_RANGES['minute']) == True
    assert is_in_range(1, FIELD_RANGES['minute']) == False
    assert is_in_range('*', FIELD_RANGES['minute']) == True
    assert is_in_range('60', FIELD_RANGES['minute']) == False

def test_is_in_range_with_list_values():
    """Test valid list hour values"""
    assert is_in_range('1,2,3', FIELD_RANGES['hour']) == True
    assert is_in_range('1,2,61', FIELD_RANGES['hour']) == False
    assert is_in_range('1,2,3,4', FIELD_RANGES['hour']) == True
    assert is_in_range('1,2,3,*', FIELD_RANGES['hour']) == True

def test_is_in_range_with_range_values():
    """Test valid range month values"""
    assert is_in_range('1-5', FIELD_RANGES['month']) == True
    assert is_in_range('5-1', FIELD_RANGES['month']) == False
    assert is_in_range('1-60', FIELD_RANGES['month']) == False
    assert is_in_range('3-1', FIELD_RANGES['month']) == False

def test_is_in_range_with_step_values():
    """Test valid step day_of_week values"""
    assert is_in_range('*/5', FIELD_RANGES['day_of_week']) == True
    assert is_in_range('5/-2', FIELD_RANGES['day_of_week']) == False
    assert is_in_range('100/2', FIELD_RANGES['day_of_week']) == False
    assert is_in_range('100/0', FIELD_RANGES['day_of_week']) == False

def test_is_in_range_with_step_and_range_values():
    """Test valid step and range day_of_month values"""
    assert is_in_range('1-5/2', FIELD_RANGES['day_of_month']) == True
    assert is_in_range('5-1/2', FIELD_RANGES['day_of_month']) == False
    assert is_in_range('1-60/5', FIELD_RANGES['day_of_month']) == False
    assert is_in_range('1-5/0', FIELD_RANGES['day_of_week']) == False

def test_is_in_range_with_list_step_range_values():
    """Test valid list, step, and range minute values"""
    assert is_in_range('1,2,3-5/2', FIELD_RANGES['minute']) == True
    assert is_in_range('1,2,3-5/0', FIELD_RANGES['minute']) == False
    assert is_in_range('1,2,3-5/3', FIELD_RANGES['minute']) == True
    assert is_in_range('1-4,5,13-25/6', FIELD_RANGES['minute']) == True

def test_is_in_range_with_invalid_values():
    """Test for invalid  values"""
    assert is_in_range('', FIELD_RANGES['minute']) == False
    assert is_in_range('-1', FIELD_RANGES['hour']) == False
    assert is_in_range('a', FIELD_RANGES['month']) == False
    assert is_in_range('1//2', FIELD_RANGES['day_of_week']) == False
    assert is_in_range('2,,3', FIELD_RANGES['day_of_month']) == False
    assert is_in_range('2--3', FIELD_RANGES['day_of_month']) == False
    assert is_in_range('2--3/2', FIELD_RANGES['day_of_month']) == False


# Tests for validate_cron_expression

def test_validate_cron_expression_valid():
    """Test valid cron expression"""
    expected_cron_object = {
        'minute': '5',
        'hour': '0',
        'day_of_month': '*',
        'month': '*',
        'day_of_week': '*',
        'command': None
    }
    actual_cron_object = parse_cron_expression('5 0 * * *')

    assert actual_cron_object == expected_cron_object
    assert validate_cron_expression(actual_cron_object) == True

def test_validate_cron_expression_valid_with_command():
    """Test valid cron expression with command"""
    expected_cron_object = {
        'minute': '5',
        'hour': '0',
        'day_of_month': '*',
        'month': '*',
        'day_of_week': '*',
        'command': 'echo "Hello, World!"'
    }
    actual_cron_object = parse_cron_expression('5 0 * * * echo "Hello, World!"')

    assert actual_cron_object == expected_cron_object
    assert validate_cron_expression(actual_cron_object) == True

@patch('builtins.print')
def test_validate_cron_expression_invalid_minute(mock_print):
    """Test invalid cron expression"""
    expected_cron_object = {
        'minute': 'a',
        'hour': '0',
        'day_of_month': '*',
        'month': '*',
        'day_of_week': '*',
        'command': None
    }
    actual_cron_object = parse_cron_expression('a 0 * * *')

    assert actual_cron_object == expected_cron_object
    assert validate_cron_expression(actual_cron_object) == False
    mock_print.assert_called_with("Field 'minute' with value 'a' does not match any valid pattern.")

@patch('builtins.print')
def test_validate_cron_expression_out_of_range_minute(mock_print):
    """Test invalid cron expression"""
    expected_cron_object = {
        'minute': '61',
        'hour': '0',
        'day_of_month': '*',
        'month': '*',
        'day_of_week': '*',
        'command': None
    }
    actual_cron_object = parse_cron_expression('61 0 * * *')

    assert actual_cron_object == expected_cron_object
    assert validate_cron_expression(actual_cron_object) == False
    mock_print.assert_called_with(f"Field 'minute' with value '61' is out of range {FIELD_RANGES['minute']} or step value is invalid.")

# Tests for parse_cron_expression
def test_parse_cron_expression_valid():
    """Test valid cron expression parsing"""
    cron_expression = '5 0 * * *'
    expected_cron_object = {
        'minute': '5',
        'hour': '0',
        'day_of_month': '*',
        'month': '*',
        'day_of_week': '*',
        'command': None
    }
    assert parse_cron_expression(cron_expression) == expected_cron_object

def test_parse_cron_expression_valid_with_command():
    """Test valid cron expression parsing with command"""
    cron_expression = '5 0 * * * echo "Hello, World!"'
    expected_cron_object = {
        'minute': '5',
        'hour': '0',
        'day_of_month': '*',
        'month': '*',
        'day_of_week': '*',
        'command': 'echo "Hello, World!"'
    }
    assert parse_cron_expression(cron_expression) == expected_cron_object

def test_parse_cron_expression_invalid():
    """Test invalid cron expression parsing empty and too few fields"""
    empty_cron_expression = ''
    few_cron_expression = '5 0 *'
    expected_empty_cron_object = None
    expected_few_cron_object = None
    assert parse_cron_expression(empty_cron_expression) == expected_empty_cron_object
    assert parse_cron_expression(few_cron_expression) == expected_few_cron_object

# Tests for generate_step_value
def test_generate_step_value_valid():
    """Test valid step value generation"""
    assert generate_step_value(1, 10, 2) == ['1', '3', '5', '7', '9']
    assert generate_step_value(0, 5, 1) == ['0', '1', '2', '3', '4', '5']
    assert generate_step_value(0, 10, 5) == ['0', '5', '10']

def test_generate_step_value_invalid():
    """Test invalid step value generation"""
    assert generate_step_value(10, 1, 2) == []
    assert generate_step_value(5, 5, 1) == ['5']

# Tests for expand_cron_field
def test_expand_cron_field_valid():
    """Test valid cron field expansion"""
    assert expand_cron_field('minute', '5') == '5'
    assert expand_cron_field('hour', '1,2,3') == '1 2 3'
    assert expand_cron_field('day_of_month', '3-5') == '3 4 5'
    assert expand_cron_field('month', '*') == '1 2 3 4 5 6 7 8 9 10 11 12'
    assert expand_cron_field('day_of_week', '*/3') == '0 3 6'
    assert expand_cron_field('minute', '1-5/2') == '1 3 5'
    assert expand_cron_field('day_of_week', '1,*') == '0 1 2 3 4 5 6'
    assert expand_cron_field('day_of_month', '1/10') == '1 11 21 31'

# Tests for display_cron_expression
@patch('builtins.print')
def test_display_cron_expression(mock_print):
    """Test displaying cron expression"""
    cron_object = {
        'minute': '5',
        'hour': '0',
        'day_of_month': '3-10/3',
        'month': '1,2,3',
        'day_of_week': '*',
        'command': None
    }
    display_cron_expression(cron_object)
    mock_print.assert_any_call('minute: 5')
    mock_print.assert_any_call('hour: 0')
    mock_print.assert_any_call('day_of_month: 3 6 9')
    mock_print.assert_any_call('month: 1 2 3')
    mock_print.assert_any_call('day_of_week: 0 1 2 3 4 5 6')
    mock_print.assert_any_call('command: None')

# Tests for main function
@patch('sys.argv', ['cron.py', '5 0 * * * echo "Hello, World!"'])
@patch('builtins.print')
def test_main_valid_expression(mock_print):
    """Test main function with valid cron expression"""
    main()
    
    mock_print.assert_any_call("======================CRON PARSER======================")
    mock_print.assert_any_call('Parsing cron expression: 5 0 * * * echo "Hello, World!"')
    mock_print.assert_any_call("Cron expression is valid.")
    mock_print.assert_any_call("Parsed components:")
    mock_print.assert_any_call('minute: 5')
    mock_print.assert_any_call('hour: 0')
    mock_print.assert_any_call('day_of_month: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31')
    mock_print.assert_any_call('month: 1 2 3 4 5 6 7 8 9 10 11 12')
    mock_print.assert_any_call('day_of_week: 0 1 2 3 4 5 6')
    mock_print.assert_any_call('command: echo "Hello, World!"')

@patch('sys.argv', ['cron.py', 'invalid'])
@patch('builtins.print')
def test_main_invalid_expression(mock_print):
    """Test main function with invalid cron expression"""
    main()
    
    mock_print.assert_any_call("======================CRON PARSER======================")
    mock_print.assert_any_call('Parsing cron expression: invalid')
    mock_print.assert_any_call("Cron expression must have minimum 5 fields.")
    mock_print.assert_any_call("Failed to parse cron expression.")

@patch('sys.argv', ['cron.py', '61 0 * * *'])
@patch('builtins.print')
def test_main_validation_failure(mock_print):
    """Test main function with expression that fails validation"""
    main()
    
    mock_print.assert_any_call("======================CRON PARSER======================")
    mock_print.assert_any_call('Parsing cron expression: 61 0 * * *')
    mock_print.assert_any_call("Field 'minute' with value '61' is out of range (0, 59) or step value is invalid.")
    mock_print.assert_any_call("Cron expression is invalid.")

if __name__ == '__main__':
    pytest.main([__file__])