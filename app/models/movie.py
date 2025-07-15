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
    # new filters
    genres: Optional[List[str]] = Field(None, description="List of genres for the movie.")
    actors: Optional[List[str]] = Field(None, description="List of main actors in the movie.")
    
    model_config = ConfigDict(
        # telling pydantic to use the alias names defined in the model 
        # for new objs pydantic will not take the field name (just the alias) , so we use (allow_population_by_field_name)  => :: accept the data with the field name or the alias whatever ..
        # This allows the model to accept data with field names that are not in snake_case.

        # (allow_population_by_field_name = True) it has been changed to populate_by_name 
        populate_by_name=True,
        # This is important for Pydantic v2. It tells Pydantic to validate default values.
        # pydantic only validates once , so if we change the default value of a field, it won't validate again unless we set this to True.
        # (validate_assignment = True) as they call it the permenant guardian of the model
        validate_assignment=True,
        # the example that will be shown in the /docs  (swagger) customized
        # the defualt on swagger isnt what we i want it to be shown so we customize it

        # json_schema_extra instead of (schema_extra )

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




    # type hints (Pydantic)
    # ... wanted (must) or validate err  -> ... used as a placeholder
    # description = swagger /docs
    # literal ( this , or that ) - must be one of these
    # optional - might not always be available [that]or none  (none , .....) -> none defualt
    # union -> int , str i can identify the type of the field for whatever i want and more than one type
