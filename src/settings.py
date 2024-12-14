from utils.logger import Logger
import yaml

rlog = Logger("Rate-Limiter").get_logger()

class Config:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get_upstream(self):
        return self.config["upstream"]
    

HTTP_429 = '''
http_response = """HTTP/1.1 429 Too Many Requests
Content-Type: text/plain

Too many requests. Please try again later.
"""
'''