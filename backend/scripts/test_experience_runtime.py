import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.model_lab.experience import (
    ExperienceRecorder,
    ExperienceStore,
)
from app.model_lab.runtime import (
    record_request,
    record_tool_start,
    record_tool_result,
)

store = ExperienceStore("./data/experience/runtime.jsonl")

recorder = ExperienceRecorder(store)

with record_request(
    recorder=recorder,
    prompt="Find information about Python.",
    model="evu",
    provider="evu",
    task_type="research",
) as session:

  tool_step = record_tool_start(
      "web_search",
      {"query": "Python programming language"},
  )

  record_tool_result(
      tool_step,
      {"results": ["Python is a programming language."]},
      success=True,
  )

  session.model_response("Python is a high-level programming language.")

  experience = session.finish(success=True)

print("Experience ID:")
print(experience.experience_id)

print()

print("Success:")
print(experience.success)

print()

print("Steps:")
print(len(experience.steps))

print()

print("Experience file:")
print(store.path)