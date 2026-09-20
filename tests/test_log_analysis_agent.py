import pytest
from app.agents.log_analysis_agent import LogAnalysisAgent

@pytest.mark.asyncio
async def test_log_analysis_java_npe():
    agent = LogAnalysisAgent()
    trace = (
        "Exception in thread \"main\" java.lang.NullPointerException: Cannot invoke method on null object\n"
        "\tat com.example.service.LoginService.validateUser(LoginService.java:25)\n"
        "\tat com.example.controller.AuthController.handleLogin(AuthController.java:80)\n"
    )
    res = await agent.analyze(stack_trace=trace)
    assert res["status"] == "Success"
    assert res["exception_type"] == "NullPointerException"
    assert res["failure_point"] == "LoginService.java:25"
    assert "LoginService.validateUser" in res["affected_code_path"]
    assert res["confidence"] >= 0.85

@pytest.mark.asyncio
async def test_log_analysis_python_traceback():
    agent = LogAnalysisAgent()
    trace = (
        "Traceback (most recent call last):\n"
        "  File \"app/services/token.py\", line 42, in generate_token\n"
        "    secret = config['jwt_secret']\n"
        "KeyError: 'jwt_secret'\n"
    )
    res = await agent.analyze(stack_trace=trace)
    assert res["status"] == "Success"
    assert res["exception_type"] == "KeyError"
    assert res["failure_point"] == "token.py:42"
    assert res["confidence"] >= 0.80

@pytest.mark.asyncio
async def test_log_analysis_missing_logs():
    agent = LogAnalysisAgent()
    res = await agent.analyze(stack_trace=None, error_logs=None)
    assert res["status"] == "Insufficient Evidence"
    assert res["confidence"] == 0.0
    assert res["failure_point"] is None
