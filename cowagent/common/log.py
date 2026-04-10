import io
import os
import logging
import sys


def _get_log_path() -> str:
    """Get the log file path, preferring logs/ dir at project root."""
    # Try to find project root (go up from this file: cowagent/common/log.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, "cowagent.log")


def _reset_logger(log):
    for handler in log.handlers:
        handler.close()
        log.removeHandler(handler)
        del handler
    log.handlers.clear()
    log.propagate = False
    stdout = sys.stdout
    if hasattr(stdout, "buffer"):
        stdout = io.TextIOWrapper(
            stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
        )
    console_handle = logging.StreamHandler(stdout)
    console_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    file_handle = logging.FileHandler(_get_log_path(), encoding="utf-8")
    file_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log.addHandler(file_handle)
    log.addHandler(console_handle)


def _get_logger():
    log = logging.getLogger("log")
    _reset_logger(log)
    log.setLevel(logging.INFO)
    return log


# 日志句柄
logger = _get_logger()
