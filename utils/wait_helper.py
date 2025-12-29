import time
import allure
from typing import Callable, Any, Optional


class WaitHelper:

    @staticmethod
    @allure.step("Wait for condition: {description}")
    def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout: int = 300,
        poll_interval: int = 5,
        description: str = "condition to be met",
        error_message: Optional[str] = None
    ) -> bool:
        """
        Wait for a condition to become true.
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            poll_interval: Time between checks in seconds
            description: Description of what we're waiting for
            error_message: Custom error message if timeout occurs
            
        Returns:
            True if condition met, False if timeout
        """
        start_time = time.time()
        elapsed = 0
        
        while elapsed < timeout:
            try:
                if condition_func():
                    allure.attach(
                        f"Condition met after {elapsed:.1f} seconds",
                        "Wait Result",
                        allure.attachment_type.TEXT
                    )
                    return True
            except Exception as e:
                allure.attach(str(e), "Condition Check Error", allure.attachment_type.TEXT)
            
            time.sleep(poll_interval)
            elapsed = time.time() - start_time
            
            if elapsed % 30 == 0:
                allure.attach(
                    f"Still waiting... ({elapsed:.0f}s / {timeout}s)",
                    "Progress",
                    allure.attachment_type.TEXT
                )
        
        msg = error_message or f"Timeout waiting for {description} after {timeout} seconds"
        allure.attach(msg, "Timeout Error", allure.attachment_type.TEXT)
        return False

    @staticmethod
    @allure.step("Wait for value: {description}")
    def wait_for_value(
        value_func: Callable[[], Any],
        expected_value: Any,
        timeout: int = 300,
        poll_interval: int = 5,
        description: str = "expected value"
    ) -> bool:
        """
        Wait for a function to return an expected value.
        
        Args:
            value_func: Function that returns a value to check
            expected_value: The value we're waiting for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between checks in seconds
            description: Description of what we're waiting for
            
        Returns:
            True if value matches, False if timeout
        """
        def condition():
            actual = value_func()
            return actual == expected_value
        
        return WaitHelper.wait_for_condition(
            condition,
            timeout,
            poll_interval,
            f"{description} to equal {expected_value}"
        )

    @staticmethod
    @allure.step("Wait for state transition: {description}")
    def wait_for_state_transition(
        state_func: Callable[[], str],
        target_state: str,
        timeout: int = 300,
        poll_interval: int = 5,
        description: str = "state transition"
    ) -> bool:
        """
        Wait for state to transition to target state.
        
        Args:
            state_func: Function that returns current state
            target_state: The state we're waiting for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between checks in seconds
            description: Description of the state transition
            
        Returns:
            True if state reached, False if timeout
        """
        start_time = time.time()
        last_state = None
        
        while time.time() - start_time < timeout:
            try:
                current_state = state_func()
                
                if current_state != last_state:
                    allure.attach(
                        f"State changed: {last_state} -> {current_state}",
                        "State Transition",
                        allure.attachment_type.TEXT
                    )
                    last_state = current_state
                
                if current_state == target_state:
                    elapsed = time.time() - start_time
                    allure.attach(
                        f"Target state '{target_state}' reached after {elapsed:.1f} seconds",
                        "Success",
                        allure.attachment_type.TEXT
                    )
                    return True
                    
            except Exception as e:
                allure.attach(str(e), "State Check Error", allure.attachment_type.TEXT)
            
            time.sleep(poll_interval)
        
        allure.attach(
            f"Timeout waiting for state '{target_state}'. Last state: {last_state}",
            "Timeout Error",
            allure.attachment_type.TEXT
        )
        return False
