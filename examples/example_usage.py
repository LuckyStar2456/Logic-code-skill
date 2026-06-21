"""
Example usage of the Code Complexity Analyzer skill.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skill'))

from __init__ import analyze, generate_report, check_code_style

# Example Python code to analyze
sample_python_code = """
def complex_function(param1, param2, param3, param4, param5):
    \"\"\"A complex function with high cyclomatic complexity.\"\"\"
    result = 0
    
    if param1 > 0:
        if param2 < 10:
            for i in range(param3):
                if i % 2 == 0:
                    result += param4 * i
                else:
                    result -= param5 * i
        elif param2 >= 10 and param2 < 20:
            while param3 > 0:
     
                result += param1
                param3 -= 1
        else:
            result = param1 + param2 + param3
    elif param1 == 0:
        for item in [1, 2, 3, 4, 5]:
            if item % 2 == 0:
                result += item
    else:
        result = -1
    
    return result

def simple_function(name):
    \"\"\"A simple function.\"\"\"
    return f"Hello, {name}!"

# TODO: This is a comment to track
class ExampleClass:
    def __init__(self, value):
        self.value = value
    
    def process(self, data):
        if data:
            return self._helper(data)
        return None
    
    def _helper(self, items):
        result = []
        for item in items:
            if isinstance(item, int):
                result.append(item * 2)
            elif isinstance(item, str):
                result.append(item.upper())
        return result
"""

def main():
    print("=" * 60)
    print("CODE COMPLEXITY ANALYZER - EXAMPLE USAGE")
    print("=" * 60)
    print()
    
    print("1. Basic Analysis:")
    print("-" * 40)
    result = analyze(sample_python_code)
    print(f"Success: {result['success']}")
    print(f"Total Lines: {result['summary']['total_lines']}")
    print(f"Average Complexity: {result['complexity']['average']}")
    print(f"Number of Functions: {len(result['functions'])}")
    print()
    
    print("2. Detailed Report:")
    print("-" * 40)
    report = generate_report(sample_python_code)
    print(report)
    print()
    
    print("3. Code Style Check:")
    print("-" * 40)
    style_result = check_code_style(sample_python_code)
    if style_result['warnings']:
        print("Warnings:")
        for warning in style_result['warnings']:
            print(f"  - {warning}")
    else:
        print("No style warnings found.")
    
    if style_result['suggestions']:
        print("\nSuggestions:")
        for suggestion in style_result['suggestions']:
            print(f"  - {suggestion}")
    
    print()
    print("=" * 60)
    print("Example complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()