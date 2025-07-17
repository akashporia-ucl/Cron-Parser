# Cron Parser

A Python-based command-line tool for parsing and validating cron expressions. This tool expands cron expressions into their constituent time values and validates them against standard cron syntax rules.

## Features

-   **Parse cron expressions**: Breaks down cron expressions into their individual components
-   **Validate syntax**: Ensures cron expressions follow proper formatting rules
-   **Expand values**: Shows all possible values for each time field
-   **Range validation**: Verifies that all values are within valid ranges
-   **Command support**: Handles optional command portions of cron expressions
-   **Comprehensive error handling**: Provides detailed error messages for invalid expressions

## Installation

No additional dependencies required beyond Python 3.6+. The tool uses only standard library modules.

```bash
git clone https://github.com/akashporia-ucl/Cron-Parser.git
cd cron-parser
```

## Usage

### Basic Usage

```bash
python3 cron.py "0 22 * * 1-5 /usr/bin/find"
```

### Command Line Interface

The tool accepts a single argument - the cron expression to parse:

```bash
python3 cron.py "<cron_expression>"
```

### Example Outputs

**Simple cron expression:**

```bash
python3 cron.py "0 22 * * 1-5"
```

Output:

```
======================CRON PARSER======================
Parsing cron expression: 0 22 * * 1-5
Cron expression is valid.
Parsed components:
minute: 0
hour: 22
day_of_month: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
month: 1 2 3 4 5 6 7 8 9 10 11 12
day_of_week: 1 2 3 4 5
command: None
```

**With step values:**

```bash
python3 cron.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

Output:

```
======================CRON PARSER======================
Parsing cron expression: */15 0 1,15 * 1-5 /usr/bin/find
Cron expression is valid.
Parsed components:
minute: 0 15 30 45
hour: 0
day_of_month: 1 15
month: 1 2 3 4 5 6 7 8 9 10 11 12
day_of_week: 1 2 3 4 5
command: /usr/bin/find
```

## Cron Expression Format

The tool supports standard 5-field cron expressions with optional command:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Monday to Sunday)
│ │ │ │ │
│ │ │ │ │
* * * * * [command]
```

### Supported Syntax

-   **Asterisk (`*`)**: Matches all values
-   **Numbers**: Specific values (e.g., `5`)
-   **Ranges**: Range of values (e.g., `1-5`)
-   **Lists**: Comma-separated values (e.g., `1,3,5`)
-   **Steps**: Step values (e.g., `*/2`, `1-10/2`)
-   **Combinations**: Mix of above (e.g., `1,3,*/2`)

### Field Ranges

| Field        | Range | Description            |
| ------------ | ----- | ---------------------- |
| minute       | 0-59  | Minutes                |
| hour         | 0-23  | Hours (24-hour format) |
| day_of_month | 1-31  | Day of the month       |
| month        | 1-12  | Month                  |
| day_of_week  | 0-6   | Day of week (0=Monday) |

## Functions Overview

### Core Functions

-   [`parse_cron_expression()`](cron.py): Parses cron string into components
-   [`validate_cron_expression()`](cron.py): Validates parsed cron expression
-   [`expand_cron_field()`](cron.py): Expands field values to show all possibilities
-   [`display_cron_expression()`](cron.py): Displays formatted output

### Utility Functions

-   [`is_in_range()`](cron.py): Validates field values against allowed ranges
-   [`generate_step_value()`](cron.py): Generates stepped value sequences

## Error Handling

The tool provides detailed error messages for various invalid inputs:

-   Empty or malformed expressions
-   Values outside valid ranges
-   Invalid step values
-   Incorrect syntax patterns

## Testing

Test files are included in the workspace:

-   [test_cron.py](test_cron.py): Unit tests for the cron parser
-   [testcases.txt](testcases.txt): Sample test cases and expected outputs

Run tests with:

```bash
python3 -m pytest test_cron.py
```

For coverage report install coverage by:

````bash
pip install coverage```
````

And run the test with coverage:

```bash
coverage run -m pytest test_cron.py -v
coverage report -m --show-missing
```

## Examples

### Valid Expressions

```bash
# Every minute
python3 cron.py "* * * * *"

# At 2:30 AM every day
python3 cron.py "30 2 * * *"

# Every 15 minutes during business hours on weekdays
python3 cron.py "*/15 9-17 * * 1-5"

# On the 1st and 15th of every month
python3 cron.py "0 0 1,15 * *"

# Every hour on weekends
python3 cron.py "0 * * * 0,6"
```

### Invalid Expressions

```bash
# Invalid minute value
python3 cron.py "60 * * * *"

# Invalid range
python3 cron.py "5-3 * * * *"

# Invalid step
python3 cron.py "*/0 * * * *"

# Too few fields
python3 cron.py "* * *"
```
