import asyncio
import httpx
from typing import Literal, Protocol, List, Dict, Any, Optional
from pydantic import ValidationError

from fastapi_cache.decorator import cache


from app.models.movie import Movie
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailable

from app.models.movie import Movie, MovieType
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailable


# new protocol

class MovieSearchService(Protocol):
    """
    Defines the contract for any movie search service.
    Any class implementing this protocol must have a search method
    with this exact signature.
    """
    async def search(self, query: str) -> List[Movie]:
        """Searches for movies based on a query string."""
        ...


# poster needs to be built not provided well by the api
# title  : check or  (original_title )
# year : release date
# imdb_id : ....
# type : .....



# implementations

class OMDBService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    async def search(self, query: str, movie_type: Optional[MovieType] = None) -> List[Movie]:
        headers = {"User-Agent": "MovieSearchApp/1.0"}
        params = {"s": query, "apikey": self.api_key}
        if movie_type:
            params["type"] = movie_type.value

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("Response") == "True":
                    movies_data = data.get("Search", [])
                    validated_movies = []
                    for movie_data in movies_data:
                        try:
                            movie_data['source_api'] = 'OMDB'
                            # empty lists for new fields to match => model
                            movie_data['genres'] = []
                            movie_data['actors'] = []
                            validated_movies.append(Movie(**movie_data))
                        except ValidationError as e:
                            print(f"OMDB validation error for {movie_data.get('Title')}: {e}")
                    return validated_movies
                else:
                    return []
            except httpx.HTTPStatusError as e:
                raise ServiceUnavailable(
                    service_name="OMDB",
                    status_code=e.response.status_code,
                    detail=str(e)
                )
            except Exception as e:
                raise ServiceUnavailable(
                    service_name="OMDB",
                    status_code=500,
                    detail=str(e)
                )


class TMDBService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    @cache(expire=86400) #  24 hrs
    async def _get_details(self, client: httpx.AsyncClient, item_id: int, search_type: Literal["movie", "tv"]) -> Dict:
        """Fetches full details including genres and actors for a single item."""
        # print(f"Fetching details for {search_type} ID: {item_id} ")

        details_url = f"{self.base_url}/{search_type}/{item_id}"
        credits_url = f"{self.base_url}/{search_type}/{item_id}/credits"
        params = {"api_key": self.api_key}

        details_task = client.get(details_url, params=params)
        credits_task = client.get(credits_url, params=params)
        
        details_response, credits_response = await asyncio.gather(details_task, credits_task)

        details_response.raise_for_status()
        credits_response.raise_for_status()

        details_data = details_response.json()
        credits_data = credits_response.json()

        genres = [genre['name'] for genre in details_data.get('genres', [])]
        actors = [actor['name'] for actor in credits_data.get('cast', [])[:5]] # Top 5 actors

        return {"genres": genres, "actors": actors}

    
    async def _search_single_type(self, client: httpx.AsyncClient, query: str, search_type: Literal["movie", "tv"]) -> List[Movie]:
        """Searches for a single content type and enriches results with details."""
        endpoint = f"/search/{search_type}"
        search_url = f"{self.base_url}{endpoint}"
        params = {"api_key": self.api_key, "query": query}
        headers = {"User-Agent": "MovieSearchApp/1.0"}

        response = await client.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        search_results = response.json().get("results", [])

        if not search_results:
            return []

        # Fetch details for all search results concurrently     N+1 => cached
        details_tasks = [self._get_details(client, item['id'], search_type) for item in search_results]
        details_list = await asyncio.gather(*details_tasks)

        validated_movies = []
        for i, item_data in enumerate(search_results):
            try:
                is_series = search_type == "tv"
                item_details = details_list[i]

                mapped_data = {
                    "imdb_id": f"tmdb_{item_data.get('id')}",
                    "title": item_data.get("name" if is_series else "title"),
                    "year": (item_data.get("first_air_date" if is_series else "release_date", "N/A") or "N/A").split('-')[0],
                    "type": "series" if is_series else "movie",
                    "poster": f"https://image.tmdb.org/t/p/w500{item_data.get('poster_path')}" if item_data.get('poster_path') else None,
                    "source_api": "TMDB",
                    "genres": item_details.get("genres"),
                    "actors": item_details.get("actors")
                }
                validated_movies.append(Movie(**mapped_data))
            except ValidationError as e:
                print(f"TMDB validation error for {item_data.get('title') or item_data.get('name')}: {e}")
        return validated_movies

    # Main search function
    async def search(self, query: str, movie_type: Optional[MovieType] = None) -> List[Movie]:
        async with httpx.AsyncClient() as client:
            tasks = []
            try:
                if movie_type == MovieType.MOVIE:
                    tasks.append(self._search_single_type(client, query, "movie"))
                elif movie_type == MovieType.SERIES:
                    tasks.append(self._search_single_type(client, query, "tv"))
                else:
                    tasks.append(self._search_single_type(client, query, "movie"))
                    tasks.append(self._search_single_type(client, query, "tv"))

                results_from_tasks: List[List[Movie]] = await asyncio.gather(*tasks)
                
                all_results = [movie for sublist in results_from_tasks for movie in sublist]
                return all_results
                
            except httpx.HTTPStatusError as e:
                raise ServiceUnavailable(
                    service_name="TMDB",
                    status_code=e.response.status_code,
                    detail=str(e)
                )
            except Exception as e:
                raise ServiceUnavailable(
                    service_name="TMDB",
                    status_code=500,
                    detail=str(e)
                )



#DIP 
# Dependency inj providers

def get_omdb_service() -> OMDBService:
    settings = get_settings()
    return OMDBService(api_key=settings.OMDB_API_KEY)

def get_tmdb_service() -> TMDBService:
    settings = get_settings()
    return TMDBService(api_key=settings.TMDB_API_KEY)
