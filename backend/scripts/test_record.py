import os
from pathlib import Path

# Ensure the data directory exists
Path("data/experience").mkdir(parents=True, exist_ok=True)

from app.model_lab.experience import ExperienceRecorder
from app.model_lab.experience.store import ExperienceStore
from app.model_lab.runtime import record_request

# 1. Initialize store & recorder
store = ExperienceStore("./data/experience/runtime.jsonl")
recorder = ExperienceRecorder(store)

# 2. Simulate a user message and a model response
user_message = "Hello EVU, how are you?"
dummy_response = "I am EVU, your AI assistant. Everything is working correctly!"

# 3. Record the session
with record_request(
    recorder,
    prompt=user_message,
    model="evu",
    provider="evu",
    task_type="general",
) as session:
    session.model_response(dummy_response)
    experience = session.finish(success=True)

print("Session recorded successfully!")