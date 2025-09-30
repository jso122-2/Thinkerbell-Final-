#!/usr/bin/env python3
"""
⚡ Performance and Stress Testing Suite for Thinkerbell Model
===========================================================

This suite tests the model's performance under various stress conditions:
1. High-volume concurrent requests
2. Large input sizes
3. Memory usage patterns
4. Response time consistency
5. Resource exhaustion scenarios
6. Rate limiting behavior
"""

import requests
import json
import time
import threading
import statistics
import psutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple
import random
import string

API_BASE_URL = "http://localhost:8000"

class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                
                self.cpu_samples.append(cpu_percent)
                self.memory_samples.append(memory_info.percent)
                
                time.sleep(0.5)
            except Exception:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.cpu_samples or not self.memory_samples:
            return {"error": "No samples collected"}
        
        return {
            "cpu": {
                "avg": statistics.mean(self.cpu_samples),
                "max": max(self.cpu_samples),
                "min": min(self.cpu_samples),
                "samples": len(self.cpu_samples)
            },
            "memory": {
                "avg": statistics.mean(self.memory_samples),
                "max": max(self.memory_samples),
                "min": min(self.memory_samples),
                "samples": len(self.memory_samples)
            }
        }

class StressTester:
    """Main stress testing class"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.results = []
        self.monitor = PerformanceMonitor()
    
    def generate_large_text(self, size: int) -> str:
        """Generate large text input for stress testing"""
        base_text = "I need a comprehensive influencer marketing agreement for social media campaigns. "
        repetitions = max(1, size // len(base_text))
        return base_text * repetitions
    
    def generate_random_text(self, length: int) -> str:
        """Generate random text of specified length"""
        words = ["contract", "influencer", "marketing", "social", "media", "brand", "content", 
                "payment", "agreement", "terms", "conditions", "deliverables", "campaign",
                "Instagram", "TikTok", "YouTube", "collaboration", "partnership", "exclusive"]
        
        text = []
        current_length = 0
        
        while current_length < length:
            word = random.choice(words)
            if current_length + len(word) + 1 <= length:
                text.append(word)
                current_length += len(word) + 1
            else:
                break
        
        return " ".join(text)
    
    def single_request(self, input_data: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Make a single API request and measure performance"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json=input_data,
                timeout=timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response_time,
                "input_size": len(input_data.get("human_example", "")),
                "timestamp": start_time
            }
            
            if response.status_code == 200:
                data = response.json()
                result.update({
                    "output_size": len(data.get("generated_text", "")),
                    "similarity_score": data.get("similarity_to_example", 0),
                    "word_count": data.get("word_count", 0),
                    "processing_time": data.get("processing_time", 0)
                })
            else:
                result["error"] = response.text[:200]  # Truncate error message
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout",
                "response_time": timeout,
                "input_size": len(input_data.get("human_example", "")),
                "timestamp": start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "input_size": len(input_data.get("human_example", "")),
                "timestamp": start_time
            }
    
    def test_input_size_scaling(self) -> Dict[str, Any]:
        """Test how performance scales with input size"""
        print("\n📏 Testing Input Size Scaling")
        print("-" * 40)
        
        sizes = [100, 500, 1000, 2000, 5000, 10000, 20000]
        results = []
        
        self.monitor.start_monitoring()
        
        for size in sizes:
            print(f"Testing input size: {size} characters")
            
            input_data = {
                "human_example": self.generate_large_text(size),
                "target_length": 700,
                "style_preference": "professional",
                "document_type": "legal_template"
            }
            
            result = self.single_request(input_data, timeout=60)
            result["test_size"] = size
            results.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} Size {size}: {result['response_time']:.2f}s")
            
            # Brief pause between tests
            time.sleep(1)
        
        self.monitor.stop_monitoring()
        
        return {
            "test_name": "input_size_scaling",
            "results": results,
            "system_stats": self.monitor.get_stats()
        }
    
    def test_concurrent_requests(self, num_requests: int = 10, max_workers: int = 5) -> Dict[str, Any]:
        """Test concurrent request handling"""
        print(f"\n🔄 Testing Concurrent Requests ({num_requests} requests, {max_workers} workers)")
        print("-" * 60)
        
        # Prepare test data
        test_inputs = []
        for i in range(num_requests):
            test_inputs.append({
                "human_example": f"Test request {i+1}: " + self.generate_random_text(200),
                "target_length": 700,
                "style_preference": "professional",
                "document_type": "legal_template"
            })
        
        results = []
        start_time = time.time()
        
        self.monitor.start_monitoring()
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.single_request, input_data): i 
                for i, input_data in enumerate(test_inputs)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    result["request_index"] = index
                    results.append(result)
                    
                    status = "✅" if result["success"] else "❌"
                    print(f"  {status} Request {index+1}: {result['response_time']:.2f}s")
                    
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "request_index": index,
                        "response_time": 0
                    })
                    print(f"  ❌ Request {index+1}: Exception - {str(e)}")
        
        total_time = time.time() - start_time
        self.monitor.stop_monitoring()
        
        # Calculate statistics
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        stats = {}
        if response_times:
            stats = {
                "total_requests": num_requests,
                "successful_requests": len(successful_requests),
                "failed_requests": num_requests - len(successful_requests),
                "success_rate": len(successful_requests) / num_requests * 100,
                "total_time": total_time,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times),
                "requests_per_second": len(successful_requests) / total_time
            }
        
        return {
            "test_name": "concurrent_requests",
            "results": results,
            "statistics": stats,
            "system_stats": self.monitor.get_stats()
        }
    
    def test_sustained_load(self, duration_seconds: int = 60, requests_per_second: float = 2) -> Dict[str, Any]:
        """Test sustained load over time"""
        print(f"\n⏱️ Testing Sustained Load ({duration_seconds}s at {requests_per_second} req/s)")
        print("-" * 60)
        
        results = []
        start_time = time.time()
        request_count = 0
        
        self.monitor.start_monitoring()
        
        while time.time() - start_time < duration_seconds:
            request_start = time.time()
            
            input_data = {
                "human_example": f"Sustained load test request {request_count+1}: " + self.generate_random_text(150),
                "target_length": 500,
                "style_preference": "professional",
                "document_type": "legal_template"
            }
            
            result = self.single_request(input_data, timeout=30)
            result["request_number"] = request_count + 1
            result["elapsed_time"] = time.time() - start_time
            results.append(result)
            
            request_count += 1
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} Request {request_count}: {result['response_time']:.2f}s (elapsed: {result['elapsed_time']:.1f}s)")
            
            # Rate limiting
            request_duration = time.time() - request_start
            sleep_time = max(0, (1.0 / requests_per_second) - request_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        total_time = time.time() - start_time
        self.monitor.stop_monitoring()
        
        # Calculate statistics
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        stats = {}
        if response_times:
            stats = {
                "duration": total_time,
                "total_requests": len(results),
                "successful_requests": len(successful_requests),
                "failed_requests": len(results) - len(successful_requests),
                "success_rate": len(successful_requests) / len(results) * 100,
                "actual_requests_per_second": len(results) / total_time,
                "avg_response_time": statistics.mean(response_times),
                "response_time_trend": self._calculate_trend(response_times)
            }
        
        return {
            "test_name": "sustained_load",
            "results": results,
            "statistics": stats,
            "system_stats": self.monitor.get_stats()
        }
    
    def test_memory_stress(self) -> Dict[str, Any]:
        """Test memory usage with large inputs"""
        print("\n🧠 Testing Memory Stress")
        print("-" * 30)
        
        # Test with increasingly large inputs
        sizes = [1000, 5000, 10000, 25000, 50000, 100000]
        results = []
        
        self.monitor.start_monitoring()
        
        for size in sizes:
            print(f"Testing memory with {size} character input")
            
            # Create large input
            large_input = self.generate_large_text(size)
            
            input_data = {
                "human_example": large_input,
                "target_length": 1000,
                "style_preference": "professional",
                "document_type": "legal_template"
            }
            
            # Monitor memory before request
            memory_before = psutil.virtual_memory().percent
            
            result = self.single_request(input_data, timeout=120)
            
            # Monitor memory after request
            memory_after = psutil.virtual_memory().percent
            
            result.update({
                "input_size": size,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_delta": memory_after - memory_before
            })
            
            results.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"  {status} Size {size}: {result['response_time']:.2f}s, Memory: {memory_before:.1f}% → {memory_after:.1f}%")
            
            # Brief pause for memory cleanup
            time.sleep(2)
        
        self.monitor.stop_monitoring()
        
        return {
            "test_name": "memory_stress",
            "results": results,
            "system_stats": self.monitor.get_stats()
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate if values are trending up, down, or stable"""
        if len(values) < 2:
            return "insufficient_data"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        diff_percent = (second_avg - first_avg) / first_avg * 100
        
        if diff_percent > 10:
            return "increasing"
        elif diff_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def run_all_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        print("⚡ PERFORMANCE & STRESS TEST SUITE")
        print("=" * 50)
        
        all_results = {}
        
        # Test 1: Input size scaling
        try:
            all_results["input_size_scaling"] = self.test_input_size_scaling()
        except Exception as e:
            print(f"❌ Input size scaling test failed: {e}")
            all_results["input_size_scaling"] = {"error": str(e)}
        
        # Test 2: Concurrent requests
        try:
            all_results["concurrent_requests"] = self.test_concurrent_requests(num_requests=15, max_workers=5)
        except Exception as e:
            print(f"❌ Concurrent requests test failed: {e}")
            all_results["concurrent_requests"] = {"error": str(e)}
        
        # Test 3: Sustained load
        try:
            all_results["sustained_load"] = self.test_sustained_load(duration_seconds=30, requests_per_second=1.5)
        except Exception as e:
            print(f"❌ Sustained load test failed: {e}")
            all_results["sustained_load"] = {"error": str(e)}
        
        # Test 4: Memory stress
        try:
            all_results["memory_stress"] = self.test_memory_stress()
        except Exception as e:
            print(f"❌ Memory stress test failed: {e}")
            all_results["memory_stress"] = {"error": str(e)}
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 50)
        
        for test_name, test_result in all_results.items():
            if "error" in test_result:
                print(f"❌ {test_name}: Failed - {test_result['error']}")
            elif "statistics" in test_result:
                stats = test_result["statistics"]
                if "success_rate" in stats:
                    print(f"✅ {test_name}: {stats['success_rate']:.1f}% success rate")
                else:
                    print(f"✅ {test_name}: Completed")
            else:
                print(f"✅ {test_name}: Completed")
        
        return all_results

def main():
    """Main test runner"""
    # Check server connection
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not ready: {response.status_code}")
            sys.exit(1)
        print("✅ Server connection verified")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print("Make sure the backend server is running: python backend_api_server.py")
        sys.exit(1)
    
    # Run tests
    tester = StressTester()
    results = tester.run_all_performance_tests()
    
    # Save results
    timestamp = int(time.time())
    filename = f"performance_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")

if __name__ == "__main__":
    main()
