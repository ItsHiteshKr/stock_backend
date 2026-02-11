from fastapi import APIRouter
from utils.cache_utils import stock_cache

router = APIRouter(prefix="/cache", tags=["Cache Management"])


@router.get("/stats")
def get_cache_stats():
    """Get cache statistics"""
    return stock_cache.get_stats()


@router.post("/clear")
def clear_cache():
    """Clear entire cache (use with caution)"""
    stock_cache.clear()
    return {"message": "Cache cleared successfully"}


@router.delete("/key/{key}")
def delete_cache_key(key: str):
    """Delete specific cache key"""
    stock_cache.delete(key)
    return {"message": f"Cache key '{key}' deleted"}
