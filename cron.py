import argparse
import re
from typing import Optional, Tuple, Dict

FIELD_RANGES = {
    'minute': (0, 59),
    'hour': (0, 23),
    'day_of_month': (1, 31),
    'month': (1, 12),
    'day_of_week': (0, 6)
}

def is_in_range(field: str, range_tuple: Tuple[int, int]) -> bool:
    """
    Checks if the field is within the specified range.
    
    Args:
        field (str): The field to check.
        range_tuple (tuple): A tuple containing the minimum and maximum values of the range.
    
    Returns:
        bool: True if the field is within the range, False otherwise.
    """
    if not isinstance(field, str) or not field:
        return False

    if field == '*':
        return True
    
    if field[0]=='-':
        return False
    
    if field.isdigit():
        value = int(field)
        if value < range_tuple[0] or value > range_tuple[1]:
            return False

    parts =  field.split(',')
    for part in parts:
        if part =='' or part == '/':
            return False
        elif '-' in part and '/' in part:
            if part.count('/') > 1 or part.count('-') > 1:
                return False
            range_part, step_part = part.split('/')
            if int(step_part)<=0 or int(step_part)>range_tuple[1]:
                return False
            
            range_start, range_end = range_part.split('-')
            if int(range_start) < range_tuple[0] or int(range_end) > range_tuple[1] or int(range_start) > int(range_end):
                return False
        elif '/' in part:
            if part.count('/') != 1:
                return False
            start, step = part.split('/')
            if int(step)<=0 or int(step) > range_tuple[1]:
                return False
            if start != '*' and start.isdigit() and ( int(start)< range_tuple[0] or int(start) > range_tuple[1]):
                return False
        elif '-' in part:
            if part.count('-') != 1:
                return False
            start, end = part.split('-')
            if int(start) < range_tuple[0] or int(end) > range_tuple[1] or int(start) > int(end):
                return False
        elif part == '*':
            continue
        else:
            if not part.isdigit() or int(part) < range_tuple[0] or int(part) > range_tuple[1]:
                return False

    return True

def validate_cron_expression(cron_expression: Dict[str, Optional[str]]) -> bool:
    """
    Validates a cron expression.
    
    Args:
        cron_expression (Dict[str, Optional[str]]): The cron object to validate.
    
    Returns:
        bool: True if the cron expression is valid, False otherwise.
        
    Note:
        Prints error messages to stdout when validation fails.
    """

    VALID_CRON_PATTERNS = [
        r'^\*$', # matches only asterisk
        r'^\d{1,4}$', # matches 1 to 4 digit numbers
        r'^(\d\,?)*$', # matches comma separated numbers
        r'^(\d)*-(\d)*$', # matches range of numbers
        r'^((\d)*-(\d)*)\/(\d)*$', # matches range with step, e.g., 1-5/2
        r'^((\d\,?)*)\/\d$', # matches values like 1,2,3/2 or 1/2
        r'^(((\d\,?)*)|\*)\/\d+$', # matches values like 1,2,3/2 or 1/2 or */1
        r'^(\d+(-\d+)?)(,(\d+(-\d+)?))*\/\d+$', # matches values like 1,2,3/2 or 1/2 or 1,2,3-6,9/2
        r'^(?:\*|\d+(?:-\d+)?)(?:,(?:\*|\d+(?:-\d+)?))*\/\d+$',  # matches values like 1,3,*/2 or 1-3,*/2 or *,1/2
        r'^(?:\*|\d+(?:-\d+)?)(?:,(?:\*|\d+(?:-\d+)?))*' # matches values like 0,15,30-45
    ]

    
    for field, value in cron_expression.items():
        if field == 'command':
            continue

        pattern_matched = False
        for pattern in VALID_CRON_PATTERNS:
            if value and re.match(pattern, value):
                pattern_matched = True
                break

        if not pattern_matched:
            print(f"Field '{field}' with value '{value}' does not match any valid pattern.")
            return False
        
        isInRange = is_in_range(value, FIELD_RANGES[field])
        if not isInRange:
            print(f"Field '{field}' with value '{value}' is out of range {FIELD_RANGES[field]} or step value is invalid.")
            return False

    
    return True

