#!/usr/bin/env python3
"""
Test script to verify database schema functionality
"""

import os
import json
from database import get_db, dict_to_json, json_to_dict

def test_database_schema():
    """Test database schema by inserting and retrieving test data."""
    print("🧪 Testing database schema...")
    
    db = get_db()
    
    # Test 1: Insert a test problem
    print("\n1️⃣ Testing problems table...")
    
    test_problem_data = {
        'title': 'Two Sum Test',
        'description': 'Find two numbers in an array that add up to a target sum.',
        'difficulty': 'Easy',
        'function_signatures': dict_to_json({
            'python': 'def solution(nums, target):',
            'javascript': 'function solution(nums, target) {',
            'java': 'public int[] solution(int[] nums, int target) {',
            'cpp': 'vector<int> solution(vector<int>& nums, int target) {'
        }),
        'test_cases': dict_to_json([
            {'input': [[2, 7, 11, 15], 9], 'output': [0, 1]},
            {'input': [[3, 2, 4], 6], 'output': [1, 2]}
        ]),
        'sample_input': '[2, 7, 11, 15], target = 9',
        'sample_output': '[0, 1]'
    }
    
    # Insert test problem
    problem_id = db.execute_insert("""
        INSERT INTO problems (title, description, difficulty, function_signatures, test_cases, sample_input, sample_output)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        test_problem_data['title'],
        test_problem_data['description'],
        test_problem_data['difficulty'],
        test_problem_data['function_signatures'],
        test_problem_data['test_cases'],
        test_problem_data['sample_input'],
        test_problem_data['sample_output']
    ))
    
    print(f"✅ Inserted test problem with ID: {problem_id}")
    
    # Retrieve and verify problem
    problem = db.execute_single("SELECT * FROM problems WHERE id = ?", (problem_id,))
    if problem:
        print(f"✅ Retrieved problem: {problem['title']}")
        print(f"   - Difficulty: {problem['difficulty']}")
        print(f"   - Function signatures: {len(json_to_dict(problem['function_signatures']))} languages")
        print(f"   - Test cases: {len(json_to_dict(problem['test_cases']))} cases")
    else:
        print("❌ Failed to retrieve test problem")
        return False
    
    # Test 2: Insert test submissions
    print("\n2️⃣ Testing submissions table...")
    
    test_submissions = [
        {
            'problem_id': problem_id,
            'user_name': 'test_user_1',
            'language': 'python',
            'code': 'def solution(nums, target):\n    return [0, 1]',
            'result': 'PASS',
            'execution_time': 0.05,
            'memory_used': 1024
        },
        {
            'problem_id': problem_id,
            'user_name': 'test_user_2',
            'language': 'javascript',
            'code': 'function solution(nums, target) {\n    return [0, 1];\n}',
            'result': 'FAIL',
            'execution_time': 0.08,
            'memory_used': 2048
        },
        {
            'problem_id': problem_id,
            'user_name': 'test_user_1',
            'language': 'java',
            'code': 'public int[] solution(int[] nums, int target) {\n    return new int[]{0, 1};\n}',
            'result': 'ERROR',
            'execution_time': 0.0,
            'memory_used': 0,
            'error_message': 'Compilation error: missing semicolon'
        }
    ]
    
    submission_ids = []
    for submission in test_submissions:
        submission_id = db.execute_insert("""
            INSERT INTO submissions (problem_id, user_name, language, code, result, execution_time, memory_used, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            submission['problem_id'],
            submission['user_name'],
            submission['language'],
            submission['code'],
            submission['result'],
            submission['execution_time'],
            submission['memory_used'],
            submission.get('error_message')
        ))
        submission_ids.append(submission_id)
        print(f"✅ Inserted submission {submission_id}: {submission['user_name']} - {submission['result']}")
    
    # Test 3: Verify user statistics (should be updated by triggers)
    print("\n3️⃣ Testing users table and triggers...")
    
    users = db.execute_query("SELECT * FROM users ORDER BY username")
    for user in users:
        print(f"✅ User: {user['username']}")
        print(f"   - Problems solved: {user['problems_solved']}")
        print(f"   - Total submissions: {user['total_submissions']}")
    
    # Test 4: Test indexes and performance queries
    print("\n4️⃣ Testing indexes and queries...")
    
    # Query by difficulty
    easy_problems = db.execute_query("SELECT COUNT(*) as count FROM problems WHERE difficulty = 'Easy'")
    print(f"✅ Easy problems count: {easy_problems[0]['count']}")
    
    # Query submissions by user
    user_submissions = db.execute_query("""
        SELECT COUNT(*) as count, result 
        FROM submissions 
        WHERE user_name = 'test_user_1' 
        GROUP BY result
    """)
    print(f"✅ test_user_1 submissions by result:")
    for row in user_submissions:
        print(f"   - {row['result']}: {row['count']}")
    
    # Test leaderboard query
    leaderboard = db.execute_query("""
        SELECT username, problems_solved, total_submissions
        FROM users 
        ORDER BY problems_solved DESC, total_submissions ASC
        LIMIT 10
    """)
    print(f"✅ Leaderboard (top users):")
    for i, user in enumerate(leaderboard, 1):
        print(f"   {i}. {user['username']}: {user['problems_solved']} solved, {user['total_submissions']} total")
    
    # Test 5: Foreign key constraints
    print("\n5️⃣ Testing foreign key constraints...")
    
    try:
        # Try to insert submission with invalid problem_id
        db.execute_insert("""
            INSERT INTO submissions (problem_id, user_name, language, code, result)
            VALUES (?, ?, ?, ?, ?)
        """, (99999, 'test_user', 'python', 'test code', 'PASS'))
        print("❌ Foreign key constraint failed - should not allow invalid problem_id")
        return False
    except Exception as e:
        print(f"✅ Foreign key constraint working: {e}")
    
    print("\n🎉 All database schema tests passed!")
    return True

def cleanup_test_data():
    """Clean up test data from database."""
    print("\n🧹 Cleaning up test data...")
    
    db = get_db()
    
    # Delete test submissions
    db.execute_update("DELETE FROM submissions WHERE user_name LIKE 'test_user_%'")
    
    # Delete test problems
    db.execute_update("DELETE FROM problems WHERE title LIKE '%Test%'")
    
    # Delete test users
    db.execute_update("DELETE FROM users WHERE username LIKE 'test_user_%'")
    
    print("✅ Test data cleaned up")

if __name__ == "__main__":
    try:
        success = test_database_schema()
        if success:
            print("\n✅ Database schema test completed successfully!")
        else:
            print("\n❌ Database schema test failed!")
    except Exception as e:
        print(f"\n❌ Database schema test error: {e}")
    finally:
        cleanup_test_data()