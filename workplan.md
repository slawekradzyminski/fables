Below is a step-by-step implementation plan that a less-capable agent can follow without guessing.
Each task ends with “✅ Done when…” acceptance criteria so you can review progress objectively.

0. Preparation

What	Instructions
Branching	Create a feature branch feat/refactor-api-v2.
CI safety net	Run pytest -q to ensure the current green baseline. Commit with tag v1.0.0-baseline.
Libraries	Upgrade to Python 3.11 (PEP 680 et al.). Replace requirements.txt with Poetry (better dependency locking).
1. Restructure the codebase (best-practice layout)
Goal: separate concerns (API layer ≠ service layer ≠ I/O)

bash
Copy
Edit
fables/
│
├── app/
│   ├── __init__.py
│   ├── core/               # generic infrastructure
│   │   ├── config.py       # Pydantic BaseSettings
│   │   └── logging.py
│   ├── prompts/            # ← new (see §2)
│   │   ├── system.txt
│   │   └── user.txt
│   ├── models/             # pure business entities (dataclasses)
│   │   ├── fable.py
│   │   └── image.py
│   ├── schemas/            # Pydantic request/response DTOs
│   │   ├── fable_request.py
│   │   └── fable_response.py
│   ├── services/           # orchestration & OpenAI calls
│   │   ├── fable_service.py
│   │   └── openai_client.py
│   └── api/                # FastAPI routers only
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── fable.py
└── tests/
✅ Done when… directory tree matches the above, imports succeed, pytest still green.

2. Extract prompts to files
Create app/prompts/system.txt

css
Copy
Edit
You are a creative story-teller specializing...
Create app/prompts/user.txt with Jinja-like placeholders:

jinja
Copy
Edit
Write a short fable for a child of age {{ age }} about:
- World Description: {{ world_description }}
- Main Character: {{ main_character }}

Then provide {{ num_images }} DALL-E prompts...
Update services/fable_service.py to:

python
Copy
Edit
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text()

system_msg = _load_prompt("system.txt")
user_template = Template(_load_prompt("user.txt"))
user_msg = user_template.render(...)
Unit tests: add tests/test_prompts.py to verify placeholders render correctly.

✅ Done when… no prompt strings remain hard-coded in Python.

3. Introduce strong typing and value objects

Area	Action
Business models	models/fable.py → @dataclass class Fable: text: str; moral: str; illustrations: list["Illustration"]
models/image.py → @dataclass class Illustration: prompt: str; url: HttpUrl.
Pydantic schemas	schemas/fable_request.py wraps former FableRequest.
schemas/fable_response.py returns: fable: str, moral: str, illustrations: list[IllustrationDTO].
Service return	fable_service.create_fable_with_images now returns a Fable domain object; API layer converts to DTO.
✅ Done when… mypy --strict passes on app/.

4. Parse and return the moral separately
In fable_service, extract the last line starting with Moral::

python
Copy
Edit
import re

moral_pattern = re.compile(r"(?im)^moral:\s*(.+)$")
moral = moral_pattern.search(fable_text).group(1).strip()
story_text = moral_pattern.sub("", fable_text).strip()
Build the Fable object with text=story_text and moral=moral.

Update unit tests to assert moral extraction.

✅ Done when… /generate_fable JSON shows separate moral.

5. Refactor API layer

Step	What
5.1	Create api/v1/fable.py with a FastAPI APIRouter containing /generate and /health.
5.2	In app/api/__init__.py, instantiate main FastAPI and include router with prefix /api/v1.
5.3	Move CORS config to core/config.py as settings.cors_allowed_origins.
5.4	Add dependency that injects OpenAI client: Depends(get_openai_client).
5.5	Enable tags metadata & contact info in app/api/__init__.py for Swagger.
✅ Done when… Swagger UI shows grouped Fables tag under /api/v1/generate.

6. OpenAPI & Swagger enhancements
Fill the FastAPI constructor:

python
Copy
Edit
app = FastAPI(
    title="Fable Generator API",
    description=open("README.md").read().split("## Features")[0].strip(),
    version=__version__,
    contact={"name": "Fable Team", "url": "https://github.com/your-org"}
)
Auto-generate schemas thanks to separated DTOs; add summary and response_description docstrings above each endpoint.

Provide example payload via Config.model_config["json_schema_extra"].

Expose customized OpenAPI JSON at /openapi.json.

✅ Done when… curl /openapi.json returns the new fields.

7. Update tests

File	Changes
tests/test_api.py	Adjust import paths; expect moral & illustrations list of dicts.
tests/test_fable.py	Assert Fable object integrity (text, moral, illustrations).
Add	tests/test_openapi.py → GET /openapi.json and validate schema with schemacheck.
Add	pytest --cov integration; fail under 90 % coverage.
✅ Done when… pytest -v passes, coverage ≥ 90 %.

8. Documentation refresh
README.md

Reflect new endpoint:
POST /api/v1/generate → returns

jsonc
Copy
Edit
{
  "fable": "...",
  "moral": "...",
  "illustrations": [
    { "prompt": "...", "url": "..." }
  ]
}
Add “How to upgrade to GPT-Image 1” section.

Remove old examples.

docs/ folder (mkdocs or Sphinx) with:

Architecture diagram (svc, router, OpenAI)

Prompt-engineering guidelines

Testing strategy & mocking cheatsheet

Changelog: create CHANGELOG.md, start with ## [1.1.0] - YYYY-MM-DD.

✅ Done when… mkdocs serve renders docs without warnings.

9. Optional polish (stretch but quick wins)

Idea	Benefit
Async OpenAI calls	non-blocking I/O under uvicorn workers.
Retry & circuit-breaker around OpenAI	graceful degradation.
Poetry scripts poetry run start and poetry run test.	
Dockerfile multi-stage build + docker compose up.	
10. Final QA & release
Bump version to 1.1.0 in pyproject.toml.

Tag release git tag v1.1.0 && git push --tags.

Merge PR after review.

Deploy to staging; run scripts/health_check.py.

If green, promote to production.

✅ Done when… health check passes, and the new Swagger contract is live.

Time-boxed checklist

Phase	Owner	Duration
1 – 2	Dev	1 day
3 – 5	Dev	0.5 day
6	Dev	0.5 day
7	QA	0.5 day
8	Tech Writer	0.5 day
9	Dev (optional)	0.5 day
Total		~3 dev-days
Execute the tasks sequentially; do not skip the unit-test updates after each structural change.