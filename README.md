# Fable Generator API

A FastAPI service that generates children's fables with illustrations using OpenAI's GPT and DALL·E APIs.

## Features

- Generates age-appropriate fables with moral lessons
- Creates matching illustrations in storybook style
- RESTful API with Swagger documentation
- Configurable number of illustrations per fable

## Prerequisites

- Python 3.9+
- OpenAI API key
- Virtual environment (recommended)

## Setup

1. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd fables
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```bash
OPENAI_API_KEY="your-api-key-here"
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API endpoint: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Usage

### Generate a Fable

**Endpoint:** `POST /generate_fable`

Example request body:
```json
{
  "world_description": "enchanted forest with sparkling fireflies and magical mushrooms",
  "main_character": "Luna the Wise Owl",
  "age": 7,
  "num_images": 2
}
```

Example response:
```json
{
  "fable_text": "Once upon a time...[generated fable text]...Moral: [moral lesson]",
  "images": [
    "https://[generated-image-url-1]",
    "https://[generated-image-url-2]"
  ]
}
```

## Running Tests

```bash
pytest tests/ -v
```

## Notes

- The API uses GPT-4o for text generation and DALL·E for illustrations
- Generated images are temporarily hosted by OpenAI and should be downloaded if permanent storage is needed
- The service is configured to generate age-appropriate content
- Each request will consume OpenAI API credits (both for text and image generation) 