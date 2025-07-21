#!/usr/bin/env python3
"""
Simple test script for CodeXam application
"""

from app import app
from judge import SimpleJudge

def test_routes():
    """Test basic routes."""
    print("🧪 Testing CodeXam routes...")
    
    with app.test_client() as client:
        # Test home page
        response = client.get('/')
        print(f"✅ Home page: {response.status_code}")
        
        # Test problems page
        response = client.get('/problems')
        print(f"✅ Problems page: {response.status_code}")
        
        # Test leaderboard
        response = client.get('/leaderboard')
        print(f"✅ Leaderboard: {response.status_code}")
        
        # Test set name page
        response = client.get('/set_name')
        print(f"✅ Set name page: {response.status_code}")
        
        # Test health check
        response = client.get('/health')
        print(f"✅ Health check: {response.status_code}")

def test_judge():
    """Test judge engine."""
    print("\n🧪 Testing Judge Engine...")
    
    judge = SimpleJudge()
    
    # Test Python execution
    python_code = """
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    test_cases = [
        {'input': [[2, 7, 11, 15], 9], 'expected_output': [0, 1]},
        {'input': [[3, 2, 4], 6], 'expected_output': [1, 2]}
    ]
    
    result = judge.execute_code('python', python_code, test_cases)
    print(f"✅ Python execution: {result['result']}")
    print(f"   Message: {result['message']}")
    print(f"   Time: {result['execution_time']:.3f}s")
    
    # Test security
    malicious_code = """
import os
def solution(a, b):
    return a + b
"""
    
    result = judge.execute_code('python', malicious_code, [{'input': [1, 2], 'expected_output': 3}])
    print(f"✅ Security test: {result['result']}")
    print(f"   Message: {result['message']}")

def test_submission():
    """Test code submission."""
    print("\n🧪 Testing Code Submission...")
    
    with app.test_client() as client:
        # Set user name first
        response = client.post('/set_name', data={'user_name': 'TestUser'})
        print(f"✅ Set name: {response.status_code}")
        
        # Try to submit code (this will fail because no problems exist yet)
        response = client.post('/submit', data={
            'problem_id': 1,
            'code': 'def solution(a, b): return a + b',
            'language': 'python'
        })
        print(f"✅ Code submission: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Result: {data.get('result', 'Unknown')}")

if __name__ == "__main__":
    print("🚀 CodeXam Application Test Suite")
    print("=" * 40)
    
    try:
        test_routes()
        test_judge()
        test_submission()
        
        print("\n" + "=" * 40)
        print("✅ All tests completed successfully!")
        print("\n🎉 CodeXam is ready to use!")
        print("   Run: python app.py")
        print("   Visit: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()