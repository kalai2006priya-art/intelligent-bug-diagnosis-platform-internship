import re
from typing import Dict, Optional, Tuple, List

# Regular expression patterns for various runtime environments
JAVA_EXCEPTION_REGEX = re.compile(
    r'(?:Exception in thread "[^"]*"\s+)?([a-zA-Z0-9_$.]+(?:Exception|Error|Throwable))(?::\s*(.*))?',
    re.MULTILINE
)
JAVA_FRAME_REGEX = re.compile(
    r'^\s*at\s+([a-zA-Z0-9_$.]+)\.([a-zA-Z0-9_$<>]+)\(([^:)]+):?(\d+)?\)',
    re.MULTILINE
)

PYTHON_TRACEBACK_REGEX = re.compile(
    r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+([a-zA-Z0-9_]+)',
    re.MULTILINE
)
PYTHON_EXCEPTION_REGEX = re.compile(
    r'^([a-zA-Z0-9_]+Error|[a-zA-Z0-9_]+Exception|AssertionError):\s*(.*)$',
    re.MULTILINE
)

JS_ERROR_REGEX = re.compile(
    r'^([a-zA-Z0-9_]+Error):\s*(.*)$',
    re.MULTILINE
)
JS_FRAME_REGEX = re.compile(
    r'^\s*at\s+(?:([a-zA-Z0-9_$.]+)\s+\()?(.*?):(\d+):(\d+)\)?',
    re.MULTILINE
)

CPP_CRASH_REGEX = re.compile(
    r'Crash\s*\[@\s*([^\]]+)\](?:\s*\[([^:]+):(\d+)\])?',
    re.MULTILINE
)

