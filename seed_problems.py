"""
CodeXam Sample Problems
Populates the database with sample coding problems for testing and demonstration
"""

from models import Problem
from init_db import initialize_database

def create_sample_problems():
    """Create sample problems for testing the platform."""
    
    problems = [
        {
            'title': 'Two Sum',
            'difficulty': 'Easy',
            'description': '''Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].''',
            'function_signatures': {
                'python': 'def solution(nums, target):\n    pass',
                'javascript': 'function solution(nums, target) {\n    // Your code here\n}',
                'java': 'public int[] solution(int[] nums, int target) {\n    // Your code here\n}',
                'cpp': 'vector<int> solution(vector<int>& nums, int target) {\n    // Your code here\n}'
            },
            'test_cases': [
                {'input': [[2, 7, 11, 15], 9], 'expected_output': [0, 1]},
                {'input': [[3, 2, 4], 6], 'expected_output': [1, 2]},
                {'input': [[3, 3], 6], 'expected_output': [0, 1]},
                {'input': [[1, 2, 3, 4, 5], 9], 'expected_output': [3, 4]},
                {'input': [[-1, -2, -3, -4, -5], -8], 'expected_output': [2, 4]}
            ],
            'sample_input': 'nums = [2,7,11,15], target = 9',
            'sample_output': '[0,1]'
        },
        {
            'title': 'Palindrome Number',
            'difficulty': 'Easy',
            'description': '''Given an integer x, return true if x is palindrome integer.

An integer is a palindrome when it reads the same backward as forward.

Example:
Input: x = 121
Output: true
Explanation: 121 reads as 121 from left to right and from right to left.

Example:
Input: x = -121
Output: false
Explanation: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.''',
            'function_signatures': {
                'python': 'def solution(x):\n    pass',
                'javascript': 'function solution(x) {\n    // Your code here\n}',
                'java': 'public boolean solution(int x) {\n    // Your code here\n}',
                'cpp': 'bool solution(int x) {\n    // Your code here\n}'
            },
            'test_cases': [
                {'input': [121], 'expected_output': True},
                {'input': [-121], 'expected_output': False},
                {'input': [10], 'expected_output': False},
                {'input': [0], 'expected_output': True},
                {'input': [12321], 'expected_output': True}
            ],
            'sample_input': 'x = 121',
            'sample_output': 'true'
        },
        {
            'title': 'Reverse Integer',
            'difficulty': 'Medium',
            'description': '''Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return 0.

Assume the environment does not allow you to store 64-bit integers (signed or unsigned).

Example:
Input: x = 123
Output: 321

Example:
Input: x = -123
Output: -321

Example:
Input: x = 120
Output: 21''',
            'function_signatures': {
                'python': 'def solution(x):\n    pass',
                'javascript': 'function solution(x) {\n    // Your code here\n}',
                'java': 'public int solution(int x) {\n    // Your code here\n}',
                'cpp': 'int solution(int x) {\n    // Your code here\n}'
            },
            'test_cases': [
                {'input': [123], 'expected_output': 321},
                {'input': [-123], 'expected_output': -321},
                {'input': [120], 'expected_output': 21},
                {'input': [0], 'expected_output': 0},
                {'input': [1534236469], 'expected_output': 0}  # Overflow case
            ],
            'sample_input': 'x = 123',
            'sample_output': '321'
        },
        {
            'title': 'Valid Parentheses',
            'difficulty': 'Easy',
            'description': '''Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.

Example:
Input: s = "()"
Output: true

Example:
Input: s = "()[]{}"
Output: true

Example:
Input: s = "(]"
Output: false''',
            'function_signatures': {
                'python': 'def solution(s):\n    pass',
                'javascript': 'function solution(s) {\n    // Your code here\n}',
                'java': 'public boolean solution(String s) {\n    // Your code here\n}',
                'cpp': 'bool solution(string s) {\n    // Your code here\n}'
            },
            'test_cases': [
                {'input': ['()'], 'expected_output': True},
                {'input': ['()[]{}'], 'expected_output': True},
                {'input': ['(]'], 'expected_output': False},
                {'input': ['([)]'], 'expected_output': False},
                {'input': ['{[]}'], 'expected_output': True}
            ],
            'sample_input': 's = "()"',
            'sample_output': 'true'
        },
        {
            'title': 'Merge Two Sorted Lists',
            'difficulty': 'Easy',
            'description': '''You are given the heads of two sorted linked lists list1 and list2.

Merge the two lists in a one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.

Note: For this problem, we'll represent linked lists as arrays for simplicity.

Example:
Input: list1 = [1,2,4], list2 = [1,3,4]
Output: [1,1,2,3,4,4]''',
            'function_signatures': {
                'python': 'def solution(list1, list2):\n    pass',
       
         'javascript': 'function solution(list1, list2) {\n    // Your code here\n}',
                'java': 'public int[] solution(int[] list1, int[] list2) {\n    // Your code here\n}',
                'cpp': 'vector<int> solution(vector<int>& list1, vector<int>& list2) {\n    // Your code here\n}'
            },
            'test_cases': [
                {'input': [[1,2,4], [1,3,4]], 'expected_output': [1,1,2,3,4,4]},
                {'input': [[], []], 'expected_output': []},
                {'input': [[], [0]], 'expected_output': [0]}
            ],
            'sample_input': 'list1 = [1,2,4], list2 = [1,3,4]',
            'sample_output': '[1,1,2,3,4,4]'
        }
    ]

    # Add problems to database
    for problem_data in problems:
        try:
            problem = Problem.create(
                title=problem_data['title'],
                difficulty=problem_data['difficulty'],
                description=problem_data['description'],
                function_signatures=problem_data['function_signatures'],
                test_cases=problem_data['test_cases'],
                sample_input=problem_data['sample_input'],
                sample_output=problem_data['sample_output']
            )
            print(f"✅ Added problem: {problem.title}")
        except Exception as e:
            print(f"❌ Failed to add problem {problem_data['title']}: {e}")

    print(f"\n🎉 Successfully seeded {len(problems)} problems!")

if __name__ == "__main__":
    create_sample_problems()