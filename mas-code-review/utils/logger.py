# utils/logger.py
import json
import logging
import os
from datetime import datetime


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Generate timestamped log filename
log_filename = f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure file logger
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()  # Also prints to console
    ]
)

logger = logging.getLogger("MAS")


def log_event(
    agent: str,
    event: str,
    detail: str,
    tool: str = None,
    input_data: dict = None,
    output_data: dict = None
) -> str:
    """
    Logs a structured event from an agent to both
    the console and a timestamped log file.

    Args:
        agent     (str): Name of the agent logging the event.
        event     (str): Event type e.g. 'start', 'tool_call',
                         'complete', 'error'.
        detail    (str): Human-readable description.
        tool      (str): Tool name if this is a tool call.
        input_data  (dict): Input passed to tool or agent.
        output_data (dict): Output returned from tool or agent.

    Returns:
        str: The formatted log entry string.
    """
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "agent": agent,
        "event": event,
        "detail": detail,
    }

    if tool:
        entry["tool"] = tool
    if input_data:
        entry["input"] = input_data
    if output_data:
        entry["output"] = output_data

    log_line = json.dumps(entry)
    logger.info(log_line)
    return log_line