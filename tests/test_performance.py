"""Performance tests for CodeXam platform."""

# Standard library imports
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Third-party imports
import pytest

# Performance test constants
PERFORMANCE_THRESHOLDS = {
    'problem_list_load': 0.1,  # 100ms
    'filtered_query': 0.05,    # 50ms
    'submission_history': 0.05, # 50ms
    'user_statistics': 0.1,    # 100ms
    'leaderboard_calc': 0.2,   # 200ms
    'page_load': 0.5,          # 500ms
    'problems_page': 0.3,      # 300ms
}

TEST_DATA_SIZES = {
    'many_problems': 100,
    'many_submissions': 200,
    'concurrent_requests': 20,
    'concurrent_submissions': 10,
}


def measure_execution_time(func, *args, **kwargs) -> tuple[Any, float]:
    """
    Measure execution time of a function.
    
    Args:
        func: Function to measure
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
    
    Returns:
        Tuple of (function_result, execution_time_in_seconds)
    
    Raises:
        Exception: Re-raises any exception from the measured function
    """
    start_time = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    except Exception as e:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        raise RuntimeError(
            f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}"
        ) from e


def assert_performance_threshold(execution_time: float, threshold_key: str, operation_name: str) -> None:
    """
    Assert that execution time meets performance threshold.
    
    Args:
        execution_time: Actual execution time in seconds
        threshold_key: Key in PERFORMANCE_THRESHOLDS dict
        operation_name: Human-readable operation name for error messages
    """
    threshold = PERFORMANCE_THRESHOLDS[threshold_key]
    assert execution_time < threshold, (
        f"{operation_name} took {execution_time:.3f}s, expected < {threshold}s"
    )


class ResourceMonitor:
    """Helper class for monitoring system resources during tests."""
    
    def __init__(self):
        """Initialize resource monitor."""
        try:
            import psutil
            import os
            self.process = psutil.Process(os.getpid())
            self.psutil_available = True
        except ImportError:
            self.psutil_available = False
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if not self.psutil_available:
            return 0.0
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        if not self.psutil_available:
            return 0.0
        try:
            return self.process.cpu_percent()
        except Exception:
            return 0.0
    
    def assert_memory_increase(self, initial_memory: float, max_increase_mb: float, operation_name: str) -> None:
        """Assert that memory increase is within acceptable limits."""
        if not self.psutil_available:
            return
        
        current_memory = self.get_memory_usage()
        memory_increase = current_memory - initial_memory
        
        assert memory_increase < max_increase_mb, (
            f"{operation_name} increased memory by {memory_increase:.1f}MB, "
            f"expected < {max_increase_mb}MB"
        )


