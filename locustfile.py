from locust import HttpUser, task, constant

class HelloWorldUser(HttpUser):
    wait_time = constant(1)
    
    def on_start(self):
        self.client.headers = {
            "Authorization": "Bearer your_api_key_here",
            "Content-Type": "application/json"
        }

    @task
    def hello_world(self):
        self.client.get("/v1/models")