def parse_stack_trace_heuristically(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Parses Java, Python, C++, and JavaScript stack traces to extract:
    - exception_type
    - error_message
    - failure_point (e.g. AuthService.java:42)
    - affected_code_path (e.g. Controller.login -> Service.auth)
    """
    if not raw_text or len(raw_text.strip()) < 10:
        return {
            "status": "Insufficient Evidence",
            "exception_type": None,
            "error_message": None,
            "failure_point": None,
            "affected_code_path": None,
            "confidence": 0.2
        }

    text = raw_text.strip()

    # 1. Check for Python Traceback
    py_frames = PYTHON_TRACEBACK_REGEX.findall(text)
    python_exc_match = PYTHON_EXCEPTION_REGEX.findall(text)
    if py_frames or "Traceback (most recent call last):" in text:
        exc_type = python_exc_match[-1][0] if python_exc_match else "PythonRuntimeError"
        msg = python_exc_match[-1][1] if python_exc_match else ""
        failure_point = None
        code_path = []
        if py_frames:
            # Last frame in python is root failure
            file_path, line, func = py_frames[-1]
            short_file = file_path.replace('\\', '/').split('/')[-1]
            failure_point = f"{short_file}:{line}"
            for f, l, fn in py_frames[-4:]:
                sf = f.replace('\\', '/').split('/')[-1]
                code_path.append(f"{sf}:{fn}")

        return {
            "status": "Success",
            "exception_type": exc_type,
            "error_message": msg.strip() or f"{exc_type} encountered",
            "failure_point": failure_point or "Unknown line",
            "affected_code_path": " -> ".join(code_path) if code_path else None,
            "confidence": 0.92 if failure_point else 0.80
        }

    # 2. Check for Java Stack Trace
    java_frames = JAVA_FRAME_REGEX.findall(text)
    java_exc_match = JAVA_EXCEPTION_REGEX.search(text)
    if java_frames or "Exception in thread" in text or "java." in text:
        exc_type = "JavaException"
        msg = ""
        if java_exc_match:
            full_exc = java_exc_match.group(1).strip()
            exc_type = full_exc.split('.')[-1]
            msg = (java_exc_match.group(2) or "").strip()
        
        failure_point = None
        code_path = []
        if java_frames:
            # Top frame is failure point
            cls, meth, file_name, line = java_frames[0]
            failure_point = f"{file_name}:{line}" if line else file_name
            for cls, meth, f, l in java_frames[:4]:
                short_cls = cls.split('.')[-1]
                code_path.append(f"{short_cls}.{meth}")
        
        return {
            "status": "Success",
            "exception_type": exc_type,
            "error_message": msg or f"{exc_type} thrown",
            "failure_point": failure_point or "Unknown frame",
            "affected_code_path": " -> ".join(code_path) if code_path else None,
            "confidence": 0.94 if failure_point else 0.82
        }

    # 3. Check for C++ / Native Crash
    cpp_match = CPP_CRASH_REGEX.search(text)
    if cpp_match:
        func = cpp_match.group(1).strip()
        f_name = cpp_match.group(2)
        line = cpp_match.group(3)
        failure_point = f"{f_name}:{line}" if (f_name and line) else func
        return {
            "status": "Success",
            "exception_type": "NativeCrashException",
            "error_message": f"Crash in {func}",
            "failure_point": failure_point,
            "affected_code_path": func,
            "confidence": 0.88
        }

    # 4. Check for JavaScript / Node.js
    js_match = JS_ERROR_REGEX.search(text)
    js_frames = JS_FRAME_REGEX.findall(text)
    if js_match or js_frames:
        exc_type = js_match.group(1) if js_match else "JavaScriptError"
        msg = js_match.group(2) if js_match else ""
        failure_point = None
        code_path = []
        if js_frames:
            fn, path, line, col = js_frames[0]
            short_p = path.replace('\\', '/').split('/')[-1]
            failure_point = f"{short_p}:{line}"
            for fn, path, line, col in js_frames[:3]:
                sp = path.replace('\\', '/').split('/')[-1]
                code_path.append(f"{fn or 'anonymous'} ({sp}:{line})")
        return {
            "status": "Success",
            "exception_type": exc_type,
            "error_message": msg.strip() or f"{exc_type} occurred",
            "failure_point": failure_point or "Unknown JS location",
            "affected_code_path": " -> ".join(code_path) if code_path else None,
            "confidence": 0.90 if failure_point else 0.78
        }

    # 5. Fallback for generic error messages
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_line = lines[0] if lines else "Error"
    return {
        "status": "Success",
        "exception_type": "GenericErrorException",
        "error_message": first_line[:200],
        "failure_point": "Log entry root",
        "affected_code_path": None,
        "confidence": 0.65
    }

def parse_uploaded_log_file(content: str, filename: str) -> Dict[str, Optional[str]]:
    """
    Parses uploaded text/log content to separate title, description,
    stack traces, and error logs automatically.
    """
    lines = content.strip().split('\n')
    title = f"Bug report from {filename}"
    description = ""
    stack_trace = ""
    error_logs = ""

    # Check if file has header or first non-empty line can serve as title
    for line in lines:
        cleaned = line.strip()
        if cleaned and not cleaned.startswith('#') and not cleaned.startswith('//'):
            if len(cleaned) < 150:
                title = cleaned
            break

    # Look for stack trace blocks
    is_stack = False
    stack_lines = []
    log_lines = []

    for line in lines:
        if (
            "at " in line
            or "Traceback" in line
            or "File \"" in line
            or "Exception in" in line
            or "Crash [@" in line
        ):
            is_stack = True

        if is_stack:
            stack_lines.append(line)
        else:
            log_lines.append(line)

    if stack_lines:
        stack_trace = "\n".join(stack_lines).strip()
    if log_lines:
        error_logs = "\n".join(log_lines).strip()

    description = f"Imported from {filename}. Total lines: {len(lines)}."
    if log_lines and len(log_lines) > 0:
        description += "\nInitial logs:\n" + "\n".join(log_lines[:5])

    return {
        "title": title[:250],
        "description": description,
        "stack_trace": stack_trace or None,
        "error_logs": error_logs or None
    }