class TestDatabasePerformance:
    """
    Test database performance and optimization.
    
    These tests ensure that database operations meet performance requirements
    even under load. They help identify performance regressions and validate
    that database queries are properly optimized.
    """
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self, test_db):
        """Set up and clean up test data for each test."""
        # Setup is handled by individual tests
        yield
        # Cleanup after each test
        try:
            # Clear test data to prevent interference between tests
            test_db.execute("DELETE FROM submissions WHERE user_name LIKE 'testuser%' OR user_name LIKE 'user%'")
            test_db.execute("DELETE FROM problems WHERE title LIKE '%Test%' OR title LIKE '%Performance%'")
            test_db.commit()
        except Exception as e:
            # Log cleanup errors but don't fail the test
            print(f"Warning: Cleanup failed: {e}")
            test_db.rollback()
    
    @pytest.mark.performance
    def test_problem_list_performance(self, test_db, test_utils):
        """Test that problem list loads quickly even with many problems."""
        # Create many test problems
        num_problems = TEST_DATA_SIZES['many_problems']
        difficulties = ["Easy", "Medium", "Hard"]
        
        for i in range(num_problems):
            test_utils.create_test_problem(
                test_db,
                title=f"Performance Test Problem {i}",
                difficulty=difficulties[i % len(difficulties)]
            )
        
        from models import Problem
        
        # Measure performance
        problems, execution_time = measure_execution_time(Problem.get_all)
        
        # Assert performance and correctness
        assert_performance_threshold(execution_time, 'problem_list_load', "Problem list loading")
        assert len(problems) >= num_problems
    
    @pytest.mark.performance
    def test_problem_list_with_filter_performance(self, test_db, test_utils):
        """Test performance of filtered problem queries."""
        # Create test problems with different difficulties
        difficulties = ["Easy", "Medium", "Hard"]
        problems_per_difficulty = 50
        
        for i in range(problems_per_difficulty):
            for difficulty in difficulties:
                test_utils.create_test_problem(
                    test_db,
                    title=f"Test Problem {i} - {difficulty}",
                    difficulty=difficulty
                )
        
        from models import Problem
        
        # Test filtering performance
        easy_problems, execution_time = measure_execution_time(
            Problem.get_all, difficulty="Easy"
        )
        
        assert_performance_threshold(execution_time, 'filtered_query', "Filtered problem query")
        assert len(easy_problems) >= problems_per_difficulty
    
    @pytest.mark.performance
    def test_submission_history_performance(self, test_db, test_utils):
        """Test performance of submission history queries."""
        # Create many test submissions
        for i in range(200):
            test_utils.create_test_submission(
                test_db,
                user_name=f"testuser{i % 10}",  # 10 different users
                problem_id=(i % 3) + 1,  # Rotate through first 3 problems
                result="PASS" if i % 2 == 0 else "FAIL"
            )
        
        from models import Submission
        
        # Test recent submissions query
        start_time = time.time()
        recent_submissions = Submission.get_recent(limit=50)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.05, f"Recent submissions query took {execution_time:.3f}s, expected < 0.05s"
        assert len(recent_submissions) == 50
    
    @pytest.mark.performance
    def test_user_statistics_performance(self, test_db, test_utils):
        """Test performance of user statistics calculation."""
        # Create submissions for a user
        for i in range(100):
            test_utils.create_test_submission(
                test_db,
                user_name="performance_test_user",
                problem_id=(i % 3) + 1,
                result="PASS" if i % 3 != 0 else "FAIL"
            )
        
        from models import Submission
        
        start_time = time.time()
        stats = Submission.get_user_statistics("performance_test_user")
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.1, f"User statistics took {execution_time:.3f}s, expected < 0.1s"
        assert stats['total_submissions'] == 100
    
    @pytest.mark.performance
    def test_leaderboard_calculation_performance(self, test_db, test_utils):
        """Test leaderboard calculation performance."""
        # Create submissions for many users
        for user_id in range(50):
            for problem_id in range(1, 4):  # 3 problems
                for attempt in range(3):  # 3 attempts per problem
                    test_utils.create_test_submission(
                        test_db,
                        user_name=f"user{user_id}",
                        problem_id=problem_id,
                        result="PASS" if attempt == 2 else "FAIL"  # Last attempt passes
                    )
        
        from models import Submission
        
        start_time = time.time()
        leaderboard = Submission.get_leaderboard(limit=20)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.2, f"Leaderboard calculation took {execution_time:.3f}s, expected < 0.2s"
        assert len(leaderboard) == 20


class TestRoutePerformance:
    """Test route performance under load."""
    
    @pytest.mark.performance
    def test_index_page_performance(self, client, test_db):
        """Test index page load performance."""
        # Warm up
        client.get('/')
        
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.5, f"Index page took {execution_time:.3f}s, expected < 0.5s"
        assert response.status_code == 200
    
    @pytest.mark.performance
    def test_problems_page_performance(self, client, test_db):
        """Test problems page load performance."""
        start_time = time.time()
        response = client.get('/problems')
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.3, f"Problems page took {execution_time:.3f}s, expected < 0.3s"
        assert response.status_code == 200
    
    @pytest.mark.performance
    def test_problem_detail_performance(self, client, test_db):
        """Test problem detail page load performance."""
        start_time = time.time()
        response = client.get('/problem/1')
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.2, f"Problem detail took {execution_time:.3f}s, expected < 0.2s"
        assert response.status_code == 200
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_requests_performance(self, app, test_db):
        """Test performance under concurrent requests."""
        def make_request():
            client = app.test_client()
            start_time = time.time()
            response = client.get('/problems')
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]
        
        assert all(status == 200 for status in status_codes)
        
        # Average response time should be reasonable
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s, expected < 1.0s"
        
        # No request should take too long
        max_response_time = max(response_times)
        assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s, expected < 2.0s"


