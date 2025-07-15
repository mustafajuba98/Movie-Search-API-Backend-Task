import asyncio
from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi_cache.decorator import cache
from typing import List, Optional, Dict
from app.models.movie import Movie, MovieSearchResult, MovieType
from app.services.movie_service import OMDBService, TMDBService, get_omdb_service, get_tmdb_service

router = APIRouter()

@router.get("/search", response_model=MovieSearchResult)
@cache(expire=3600)
async def search_movies(
    #َ Queries
    title: Optional[str] = Query(None, min_length=2, description="Movie title to search for."),
    type: Optional[MovieType] = Query(None, description="Filter by type (movie or series)."),
    actor: Optional[str] = Query(None, description="Filter by actor name (case-insensitive)."),
    genre: Optional[str] = Query(None, description="Filter by genre (case-insensitive)."),

    # DIP (Depends)
    omdb_service: OMDBService = Depends(get_omdb_service),
    tmdb_service: TMDBService = Depends(get_tmdb_service)
):
    # this , this or that 
    if not title and not actor and not genre:
        raise HTTPException(status_code=400, detail="At least one of 'title', 'actor', or 'genre' must be provided.")
    
    #  broad search if only actor/genre is provided
    search_query = title if title else (actor or genre or "a")

    omdb_task = omdb_service.search(search_query, movie_type=type)
    tmdb_task = tmdb_service.search(search_query, movie_type=type)
    results = await asyncio.gather(omdb_task, tmdb_task)
    
    all_movies: Dict[str, Movie] = {movie.imdb_id: movie for sublist in results for movie in sublist if movie.imdb_id not in (all_movies := {})}
    final_results = list(all_movies.values())

    if genre:
        final_results = [m for m in final_results if m.genres and any(g.lower() == genre.lower() for g in m.genres)]
    if actor:
        final_results = [m for m in final_results if m.actors and any(a.lower() == actor.lower() for a in m.actors)]

    return MovieSearchResult(search_results=final_results, total_results=len(final_results), response=True)