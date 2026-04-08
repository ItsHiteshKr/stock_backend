from model.pattern_matcher_model import PatternMatcherModel
from schema.pattern_schema import PatternMatchRequest, PatternMatchResponse
import logging

logger = logging.getLogger(__name__)


class PatternMatcherService:
    """Pattern matching business logic"""
    
    @staticmethod
    def find_pattern_match(request: PatternMatchRequest) -> PatternMatchResponse:
        """
        Find best pattern match for a stock
        
        Args:
            request: Pattern match request with symbol, years, window size
            
        Returns:
            PatternMatchResponse with match results or error
        """
        try:
            logger.info(f"Pattern match request: {request.symbol}, window={request.window_size}")
            
            # Create matcher
            matcher = PatternMatcherModel(
                symbol=request.symbol,
                years_back=request.years_back
            )
            
            # Load data
            success, message = matcher.load_data(use_cache=request.use_cache)
            
            if not success:
                logger.warning(f"Data load failed: {message}")
                return PatternMatchResponse(
                    success=False,
                    message=f"Failed to load data: {message}",
                    data=None
                )
            
            logger.info(f"Data loaded: {message}")
            
            # Find best match
            result = matcher.find_best_match(window_size=request.window_size)
            
            if result is None:
                logger.warning("No pattern match found")
                return PatternMatchResponse(
                    success=False,
                    message="No suitable pattern match found",
                    data=None
                )
            
            # Success
            score = result['best_match']['score']
            logger.info(f"Match found: score={score:.2f}%")
            
            return PatternMatchResponse(
                success=True,
                message=f"Pattern match found (Score: {score:.2f}%)",
                data=result
            )
            
        except Exception as e:
            logger.error(f"Error in pattern matching: {str(e)}", exc_info=True)
            return PatternMatchResponse(
                success=False,
                message=f"Pattern matching failed: {str(e)}",
                data=None
            )