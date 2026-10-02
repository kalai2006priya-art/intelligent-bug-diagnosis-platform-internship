"""
Benchmark Ground-Truth Corpus for Milestone 4.3 System Validation
Contains diverse defect test cases spanning:
- Programming Languages: Java, Python, C++, JavaScript/Node.js, Go/SQL
- Exception Types: NullPointerException, ZeroDivisionError, TypeError, SocketTimeoutException, Crash [@ ...], OutOfMemoryError, KeyError
- Severities: Critical, High, Medium, Low
- Information Profiles: Complete, Partial, Sparse / Insufficient Evidence
- Duplicate Pairs: Known duplicates, related issues, unrelated issues
"""

BENCHMARK_CASES = [
    {
        "id": "TC-JAVA-01",
        "language": "Java",
        "title": "NullPointerException during OAuth token refresh in AuthService",
        "description": "When an access token expires during active session keep-alive, AuthService.refreshToken throws a NullPointerException because the user token store reference is null.",
        "component": "Authentication & Authorization",
        "environment": "Production Linux JDK 17",
        "stack_trace": """java.lang.NullPointerException: Cannot invoke "TokenStore.getRefreshToken()" because "this.tokenStore" is null
    at com.platform.auth.AuthService.refreshToken(AuthService.java:55)
    at com.platform.auth.AuthController.handleKeepAlive(AuthController.java:120)
    at org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:1072)""",
        "error_logs": "2026-09-29 10:14:02.112 [ERROR] [auth-thread-4] com.platform.auth.AuthService - Failed to process token refresh: NullPointerException at AuthService.java:55",
        "expected_severity": "High",
        "expected_priority": "High",
        "expected_component": "Authentication & Authorization",
        "expected_exception": "NullPointerException",
        "expected_failure_point": "AuthService.java:55",
        "expected_root_cause_keyword": "null",
        "info_level": "Complete"
    },
    {
        "id": "TC-PY-02",
        "language": "Python",
        "title": "ZeroDivisionError in metrics calculation worker",
        "description": "The analytics computation pipeline encounters an unhandled ZeroDivisionError when processing an empty dataset where total_events count is zero.",
        "component": "General / Core Subsystem",
        "environment": "Ubuntu 22.04 Python 3.10",
        "stack_trace": """Traceback (most recent call last):
  File "/opt/platform/workers/analytics_worker.py", line 108, in calculate_conversion_rate
    rate = successful_events / total_events
ZeroDivisionError: division by zero""",
        "error_logs": "ERROR:workers.analytics_worker:Job #4491 failed with ZeroDivisionError at /opt/platform/workers/analytics_worker.py:108",
        "expected_severity": "Medium",
        "expected_priority": "Medium",
        "expected_component": "General / Core Subsystem",
        "expected_exception": "ZeroDivisionError",
        "expected_failure_point": "analytics_worker.py:108",
        "expected_root_cause_keyword": "division",
        "info_level": "Complete"
    },
    {
        "id": "TC-CPP-03",
        "language": "C++",
        "title": "Fatal crash in HTTP network request callback when cancelled",
        "description": "Browser crashes when a large file download stream is abruptly cancelled by the client. nsHttpChannel dereferences mListener without checking if it has been cleared.",
        "component": "Networking & API",
        "environment": "Windows 11 x64",
        "stack_trace": """Crash [@ nsHttpChannel::OnStopRequest(nsIRequest*, nsISupports*, tag_nsresult)]
0 xul.dll!nsHttpChannel::OnStopRequest [nsHttpChannel.cpp:6840]
1 xul.dll!nsInputStreamPump::OnStateStop [nsInputStreamPump.cpp:650]
2 xul.dll!nsThread::ProcessNextEvent [nsThread.cpp:890]""",
        "error_logs": "[FATAL] Process terminated due to access violation in xul.dll at nsHttpChannel.cpp:6840",
        "expected_severity": "Critical",
        "expected_priority": "Critical",
        "expected_component": "Networking & API",
        "expected_exception": "NativeCrashException",
        "expected_failure_point": "nsHttpChannel.cpp:6840",
        "expected_root_cause_keyword": "null",
        "info_level": "Complete"
    },
    {
        "id": "TC-JS-04",
        "language": "JavaScript",
        "title": "TypeError cannot read properties of undefined in user table render",
        "description": "The UI fails to render table content when navigating to the member directory before user profile data finishes asynchronous fetching.",
        "component": "UI & Frontend Rendering",
        "environment": "Node.js v20 / Chrome 128",
        "stack_trace": """TypeError: Cannot read properties of undefined (reading 'map')
    at renderTable (/app/src/components/UserTable.js:42:18)
    at renderWithHooks (/app/node_modules/react-dom/cjs/react-dom.development.js:14985:18)
    at updateFunctionComponent (/app/node_modules/react-dom/cjs/react-dom.development.js:17356:20)""",
        "error_logs": "[Uncaught TypeError] UserTable.js:42 - Cannot read properties of undefined (reading 'map')",
        "expected_severity": "Medium",
        "expected_priority": "Medium",
        "expected_component": "UI & Frontend Rendering",
        "expected_exception": "TypeError",
        "expected_failure_point": "UserTable.js:42",
        "expected_root_cause_keyword": "undefined",
        "info_level": "Complete"
    },
    {
        "id": "TC-DB-05",
        "language": "SQL / Java",
        "title": "Database connection pool exhaustion deadlock under concurrent load",
        "description": "High concurrent transactions cause the connection pool to become exhausted, leading to timeouts and thread deadlocks across all worker pools.",
        "component": "Database / Persistence",
        "environment": "Docker Postgres 16",
        "stack_trace": """java.sql.SQLException: Connection pool exhausted after timeout of 30000ms
    at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:182)
    at com.platform.dao.OrderRepository.findPending(OrderRepository.java:47)""",
        "error_logs": "[ERROR] [HikariPool-1] Connection is not available, request timed out after 30000ms (total=50, active=50, idle=0, waiting=12)",
        "expected_severity": "High",
        "expected_priority": "High",
        "expected_component": "Database / Persistence",
        "expected_exception": "SQLException",
        "expected_failure_point": "HikariPool.java:182",
        "expected_root_cause_keyword": "connection",
        "info_level": "Complete"
    },
    {
        "id": "TC-MEM-06",
        "language": "Java",
        "title": "Catastrophic OutOfMemoryError in batch report generator",
        "description": "Generating large monthly analytical PDF reports exhausts the JVM heap memory, causing complete application crash and unhandled process termination.",
        "component": "Memory & Runtime Resources",
        "environment": "Production AWS ECS",
        "stack_trace": """java.lang.OutOfMemoryError: Java heap space
    at java.base/java.util.Arrays.copyOf(Arrays.java:3537)
    at java.base/java.io.ByteArrayOutputStream.grow(ByteArrayOutputStream.java:115)
    at com.platform.report.PDFGenerator.renderLargeReport(PDFGenerator.java:214)""",
        "error_logs": "FATAL: System crash - java.lang.OutOfMemoryError: Java heap space at PDFGenerator.java:214",
        "expected_severity": "Critical",
        "expected_priority": "Critical",
        "expected_component": "Memory & Runtime Resources",
        "expected_exception": "OutOfMemoryError",
        "expected_failure_point": "PDFGenerator.java:214",
        "expected_root_cause_keyword": "memory",
        "info_level": "Complete"
    },
    {
        "id": "TC-PARTIAL-07",
        "language": "Java",
        "title": "Payment gateway socket timeout on checkout confirmation",
        "description": "Customers experience timeout errors during credit card processing when communicating with third-party payment gateway.",
        "component": "Networking & API",
        "environment": "Staging",
        "stack_trace": None,
        "error_logs": "2026-09-29 11:22:01 [WARN] SocketTimeoutException: Read timed out connecting to api.paymentgateway.com:443 after 15000ms",
        "expected_severity": "High",
        "expected_priority": "High",
        "expected_component": "Networking & API",
        "expected_exception": "SocketTimeoutException",
        "expected_failure_point": None,
        "expected_root_cause_keyword": "timeout",
        "info_level": "Partial"
    },
    {
        "id": "TC-SPARSE-08",
        "language": "General",
        "title": "Something wrong",
        "description": "App failed.",
        "component": None,
        "environment": None,
        "stack_trace": None,
        "error_logs": None,
        "expected_severity": "Low",
        "expected_priority": "Low",
        "expected_component": "Unspecified",
        "expected_exception": None,
        "expected_failure_point": None,
        "expected_root_cause_keyword": None,
        "info_level": "Sparse"
    }
]

