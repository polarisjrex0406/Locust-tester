import time, threading
from locust import HttpUser, task, constant_throughput, events, between

# Global counter and lock
request_counter = 1
counter_lock = threading.Lock()

class OpenEdgeTTSUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        self.client.headers = {
            "Authorization": "Bearer your_api_key_here",
            "Content-Type": "application/json"
        }

    @task
    def audio_speech(self):
        global request_counter, counter_lock

        with counter_lock:  # Thread-safe counter increment
            current_count = request_counter
            request_counter += 1

        start_time = time.perf_counter()
        print(f"Sending a request {current_count}...")
        with self.client.post(
            url = "/v1/audio/speech",
            json = {
                "input":"Welcome to this important training on Environmental Emergency Preparedness. This introductory slide sets the foundation for understanding how to handle environmental emergencies in our industrial workplace. The key message here is that emergency preparedness is everyone's responsibility - from frontline workers to management. Take note of three main points we'll be covering: What constitutes an environmental emergency and why awareness matters. How to effectively manage environmental emergencies when they occur. Your personal role in maintaining workplace safety and responding to emergencies. As you progress through this training, keep in mind that these skills and knowledge are essential for protecting yourself, your colleagues, and the environment.",
                "response_format": "mp3",
                "speed": 1.0
            },
            catch_response = True
        ) as response:
            if response.status_code != 200:
                if response.status_code == 0:
                    print(f"[#{current_count}] Error 0 Time: {time.perf_counter() - start_time}")
                else:
                    response.failure(f"[#{current_count}] Status code error: {response.status_code}")
            else:
                print(f"[#{current_count}] Success Time: {time.perf_counter() - start_time}")

    # Custom metrics validation (add to your locustfile)
    @events.request.add_listener
    def validate_metrics(request_type, name, response_time, response_length, exception, **kwargs):
        # Latency check
        # if response_time > 500:
        #     print(f"High latency: {response_time}ms")
        
        # Error rate tracking (automatically tracked by Locust)
        if exception:
            print(f"Request failed: {exception}")
