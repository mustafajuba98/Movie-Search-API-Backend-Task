# Movie Search API

A robust and efficient RESTful API built with FastAPI to search for movies across multiple external data providers. This project demonstrates best practices in API design, including asynchronous operations, dependency injection, caching, and comprehensive error handling.

---

## Features

- **Multi-Provider Search**: Fetches and aggregates movie data from **OMDB** and **TMDB**.
- **Advanced Filtering**: Search movies by title, type (`movie`, `series`), genre, and actors.
- **High Performance**:
    - Asynchronous requests to external APIs using `httpx` and `asyncio.gather`.
    - A two-level caching strategy (endpoint and service-level) to minimize latency and reduce external API calls, effectively mitigating the N+1 problem.
- **Robust Error Handling**: Gracefully handles external service failures and invalid user input with custom exception handlers.
- **Automated Testing**: Integration tests built with `pytest` to ensure API reliability.
- **Auto-Generated Documentation**: Interactive API documentation powered by Swagger UI and ReDoc.

---

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Asynchronous HTTP Client**: [HTTPX](https://www.python-httpx.org/)
- **Caching**: [fastapi-cache2](https://github.com/long2ice/fastapi-cache) with an in-memory backend.
- **Configuration Management**: [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Testing**: [Pytest](https://pytest.org) with `pytest-asyncio`.

---

## Project Structure

The project follows a modular structure to ensure separation of concerns and maintainability:

```
├── app/
│   ├── api/          # API Endpoints and Routers
│   ├── core/         # Core logic (config, exceptions)
│   ├── models/       # Pydantic data models
│   └── services/     # Business logic (external API interaction)
├── tests/            # Pytest tests
│   └── test_endpoints.py
├── .env.example      # Example environment variables file
├── .gitignore
├── README.md
├── pytest.ini
└── requirements.txt
```

---

## Setup and Run

### 1. Prerequisites

- Python 3.10+
- An active internet connection

### 2. Get API Keys

This service requires API keys from two external providers:

- **OMDB API**:
    1. Go to [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx).
    2. Select the "FREE" plan and enter your email.
    3. You will receive an API key in your email after activation.

- **TMDB API**:
    1. Create a free account at [themoviedb.org](https://www.themoviedb.org/).
    2. Go to your account `Settings > API` section.
    3. Request a "Developer" API key and fill out the required form.
    4. You will be provided with an **API Key (v3 auth)**.

### 3. Installation

**Step 1: Clone the repository**
```bash
git clone <your-github-repo-url>
cd <repository-folder-name>
```

**Step 2: Create and activate a virtual environment**
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Set up environment variables**
Create a file named `.env` in the root directory of the project by copying the example file:
```bash
# For Windows
copy .env.example .env

# For macOS/Linux
cp .env.example .env
```
Now, open the `.env` file and replace the placeholder values with your actual API keys.
```ini
OMDB_API_KEY="YOUR_OMDB_KEY_HERE"
TMDB_API_KEY="YOUR_TMDB_KEY_HERE"
```

### 4. Running the Application

With the virtual environment activated, run the following command to start the server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 5. Running Tests

To ensure everything is working correctly, run the test suite:
```bash
pytest
```
To see print statements during test execution, use the `-s` flag:
```bash
pytest -s
```

---

## API Reference

### Accessing Interactive Documentation

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### `GET /movies/search`

Searches for movies based on the provided query parameters.

**Query Parameters:**

| Parameter | Type   | Description                                           | Required |
|-----------|--------|-------------------------------------------------------|----------|
| `title`   | string | The title of the movie to search for.                 | No       |
| `type`    | enum   | Filter by type. Accepts `movie` or `series`.          | No       |
| `actor`   | string | Filter results by actor name (case-insensitive).      | No       |
| `genre`   | string | Filter results by genre (case-insensitive).           | No       |

*Note: At least one of `title`, `actor`, or `genre` must be provided.*

**Example Request:**
```
http://127.0.0.1:8000/movies/search?title=The Dark Knight&actor=Heath Ledger&genre=Action
```

**Success Response (200 OK):**
```json
{
  "search_results": [
    {
      "title": "The Dark Knight",
      "year": "2008",
      "imdb_id": "tt0468569",
      "type": "movie",
      "source_api": "TMDB",
      "poster": "https://...",
      "genres": [
        "Action",
        "Crime",
        "Drama"
      ],
      "actors": [
        "Christian Bale",
        "Heath Ledger",
        "Aaron Eckhart",
        "Michael Caine",
        "Maggie Gyllenhaal"
      ]
    }
  ],
  "total_results": 1,
  "response": true
}
```

---

## Design Decisions

- **Modular Architecture**: The project is structured into `api`, `core`, `models`, and `services` layers to adhere to the Single Responsibility Principle. This makes the codebase easy to navigate, maintain, and test.
- **Service Layer**: A dedicated service layer abstracts the logic of interacting with external APIs. This isolates the core application from the specifics of external data sources and allows for independent, focused logic.
- **Asynchronous First**: All I/O operations (API calls) are fully asynchronous, leveraging `async/await`, `httpx`, and `asyncio.gather` to ensure the server remains non-blocking and can handle concurrent requests efficiently.
- **N+1 Problem Mitigation**: The `N+1` query problem, which arises when fetching details for a list of items, is addressed using a **two-level caching strategy**. 
    1.  **Endpoint-level caching**: Caches the final response for identical requests.
    2.  **Service-level caching**: Caches the detailed results for individual movie IDs. This is the key to performance, as subsequent searches for different titles that return a common movie will hit the cache instead of making a new API call for that movie's details.

## Known Limitations and Future Improvements

- **Filter Implementation**: Filtering by `actor` and `genre` is performed by first fetching a broader set of results based on the search query, and then filtering these results within our API. While functional and optimized with caching, this can be inefficient for very broad or generic queries (e.g., searching for an actor without a title).
- **OMDB Data**: The free tier of the OMDB API does not provide rich data like genres or actors in its search results. Therefore, these fields will be empty for results sourced solely from OMDB.
- **Future Improvements**:
    1.  **Persistent Cache**: Replace the `in-memory` cache backend with `Redis` for a persistent and scalable caching solution that survives server restarts and can be shared across multiple server instances.
    2.  **More Accurate Actor/Genre Search**: Implement a more precise search by utilizing `TMDB`'s `/search/person` endpoint to find an actor's ID first, then fetch their filmography. This would provide more accurate results than the current text-based filtering.
    3.  **Local Database Sync**: For a production-grade application, a background worker could synchronize data from external APIs into a local database (e.g., PostgreSQL). This would allow for incredibly fast and complex queries directly on our data, completely eliminating the N+1 issue at the source.

---