# Duplicate Detection Evaluation Pairs
DUPLICATE_EVAL_PAIRS = [
    {
        "pair_id": "DUP-PAIR-01",
        "type": "Likely Duplicate",
        "base_bug": {
            "title": "Null pointer crash in HTTP network request callback when cancelled",
            "description": "Firefox crashes when a large download is cancelled before stream completes. nsHttpChannel fails to check if mListener is null."
        },
        "query_bug": {
            "title": "Null pointer crash in HTTP network request callback when cancelled",
            "description": "Firefox crashes when a download is aborted by user. nsHttpChannel mListener is null before calling OnStopRequest."
        },
        "expected_status": "Likely Duplicate",
        "min_similarity": 0.85
    },
    {
        "pair_id": "REL-PAIR-02",
        "type": "Related Issue",
        "base_bug": {
            "title": "Connection pool timeout when acquiring database connection",
            "description": "HikariCP pool becomes exhausted under 50 concurrent transactions leading to acquire timeout."
        },
        "query_bug": {
            "title": "Database transaction rollback aborts due to pool lease exhaustion",
            "description": "During heavy concurrent queries, database lease acquire times out waiting for pool."
        },
        "expected_status": "Related Issue",
        "min_similarity": 0.65
    },
    {
        "pair_id": "UNREL-PAIR-03",
        "type": "New / Unmatched",
        "base_bug": {
            "title": "Null pointer crash in HTTP network request callback when cancelled",
            "description": "nsHttpChannel crashes on stream cancellation."
        },
        "query_bug": {
            "title": "Button padding alignment glitch in dark mode theme navigation bar",
            "description": "In dark mode the CSS padding on the header navbar is misaligned by 2px on Safari browser."
        },
        "expected_status": "New / Unmatched",
        "max_similarity": 0.55
    }
]