def parse_cron_expression(cron_expression: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Parses and validates a cron expression.
    
    Args:
        cron_expression (str): The cron expression to parse.
    
    Returns:
        Optional[Dict[str, Optional[str]]]: A dictionary containing the parsed components, or None if parsing fails.
    """
    if not cron_expression:
        print("Cron expression cannot be empty.")
        return None
    
    components = cron_expression.split()
    if len(components) < 5 :
        print("Cron expression must have minimum 5 fields.")
        return None
    
    cron_components = {
        "minute": components[0],
        "hour": components[1],
        "day_of_month": components[2],
        "month": components[3],
        "day_of_week": components[4],
        "command": None
    }

    if len(components) == 5:
        pass
    else:
        cron_components["command"] = ' '.join(components[5:])

    return cron_components

def generate_step_value(start: int, end: int, step: int) -> list[str]:
    """
    Generates a list of values with a given step size within a range.
    
    Args:
        start (int): The starting value of the range.
        end (int): The ending value of the range.
        step (int): The step size.
    
    Returns:
        list[str]: A list of string values within the range with the given step size.
        
    Raises:
        ValueError: If step size is less than 1.
    """
    if step < 1:
        raise ValueError("Step size must be a positive integer.")
    
    step_values = []
    for i in range(start, end + 1, step):
        step_values.append(str(i))
    return step_values

def expand_cron_field(field: str, value: str) -> str:
    """
    Expands a cron field value into all possible values.
    
    Args:
        field (str): The name of the cron field.
        value (str): The value of the cron field.
    
    Returns:
        str: A space-separated string of all possible values for the field.
    """
    cron_values = []
    if value == '*':
        for i in range(FIELD_RANGES[field][0], FIELD_RANGES[field][1] + 1):
            cron_values.append(str(i))
    
    else:
        parts = value.split(',')
        for part in parts:
            if '/' in part:
                step = int(part.split('/')[1])
                stepped_values = []
                if part[0] == '*':
                    stepped_values = generate_step_value(FIELD_RANGES[field][0], FIELD_RANGES[field][1], step)
                elif '-' in part:
                    range_part = part.split('/')[0]
                    start, end = range_part.split('-')
                    stepped_values = generate_step_value(int(start), int(end), step)
                    
                else:
                    stepped_values = generate_step_value(int(part.split('/')[0]), FIELD_RANGES[field][1], step)
                cron_values.extend(stepped_values)
            elif '-' in part:
                start, end = part.split('-')
                cron_values.extend(generate_step_value(int(start), int(end), 1))
            elif part == '*':
                cron_values.extend(generate_step_value(FIELD_RANGES[field][0], FIELD_RANGES[field][1], 1))
            else:
                cron_values.append(part)

    cron_values = list(set(cron_values))  # Remove duplicates
    cron_values.sort(key=int)  # Sort numerically
    return ' '.join(cron_values)


def display_cron_expression(cron_object: Dict[str, Optional[str]]) -> None:
    """
    Expands and displays the cron expression components.
    
    Note: This function modifies the input dictionary by expanding field values.
    
    Args:
        cron_object (Dict[str, Optional[str]]): The cron components to expand and display.
    """
    for key, value in cron_object.items():
        if value is not None and key != 'command':
            cron_object[key] = expand_cron_field(key, value)
            print(f"{key}: {cron_object[key]}")
        else:
            print(f"{key}: {value}")



def main():
    print("======================CRON PARSER======================")
    
    parser = argparse.ArgumentParser(description="Parse a cron expression and print its components.")
    parser.add_argument("cron_expression", type=str, help="The cron expression to parse.")
    args = parser.parse_args()

    try:
        print(f"Parsing cron expression: {args.cron_expression}")

        cron_object = parse_cron_expression(args.cron_expression)

        if cron_object is None:
            print("Failed to parse cron expression.")
            return

        if validate_cron_expression(cron_object):
            print("Cron expression is valid.")
            print("Parsed components:")
            display_cron_expression(cron_object)
        else:
            print("Cron expression is invalid.")
    except Exception as e:
        print(f"An error occurred while parsing the cron expression: {e}")

if __name__ == "__main__":
    main()
