from enum import Enum
from pydantic import BaseModel, Field, HttpUrl , ConfigDict
from typing import Literal, List, Optional

class MovieType(str, Enum):
    """Enumeration for the type of content to search for."""
    MOVIE = "movie"
    SERIES = "series"


class Movie(BaseModel):
    """
    Represents a single movie item in the search results.
    This model defines the consistent structure for movies from any provider.
    """

    title: str = Field(..., description="The title of the movie.", alias="Title")
    year: str = Field(..., description="The release year of the movie.", alias="Year")
    imdb_id: str = Field(..., description="The unique ID from IMDb.", alias="imdbID")  # imdbId -> camel case from their API  and we use snake_case here (alias)
    type: Literal['movie', 'series', 'episode', 'game'] = Field(..., description="The type of the content.", alias="Type")
    source_api: Literal['OMDB', 'TMDB'] = Field(..., description="The API source of this movie data.")
    poster: Optional[HttpUrl] = Field(None, description="URL to the movie's poster image.", alias="Poster")
    genres: Optional[List[str]] = Field(None, description="List of genres for the movie.")
    actors: Optional[List[str]] = Field(None, description="List of main actors in the movie.")
    
    model_config = ConfigDict(
        populate_by_name=True,

        validate_assignment=True,
        json_schema_extra={
            "example": {
                "title": "Inception",
                "year": "2010",
                "imdb_id": "tt1375666",
                "type": "movie",
                "poster": "https://somethingsmth.jpg",
                "source_api": "OMDB",
                "genres": ["Action", "Adventure", "Sci-Fi"],
                "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"]
            }
        }
    )

class MovieSearchResult(BaseModel):
    """
    Represents the overall search result, which can contain a list of movies.
    """
    search_results: List[Movie]
    total_results: int
    response: bool = Field(True)
