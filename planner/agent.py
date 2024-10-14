import json
import os

from openai import OpenAI

from . import catalog

client = OpenAI()
MODEL = os.environ.get("PLANNER_MODEL", "gpt-4o-mini")

SYSTEM = """You are an academic advisor assistant. Help the student plan which courses to take.
Always use the tools to look up courses and verify prerequisites; never guess course codes.
When proposing a plan, list it term by term and respect which terms a course is offered in."""

TOOLS = [
    {"type": "function", "function": {
        "name": "search_courses",
        "description": "Search the course catalog by keyword",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "get_course",
        "description": "Get full details for a course code",
        "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
    {"type": "function", "function": {
        "name": "check_prereqs",
        "description": "Check whether the student can take a course given completed courses",
        "parameters": {"type": "object", "properties": {
            "code": {"type": "string"},
            "completed": {"type": "array", "items": {"type": "string"}}},
            "required": ["code", "completed"]}}},
]
IMPL = {
    "search_courses": catalog.search_courses,
    "get_course": catalog.get_course,
    "check_prereqs": catalog.check_prereqs,
}


def run(messages: list[dict], max_steps: int = 8) -> tuple[str, list[dict]]:
    """Run the tool-calling loop. Returns the final answer and a trace of tool calls."""
    messages = [{"role": "system", "content": SYSTEM}, *messages]
    trace = []
    for _ in range(max_steps):
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content, trace
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = IMPL[call.function.name](**args)
            trace.append({"tool": call.function.name, "args": args, "result": result})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return "Sorry, I couldn't finish planning within the step limit.", trace
