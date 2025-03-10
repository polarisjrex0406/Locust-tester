from locust import HttpUser, task, constant_throughput, events, between

class OpenEdgeTTSUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        self.client.headers = {
            "Authorization": "Bearer your_api_key_here",
            "Content-Type": "application/json"
        }

    @task
    def audio_speech(self):
        with self.client.post(
            url = "/v1/audio/speech",
            json = {
                "input":"What can I do for you?",
                "voice":"en-US-EmmaNeural",
                "response_format": "mp3",
                "speed": 1.0
            },
            catch_response = True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status code error: {response.status_code}")

    # Custom metrics validation (add to your locustfile)
    @events.request.add_listener
    def validate_metrics(request_type, name, response_time, response_length, exception, **kwargs):
        # Latency check
        # if response_time > 500:
        #     print(f"High latency: {response_time}ms")
        
        # Error rate tracking (automatically tracked by Locust)
        if exception:
            print(f"Request failed: {exception}")
