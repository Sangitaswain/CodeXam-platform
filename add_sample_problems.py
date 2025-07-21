#!/usr/bin/env python3
"""
Add sample problems to CodeXam database
"""

from models import Problem
from database import get_db

def add_sample_problems():
    """Add sample coding problems to the database."""
    print("🔧 Adding sample problems to CodeXam...")
    
    # Problem 1: Two Sum (Easy)
    problem1 = Problem.create(
        title="Two Sum",
        description="""Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:
Input: nums = [3,3], target = 6
Output: [0,1]""",
        difficulty="Easy",
        function_signatures={
            "python": "def two_sum(nums, target):\n    pass",
            "javascript": "function twoSum(nums, target) {\n    // Your code here\n}",
            "java": "public int[] twoSum(int[] nums, int target) {\n    // Your code here\n}",
            "cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    // Your code here\n}"
        },
        test_cases=[
            {'input': [[2, 7, 11, 15], 9], 'expected_output': [0, 1]},
            {'input': [[3, 2, 4], 6], 'expected_output': [1, 2]},
            {'input': [[3, 3], 6], 'expected_output': [0, 1]},
            {'input': [[1, 2, 3, 4, 5], 8], 'expected_output': [2, 4]},
            {'input': [[1, 5, 3, 7, 2], 10], 'expected_output': [1, 3]}
        ],
        sample_input="nums = [2,7,11,15], target = 9",
        sample_output="[0,1]"
    )
    print(f"✅ Added problem: {problem1.title}")
    
    # Problem 2: Palindrome Number (Easy)
    problem2 = Problem.create(
        title="Palindrome Number",
        description="""Given an integer x, return true if x is palindrome integer.

An integer is a palindrome when it reads the same backward as forward.

For example, 121 is a palindrome while 123 is not.

Example 1:
Input: x = 121
Output: true
Explanation: 121 reads as 121 from left to right and from right to left.

Example 2:
Input: x = -121
Output: false
Explanation: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.

Example 3:
Input: x = 10
Output: false
Explanation: Reads 01 from right to left. Therefore it is not a palindrome.""",
        difficulty="Easy",
        function_signatures={
            "python": "def is_palindrome(x):\n    pass",
            "javascript": "function isPalindrome(x) {\n    // Your code here\n}",
            "java": "public boolean isPalindrome(int x) {\n    // Your code here\n}",
            "cpp": "bool isPalindrome(int x) {\n    // Your code here\n}"
        },
        test_cases=[
            {'input': [121], 'expected_output': True},
            {'input': [-121], 'expected_output': False},
            {'input': [10], 'expected_output': False},
            {'input': [0], 'expected_output': True},
            {'input': [12321], 'expected_output': True}
        ],
        sample_input="x = 121",
        sample_output="true"
    )
    print(f"✅ Added problem: {problem2.title}")
    
    # Problem 3: Reverse Integer (Medium)
    problem3 = Problem.create(
        title="Reverse Integer",
        description="""Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return 0.

Assume the environment does not allow you to store 64-bit integers (signed or unsigned).

Example 1:
Input: x = 123
Output: 321

Example 2:
Input: x = -123
Output: -321

Example 3:
Input: x = 120
Output: 21""",
        difficulty="Medium",
        function_signatures={
            "python": "def reverse(x):\n    pass",
            "javascript": "function reverse(x) {\n    // Your code here\n}",
            "java": "public int reverse(int x) {\n    // Your code here\n}",
            "cpp": "int reverse(int x) {\n    // Your code here\n}"
        },
        test_cases=[
            {'input': [123], 'expected_output': 321},
            {'input': [-123], 'expected_output': -321},
            {'input': [120], 'expected_output': 21},
            {'input': [0], 'expected_output': 0},
            {'input': [1534236469], 'expected_output': 0}  # Overflow case
        ],
        sample_input="x = 123",
        sample_output="321"
    )
    print(f"✅ Added problem: {problem3.title}")
    
    print(f"\n🎉 Successfully added {3} sample problems!")
    print("You can now test the full CodeXam workflow:")
    print("1. Run: python app.py")
    print("2. Visit: http://localhost:5000")
    print("3. Click 'View Problems' to see the problems")
    print("4. Try solving them!")

if __name__ == "__main__":
    try:
        add_sample_problems()
    except Exception as e:
        print(f"❌ Error adding problems: {e}")
        import traceback
        traceback.print_exc()