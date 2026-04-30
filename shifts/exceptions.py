class SchedulingError(Exception):
    """Base exception for scheduling errors"""
    pass

class ValidationError(SchedulingError):
    """Raised when input validation fails"""
    pass

class OptimizationError(SchedulingError):
    """Raised when optimization fails"""
    pass

class DataAccessError(SchedulingError):
    """Raised when data access fails"""
    pass