#!/usr/bin/env python3
"""
Performance Testing Suite for System Info Modal
Tests performance, load times, and resource usage
"""

import pytest
import time
import threading
import concurrent.futures
import psutil
import gc
import json
from unittest.mock import patch
from app import create_app
from init_db import initialize_database


class TestSystemInfoModalPerformance:
    """Test suite for system info modal performance metrics."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(':memory:')
                yield client
    
    def test_api_response_times(self, client):
        """Test API endpoint response times."""
        endpoints = [
            '/api/system-info',
            '/api/platform-stats', 
            '/api/health-check'
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            # Warm up request
            client.get(endpoint)
            
            # Measure response time
            start_time = time.perf_counter()
            response = client.get(endpoint)
            end_time = time.perf_counter()
            
            response_time = end_time - start_time
            response_times[endpoint] = response_time
            
            assert response.status_code == 200
            assert response_time < 0.5, f"{endpoint} should respond within 500ms, got {response_time:.3f}s"
        
        print(f"\n📊 API Response Times:")
        for endpoint, time_taken in response_times.items():
            print(f"  {endpoint}: {time_taken:.3f}s")
    
    def test_concurrent_api_requests(self, client):
        """Test API performance under concurrent load."""
        def make_request(endpoint):
            start_time = time.perf_counter()
            response = client.get(endpoint)
            end_time = time.perf_counter()
            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'content_length': len(response.data)
            }
        
        # Test with multiple concurrent requests
        endpoints = ['/api/system-info', '/api/platform-stats', '/api/health-check']
        num_requests = 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit requests
            futures = []
            for _ in range(num_requests):
                for endpoint in endpoints:
                    future = executor.submit(make_request, endpoint)
                    futures.append(future)
            
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
        
        # Analyze results
        successful_requests = [r for r in results if r['status_code'] == 200]
        failed_requests = [r for r in results if r['status_code'] != 200]
        
        assert len(failed_requests) == 0, f"All requests should succeed, got {len(failed_requests)} failures"
        
        # Check response times
        avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
        max_response_time = max(r['response_time'] for r in successful_requests)
        
        assert avg_response_time < 1.0, f"Average response time should be < 1s, got {avg_response_time:.3f}s"
        assert max_response_time < 2.0, f"Max response time should be < 2s, got {max_response_time:.3f}s"
        
        print(f"\n📊 Concurrent Request Performance:")
        print(f"  Total requests: {len(results)}")
        print(f"  Successful: {len(successful_requests)}")
        print(f"  Failed: {len(failed_requests)}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Max response time: {max_response_time:.3f}s")
    
    def test_memory_usage_during_requests(self, client):
        """Test memory usage during API requests."""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests
        for _ in range(50):
            client.get('/api/system-info')
            client.get('/api/platform-stats')
            client.get('/api/health-check')
        
        # Force garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\n📊 Memory Usage:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  Final: {final_memory:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")
        
        # Memory increase should be reasonable (less than 50MB for 150 requests)
        assert memory_increase < 50, f"Memory increase should be < 50MB, got {memory_increase:.2f}MB"
    
    def test_api_payload_sizes(self, client):
        """Test API response payload sizes."""
        endpoints = [
            '/api/system-info',
            '/api/platform-stats',
            '/api/health-check'
        ]
        
        payload_sizes = {}
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            payload_size = len(response.data)
            payload_sizes[endpoint] = payload_size
            
            # Payload should be reasonable size (less than 100KB)
            assert payload_size < 100 * 1024, f"{endpoint} payload too large: {payload_size} bytes"
            
            # Payload should contain actual data (more than 100 bytes)
            assert payload_size > 100, f"{endpoint} payload too small: {payload_size} bytes"
        
        print(f"\n📊 API Payload Sizes:")
        for endpoint, size in payload_sizes.items():
            print(f"  {endpoint}: {size:,} bytes ({size/1024:.1f} KB)")
    
    def test_json_parsing_performance(self, client):
        """Test JSON parsing performance."""
        endpoints = ['/api/system-info', '/api/platform-stats', '/api/health-check']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            # Measure JSON parsing time
            start_time = time.perf_counter()
            for _ in range(100):  # Parse 100 times to get measurable time
                json.loads(response.data)
            end_time = time.perf_counter()
            
            parsing_time = (end_time - start_time) / 100  # Average per parse
            
            # JSON parsing should be fast (less than 1ms per parse)
            assert parsing_time < 0.001, f"{endpoint} JSON parsing too slow: {parsing_time:.6f}s"
    
    def test_database_query_performance(self, client):
        """Test database query performance."""
        # Add some test data first
        with client.application.app_context():
            from models import Problem, Submission
            
            # Create test problems if they don't exist
            try:
                for i in range(10):
                    Problem.create(
                        title=f"Test Problem {i}",
                        difficulty="Easy" if i < 5 else "Medium",
                        description=f"Test description {i}",
                        test_cases=json.dumps([{"input": "test", "output": "test"}])
                    )
            except Exception:
                pass  # Problems might already exist
        
        # Test query performance
        start_time = time.perf_counter()
        response = client.get('/api/platform-stats')
        end_time = time.perf_counter()
        
        query_time = end_time - start_time
        
        assert response.status_code == 200
        assert query_time < 0.2, f"Database queries should complete within 200ms, got {query_time:.3f}s"
        
        print(f"\n📊 Database Query Performance: {query_time:.3f}s")
    
    def test_caching_effectiveness(self, client):
        """Test caching effectiveness for repeated requests."""
        endpoint = '/api/system-info'
        
        # First request (cold)
        start_time = time.perf_counter()
        response1 = client.get(endpoint)
        cold_time = time.perf_counter() - start_time
        
        # Second request (potentially cached)
        start_time = time.perf_counter()
        response2 = client.get(endpoint)
        warm_time = time.perf_counter() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Responses should be similar (allowing for timestamp differences)
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        # Basic structure should be the same
        assert data1['status'] == data2['status']
        assert 'data' in data1 and 'data' in data2
        
        print(f"\n📊 Caching Performance:")
        print(f"  Cold request: {cold_time:.3f}s")
        print(f"  Warm request: {warm_time:.3f}s")
        
        # If caching is implemented, warm request should be faster
        # If not, they should be similar (within reasonable variance)
        time_ratio = warm_time / cold_time if cold_time > 0 else 1
        assert time_ratio < 2.0, f"Warm request shouldn't be much slower than cold: {time_ratio:.2f}x"
    
    def test_error_handling_performance(self, client):
        """Test performance of error handling."""
        # Test with invalid endpoints
        invalid_endpoints = [
            '/api/non-existent',
            '/api/system-info/invalid',
            '/api/platform-stats?invalid=param'
        ]
        
        for endpoint in invalid_endpoints:
            start_time = time.perf_counter()
            response = client.get(endpoint)
            end_time = time.perf_counter()
            
            response_time = end_time - start_time
            
            # Error responses should be fast
            assert response_time < 0.1, f"Error response should be fast: {response_time:.3f}s"
            
            # Should return proper error status
            assert response.status_code in [400, 404, 500]
    
    def test_large_dataset_performance(self, client):
        """Test performance with larger datasets."""
        # Mock large dataset
        with patch('api_helpers.get_enhanced_platform_stats') as mock_stats:
            # Create mock data with many entries
            large_stats = {
                'basic': {
                    'total_problems': 10000,
                    'total_submissions': 500000,
                    'total_users': 50000,
                    'success_rate': 67.8
                },
                'languages': [
                    {'name': f'Language{i}', 'submissions': 1000 + i * 100, 'success_rate': 60 + i}
                    for i in range(50)  # 50 languages
                ],
                'difficulty': {
                    'Easy': 4000,
                    'Medium': 3500,
                    'Hard': 2500
                },
                'performance': {
                    'avg_response_time': 150,
                    'peak_concurrent_users': 1000,
                    'uptime_percentage': 99.9
                }
            }
            mock_stats.return_value = large_stats
            
            # Test performance with large dataset
            start_time = time.perf_counter()
            response = client.get('/api/platform-stats')
            end_time = time.perf_counter()
            
            response_time = end_time - start_time
            payload_size = len(response.data)
            
            assert response.status_code == 200
            assert response_time < 1.0, f"Large dataset should process within 1s: {response_time:.3f}s"
            
            print(f"\n📊 Large Dataset Performance:")
            print(f"  Response time: {response_time:.3f}s")
            print(f"  Payload size: {payload_size:,} bytes ({payload_size/1024:.1f} KB)")
    
    def test_stress_test_rapid_requests(self, client):
        """Stress test with rapid consecutive requests."""
        num_requests = 100
        endpoint = '/api/system-info'
        
        start_time = time.perf_counter()
        
        # Make rapid requests
        responses = []
        for _ in range(num_requests):
            response = client.get(endpoint)
            responses.append(response)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Check all responses
        successful = sum(1 for r in responses if r.status_code == 200)
        failed = num_requests - successful
        
        requests_per_second = num_requests / total_time
        avg_response_time = total_time / num_requests
        
        print(f"\n📊 Stress Test Results:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Requests/second: {requests_per_second:.1f}")
        print(f"  Avg response time: {avg_response_time:.3f}s")
        
        # Performance assertions
        assert failed == 0, f"All requests should succeed, got {failed} failures"
        assert requests_per_second > 10, f"Should handle >10 req/s, got {requests_per_second:.1f}"
        assert avg_response_time < 0.1, f"Avg response time should be <100ms, got {avg_response_time:.3f}s"


class TestSystemInfoModalResourceUsage:
    """Test suite for resource usage monitoring."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(':memory:')
                yield client
    
    def test_cpu_usage_during_requests(self, client):
        """Test CPU usage during API requests."""
        process = psutil.Process()
        
        # Baseline CPU usage
        baseline_cpu = process.cpu_percent(interval=1)
        
        # Make requests while monitoring CPU
        start_time = time.time()
        cpu_samples = []
        
        def monitor_cpu():
            while time.time() - start_time < 5:  # Monitor for 5 seconds
                cpu_samples.append(process.cpu_percent(interval=0.1))
                time.sleep(0.1)
        
        # Start CPU monitoring in background
        cpu_thread = threading.Thread(target=monitor_cpu)
        cpu_thread.start()
        
        # Make requests
        for _ in range(20):
            client.get('/api/system-info')
            client.get('/api/platform-stats')
            time.sleep(0.1)
        
        cpu_thread.join()
        
        if cpu_samples:
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            max_cpu = max(cpu_samples)
            
            print(f"\n📊 CPU Usage:")
            print(f"  Baseline: {baseline_cpu:.1f}%")
            print(f"  Average during requests: {avg_cpu:.1f}%")
            print(f"  Peak during requests: {max_cpu:.1f}%")
            
            # CPU usage should be reasonable
            assert max_cpu < 80, f"CPU usage should stay below 80%, got {max_cpu:.1f}%"
    
    def test_memory_leak_detection(self, client):
        """Test for memory leaks over extended usage."""
        process = psutil.Process()
        
        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = [initial_memory]
        
        # Make many requests and track memory
        for i in range(100):
            client.get('/api/system-info')
            client.get('/api/platform-stats')
            client.get('/api/health-check')
            
            if i % 10 == 0:  # Sample every 10 requests
                gc.collect()  # Force garbage collection
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
        
        final_memory = memory_samples[-1]
        memory_growth = final_memory - initial_memory
        
        # Calculate memory growth trend
        if len(memory_samples) > 2:
            # Simple linear regression to detect trend
            n = len(memory_samples)
            x_sum = sum(range(n))
            y_sum = sum(memory_samples)
            xy_sum = sum(i * memory_samples[i] for i in range(n))
            x2_sum = sum(i * i for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            
            print(f"\n📊 Memory Leak Detection:")
            print(f"  Initial memory: {initial_memory:.2f} MB")
            print(f"  Final memory: {final_memory:.2f} MB")
            print(f"  Total growth: {memory_growth:.2f} MB")
            print(f"  Growth trend: {slope:.4f} MB per sample")
            
            # Memory growth should be minimal
            assert memory_growth < 100, f"Memory growth should be <100MB, got {memory_growth:.2f}MB"
            assert slope < 1.0, f"Memory growth trend should be <1MB per sample, got {slope:.4f}"
    
    def test_file_descriptor_usage(self, client):
        """Test file descriptor usage."""
        process = psutil.Process()
        
        try:
            initial_fds = process.num_fds()
            
            # Make many requests
            for _ in range(50):
                client.get('/api/system-info')
                client.get('/api/platform-stats')
                client.get('/api/health-check')
            
            final_fds = process.num_fds()
            fd_growth = final_fds - initial_fds
            
            print(f"\n📊 File Descriptor Usage:")
            print(f"  Initial FDs: {initial_fds}")
            print(f"  Final FDs: {final_fds}")
            print(f"  Growth: {fd_growth}")
            
            # File descriptor growth should be minimal
            assert fd_growth < 10, f"FD growth should be <10, got {fd_growth}"
            
        except AttributeError:
            # num_fds() not available on Windows
            pytest.skip("File descriptor monitoring not available on this platform")
    
    def test_database_connection_pooling(self, client):
        """Test database connection efficiency."""
        # Make concurrent requests to test connection pooling
        def make_requests():
            responses = []
            for _ in range(10):
                response = client.get('/api/platform-stats')  # DB-heavy endpoint
                responses.append(response.status_code)
            return responses
        
        # Run multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_requests) for _ in range(3)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        all_responses = [status for thread_results in results for status in thread_results]
        successful = sum(1 for status in all_responses if status == 200)
        
        print(f"\n📊 Database Connection Test:")
        print(f"  Total requests: {len(all_responses)}")
        print(f"  Successful: {successful}")
        print(f"  Success rate: {successful/len(all_responses)*100:.1f}%")
        
        assert successful == len(all_responses), "All database requests should succeed"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])