import time, threading, random
from datetime import datetime
from locust import HttpUser, task, constant_throughput, events

# Global counter and lock
request_counter = 1
counter_lock = threading.Lock()

log_lock = threading.Lock()
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"OpenEdgeTTS_{TIMESTAMP}.log"

failed_list = []
fail_lock = threading.Lock()

class OpenEdgeTTSUser(HttpUser):
    wait_time = constant_throughput(1)

    def on_start(self):
        self.client.headers = {
            "Authorization": "Bearer your_api_key_here",
            "Content-Type": "application/json"
        }

    @task
    def audio_speech(self):
        global request_counter, counter_lock, failed_list, fail_lock

        with fail_lock:
            if len(failed_list) == 0:
                with counter_lock:
                    current_count = f"{request_counter}"
                    request_counter += 1
            else:
                current_count = f"{failed_list[0]} + 1"
                failed_list.remove(failed_list[0])
                seconds = random.uniform(2, 3)
                time.sleep(seconds)

        start_time = time.perf_counter()

        # Log request start
        with log_lock:
            with open(LOG_FILE, "a") as f:
                f.write(f"Sending request {current_count}...\n")

        with self.client.post(
            url = "/v1/audio/speech",
            json = {
                "input":"Welcome to our module on Working at Heights Safety at Maple Lodge Farms. The image you see represents the varying conditions our workers might face during their shifts, reminding us why safety is so crucial. In this section, we'll explore our essential safety protocols for working at heights. Pay special attention to the height threshold of 6 feet, or 1.8 meters - this is your key indicator for when fall protection equipment becomes mandatory. Every single point you see listed here has been established through years of experience and best practices. These requirements aren't just rules on paper - they're vital practices that protect lives. Notice how each requirement builds upon the others: from equipment requirements to inspection protocols, secure attachments, and weather assessments. Each element plays a crucial role in our comprehensive safety system. In the next slide, we'll break down how to properly assess risks before beginning any work at heights, so stay tuned to learn these essential skills.",
                "response_format": "mp3",
                "speed": 1.0
            },
            catch_response = True
        ) as response:
            if response.status_code != 200:
                # Log error details
                error_msg = f"[#{current_count}] Error 0 Time: {time.perf_counter() - start_time}" \
                    if response.status_code == 0 else \
                    f"[#{current_count}] Status error: {response.status_code}"
                
                with log_lock:
                    with open(LOG_FILE, "a") as f:
                        f.write(f"{error_msg}\n")
                    
                    if current_count.count("+") >= 2:
                        with open(LOG_FILE, "a") as f:
                            f.write(f"[#{current_count}] failed finally\n")
                    else:
                        with fail_lock:
                            failed_list.append(current_count)
                
                response.failure(error_msg)
            else:
                # Log success
                with log_lock:
                    with open(LOG_FILE, "a") as f:
                        f.write(f"[#{current_count}] Success in {time.perf_counter() - start_time:.2f}s\n")

    # Custom metrics validation (add to your locustfile)
    @events.request.add_listener
    def validate_metrics(request_type, name, response_time, response_length, exception, **kwargs):
        # Error rate tracking (automatically tracked by Locust)
        if exception:
            with log_lock:
                with open(LOG_FILE, "a") as f:
                    f.write(f"Request failed: {exception}\n")
