import json
import os
from datetime import datetime
import traceback


class ErrorHandler:

    def __init__(self):
        self.log_file = "APP/LOGS/error.json"

        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def write_log(self, log_data):
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)

            data.append(log_data)

            with open(self.log_file, "w") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print("Logging Failed:", e)

    def log_error(self, class_name, function_name, message):
        log_data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "ERROR",
            "class": class_name,
            "function": function_name,
            "message": message
        }
        self.write_log(log_data)

    def log_exception(self, class_name, function_name, e):
        tb = traceback.extract_tb(e.__traceback__)[-1]

        log_data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "EXCEPTION",
            "class": class_name,
            "function": function_name,
            "message": str(e),
            "line": tb.lineno,
            "file": tb.filename
        }
        self.write_log(log_data)



error_handler = ErrorHandler()