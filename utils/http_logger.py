import logging
import os
from inspect import stack
from json import dumps as json_dumps, JSONDecodeError
from typing import Optional
from pathlib import Path

import httpx

# Configure logging to file (in project root)
LOG_FILE = Path(__file__).parent.parent / "pytest.log"


# Create logger
log = logging.getLogger("http_logger")
log.setLevel(logging.INFO)

# Avoid adding multiple handlers if module is reloaded
if not log.handlers:
    # File handler - overwrite on each test run
    file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    log.addHandler(file_handler)
    
    # Console handler (optional - comment out if too verbose)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)


class LogHTTPResponse:
    def __init__(self, response: httpx.Response, stage: str, include_response_body: bool = True):
        self.stage = stage
        if isinstance(response, httpx.Response):
            self.response = response
        else:
            raise TypeError("LogHTTPResponse takes only httpx.Response type")
        
        # Mask authorization header for security
        request_headers = dict(self.response.request.headers)
        if request_headers.get("authorization"):
            auth_value = request_headers["authorization"]
            request_headers["authorization"] = f'{auth_value[:10]}...{auth_value[-3:]}'
        self.request_headers = request_headers
        
        self._log_context()
        self._log_request()
        self._log_response(include_response_body)

    def _log_context(self):
        context_name = "unknown"
        for elem in stack():
            func_name = elem[3]
            if "_fixture" in func_name or "_case" in func_name or "test_" in func_name:
                context_name = func_name
                break
        log.info(f"Context: {self.stage} / {context_name}")

    def _log_request(self):
        request = self.response.request
        elapsed = getattr(self.response, 'elapsed', None)
        elapsed_str = f" / {elapsed}" if elapsed else ""
        
        log.info(f">REQ Url: {request.url}")
        log.info(f">REQ Common: {request.method} / {self.response.status_code}{elapsed_str}")
        log.info(f">REQ Headers: {self.request_headers}")
        
        body = self._get_request_body()
        log.info(f">REQ Body:\n{body}")

    def _get_request_body(self) -> Optional[str]:
        request = self.response.request
        if request.content:
            try:
                return request.content.decode('utf-8')
            except UnicodeDecodeError:
                return f"<binary data: {len(request.content)} bytes>"
        return None

    def _log_response(self, include_response_body: bool):
        try:
            body = json_dumps(self.response.json(), sort_keys=True, indent=4)
        except (JSONDecodeError, ValueError):
            body = self.response.text if len(self.response.text) > 0 else None
        
        log.info(f"<RES Headers: {dict(self.response.headers)}")
        if include_response_body:
            log.info(f"<RES Body:\n{body}\n<---------------------------------------------------------\n")


def log_response(response: httpx.Response, stage: str = "API", include_body: bool = True) -> httpx.Response:
    LogHTTPResponse(response, stage, include_body)
    return response