class TestJudgePerformance:
    """Test judge system performance."""
    
    @pytest.mark.performance
    def test_code_execution_performance(self, mock_judge):
        """Test code execution performance."""
        from judge import SimpleJudge
        
        # Mock fast execution
        mock_judge.execute_code.return_value = {
            'result': 'PASS',
            'message': '1/1 test cases passed',
            'test_results': [{'passed': True}],
            'execution_time': 0.001,
            'memory_used': 1024
        }
        
        test_code = '''
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
'''
        
        with patch('judge.SimpleJudge', return_value=mock_judge):
            judge = SimpleJudge()
            
            start_time = time.time()
            result = judge.execute_code('python', test_code, [])
            end_time = time.time()
            
            execution_time = end_time - start_time
            assert execution_time < 0.1, f"Judge execution took {execution_time:.3f}s, expected < 0.1s"
            assert result['result'] == 'PASS'
    
    @pytest.mark.performance
    def test_multiple_submissions_performance(self, authenticated_client, test_db, mock_judge):
        """Test performance of multiple code submissions."""
        with patch('routes.SimpleJudge', return_value=mock_judge):
            submission_times = []
            
            for i in range(10):
                start_time = time.time()
                response = authenticated_client.post('/submit', data={
                    'problem_id': '1',
                    'language': 'python',
                    'code': f'def solution(): return {i}',
                    'csrf_token': 'test-token'
                })
                end_time = time.time()
                
                submission_times.append(end_time - start_time)
                assert response.status_code == 200
            
            # Average submission time should be reasonable
            avg_time = sum(submission_times) / len(submission_times)
            assert avg_time < 0.5, f"Average submission time {avg_time:.3f}s, expected < 0.5s"
            
            # No submission should take too long
            max_time = max(submission_times)
            assert max_time < 1.0, f"Max submission time {max_time:.3f}s, expected < 1.0s"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_submissions_performance(self, app, test_db, mock_judge):
        """Test performance of concurrent code submissions."""
        def submit_code(user_id):
            client = app.test_client()
            with client.session_transaction() as sess:
                sess['user_name'] = f'testuser{user_id}'
            
            with patch('routes.SimpleJudge', return_value=mock_judge):
                start_time = time.time()
                response = client.post('/submit', data={
                    'problem_id': '1',
                    'language': 'python',
                    'code': f'def solution(): return {user_id}',
                    'csrf_token': 'test-token'
                })
                end_time = time.time()
                
                return response.status_code, end_time - start_time
        
        # Make 10 concurrent submissions
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(submit_code, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # All submissions should succeed
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]
        
        assert all(status == 200 for status in status_codes)
        
        # Performance should be reasonable
        avg_time = sum(response_times) / len(response_times)
        assert avg_time < 1.0, f"Average concurrent submission time {avg_time:.3f}s, expected < 1.0s"


class TestMemoryPerformance:
    """Test memory usage and optimization."""
    
    @pytest.mark.performance
    def test_memory_usage_large_dataset(self, test_db, test_utils):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        for i in range(500):
            test_utils.create_test_problem(
                test_db,
                title=f"Memory Test Problem {i}",
                description="A" * 1000  # 1KB description
            )
        
        from models import Problem
        problems = Problem.get_all()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for this test)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB, expected < 50MB"
        assert len(problems) >= 500
    
    @pytest.mark.performance
    def test_memory_cleanup_after_requests(self, client, test_db):
        """Test that memory is properly cleaned up after requests."""
        import psutil
        import os
        import gc
        
        process = psutil.Process(os.getpid())
        
        # Make many requests
        for i in range(100):
            response = client.get('/problems')
            assert response.status_code == 200
        
        # Force garbage collection
        gc.collect()
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make more requests
        for i in range(100):
            response = client.get('/problems')
            assert response.status_code == 200
        
        # Force garbage collection again
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory should not increase significantly
        assert memory_increase < 10, f"Memory increased by {memory_increase:.1f}MB after requests"


