# Planwise: AI Course Planner

Capstone project (Fall 2024). A chat assistant that helps students plan their degree. It uses an LLM with function calling to search the course catalog and verify prerequisites instaed of hallucinating them.

## Architecture

```
web/index.html  ->  FastAPI /api/chat  ->  agent loop (OpenAI tools)
                                         ├─ search_courses
                                         ├─ get_course
                                         ├─ check_prereqs
                                         └─ check_term_plan -> courses.json
```

## Run

```
pip install -r requirements.txt
export OPENAI_API_KEY=...
uvicorn planner.api:app --reload
```

## Tests

`pytest`
