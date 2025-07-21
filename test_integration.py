#!/usr/bin/env python3
"""
Integration test for CodeXam models and judge
"""

from models import Problem, Submission
from judge import SimpleJudge

def test_integration():
    """Test integration between models and judge."""
    print("🧪 Running integration test...")
    
    try:
        # Create a test problem
        problem = Problem.create(
            title='Two Sum Test',
            description='Find two numbers that add up to target',
            difficulty='Easy',
            function_signatures={'python': 'def two_sum(nums, target):'},
            test_cases=[{'input': [[2, 7, 11, 15], 9], 'expected_output': [0, 1]}]
        )
        
        print(f'✅ Created problem: {problem}')
        
        # Test code execution
        judge = SimpleJudge()
        code = '''
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
'''
        
        result = judge.execute_code('python', code, problem.test_cases)
        print(f'✅ Judge result: {result["result"]}')
        
        # Create submission
        submission = Submission.create(
            problem_id=problem.id,
            user_name='test_user',
            language='python',
            code=code,
            result=result['result'],
            execution_time=result['execution_time']
        )
        
        print(f'✅ Created submission: {submission}')
        
        # Test leaderboard
        leaderboard = Submission.get_leaderboard(5)
        print(f'✅ Leaderboard: {leaderboard}')
        
        print('🎉 Integration test successful!')
        return True
        
    except Exception as e:
        print(f'❌ Integration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_integration()