class TestCachePerformance:
    """Test caching performance and effectiveness."""
    
    @pytest.mark.performance
    def test_cache_effectiveness(self, test_db):
        """Test that caching improves performance."""
        from cache import SimpleCache
        
        cache = SimpleCache()
        
        # Test cache miss (first access)
        start_time = time.time()
        cache.set('test_key', 'test_value', ttl=60)
        cache_miss_time = time.time() - start_time
        
        # Test cache hit (subsequent access)
        start_time = time.time()
        value = cache.get('test_key')
        cache_hit_time = time.time() - start_time
        
        assert value == 'test_value'
        assert cache_hit_time < cache_miss_time  # Cache hit should be faster
        assert cache_hit_time < 0.001  # Cache hit should be very fast
    
    @pytest.mark.performance
    def test_cache_performance_under_load(self):
        """Test cache performance under concurrent load."""
        from cache import SimpleCache
        
        cache = SimpleCache()
        
        def cache_operations():
            results = []
            for i in range(100):
                start_time = time.time()
                cache.set(f'key_{i}', f'value_{i}', ttl=60)
                value = cache.get(f'key_{i}')
                end_time = time.time()
                
                results.append(end_time - start_time)
                assert value == f'value_{i}'
            
            return results
        
        # Run concurrent cache operations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(cache_operations) for _ in range(5)]
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # All operations should be fast
        avg_time = sum(all_results) / len(all_results)
        assert avg_time < 0.01, f"Average cache operation time {avg_time:.4f}s, expected < 0.01s"
        
        max_time = max(all_results)
        assert max_time < 0.1, f"Max cache operation time {max_time:.4f}s, expected < 0.1s"


class TestScalabilityTests:
    """Test system scalability and limits."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_code_submission_handling(self, authenticated_client, test_db, mock_judge):
        """Test handling of large code submissions."""
        # Create progressively larger code submissions
        code_sizes = [1000, 5000, 10000, 20000]  # Characters
        
        for size in code_sizes:
            large_code = f'def solution():\n    # {"x" * (size - 50)}\n    return "test"'
            
            with patch('routes.SimpleJudge', return_value=mock_judge):
                start_time = time.time()
                response = authenticated_client.post('/submit', data={
                    'problem_id': '1',
                    'language': 'python',
                    'code': large_code,
                    'csrf_token': 'test-token'
                })
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                if size <= 10000:  # Should handle up to 10KB
                    assert response.status_code == 200
                    assert execution_time < 1.0, f"Large code ({size} chars) took {execution_time:.3f}s"
                else:  # Very large submissions might be rejected
                    assert response.status_code in [200, 400, 413]
    
    @pytest.mark.performance
    def test_database_connection_pooling_performance(self, test_db):
        """Test database connection pooling performance."""
        from database import get_db
        
        connection_times = []
        
        # Test multiple database connections
        for i in range(20):
            start_time = time.time()
            db = get_db()
            end_time = time.time()
            
            connection_times.append(end_time - start_time)
            assert db is not None
        
        # Connection times should be consistent and fast
        avg_time = sum(connection_times) / len(connection_times)
        assert avg_time < 0.01, f"Average connection time {avg_time:.4f}s, expected < 0.01s"
        
        # No connection should take too long
        max_time = max(connection_times)
        assert max_time < 0.1, f"Max connection time {max_time:.4f}s, expected < 0.1s"
    
    @pytest.mark.performance
    def test_system_resource_monitoring(self, client, test_db):
        """Test system resource usage during normal operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Record initial resource usage
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform various operations
        operations = [
            lambda: client.get('/'),
            lambda: client.get('/problems'),
            lambda: client.get('/problem/1'),
            lambda: client.get('/problems?difficulty=Easy'),
        ]
        
        for _ in range(50):  # Repeat operations
            for operation in operations:
                response = operation()
                assert response.status_code == 200
        
        # Record final resource usage
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = final_memory - initial_memory
        
        # Resource usage should be reasonable
        assert memory_increase < 20, f"Memory increased by {memory_increase:.1f}MB during operations"
        
        # CPU usage should not be excessive (this is approximate)
        assert final_cpu < 80, f"CPU usage {final_cpu}% is too high"