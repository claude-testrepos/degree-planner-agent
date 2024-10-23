import json
import os
from types import SimpleNamespace as NS

os.environ.setdefault("OPENAI_API_KEY", "test")

from planner import agent  # noqa: E402


class FakeCompletions:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=self.replies.pop(0))])


def tool_call(name, args, id="call_1"):
    return NS(id=id, function=NS(name=name, arguments=json.dumps(args)))


def test_agent_runs_tools_then_answers(monkeypatch):
    fake = FakeCompletions([
        NS(content=None, tool_calls=[tool_call("check_prereqs", {"code": "CS301", "completed": ["CS101"]})]),
        NS(content="You need CS201 and MATH220 first.", tool_calls=None),
    ])
    monkeypatch.setattr(agent, "client", NS(chat=NS(completions=fake)))

    answer, trace = agent.run([{"role": "user", "content": "can I take CS301?"}])

    assert answer == "You need CS201 and MATH220 first."
    assert trace[0]["tool"] == "check_prereqs"
    assert trace[0]["result"]["eligible"] is False
    # tool result was sent back to the model
    assert fake.calls[1]["messages"][-1]["role"] == "tool"


def test_agent_gives_up_after_max_steps(monkeypatch):
    loop = [NS(content=None, tool_calls=[tool_call("search_courses", {"query": "x"})]) for _ in range(3)]
    monkeypatch.setattr(agent, "client", NS(chat=NS(completions=FakeCompletions(loop))))
    answer, trace = agent.run([{"role": "user", "content": "hi"}], max_steps=3)
    assert "step limit" in answer
    assert len(trace) == 3
