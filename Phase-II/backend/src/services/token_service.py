"""
Token service for managing JWT tokens including blacklisting functionality.
"""
from datetime import datetime, timedelta
from typing import Optional
import redis
from src.config.settings import settings


class TokenService:
    """
    Service class for managing JWT tokens, including blacklisting functionality.
    """

    def __init__(self):
        """
        Initialize the token service with Redis connection for token blacklisting.
        """
        if settings.REDIS_URL:
            self.redis_client = redis.from_url(settings.REDIS_URL)
        else:
            # For development without Redis, we'll use an in-memory approach
            self.redis_client = None
            self._blacklisted_tokens = set()

    def blacklist_token(self, token: str, expiration: Optional[timedelta] = None) -> bool:
        """
        Blacklist a token to prevent further use.

        Args:
            token: JWT token to blacklist
            expiration: Optional expiration time for the blacklisted token

        Returns:
            bool: True if token was successfully blacklisted
        """
        try:
            if self.redis_client:
                # Use the token's expiration time if not provided
                if not expiration:
                    # Default to 24 hours if we can't determine the token's expiration
                    expiration = timedelta(hours=24)

                # Store the token in Redis with an expiration
                self.redis_client.setex(
                    f"blacklisted_token:{token}",
                    expiration,
                    "true"
                )
            else:
                # In-memory storage for development
                if not expiration:
                    expiration = timedelta(hours=24)

                # For in-memory, we'll just store the token temporarily
                # In a real implementation, you'd want to handle cleanup
                self._blacklisted_tokens.add(token)

            return True
        except Exception:
            return False

    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: JWT token to check

        Returns:
            bool: True if token is blacklisted
        """
        try:
            if self.redis_client:
                # Check if the token exists in Redis
                return self.redis_client.exists(f"blacklisted_token:{token}") > 0
            else:
                # Check in-memory storage
                return token in self._blacklisted_tokens
        except Exception:
            # If there's an error checking, assume it's not blacklisted
            return False

    def blacklist_user_tokens(self, user_id: str, expiration: Optional[timedelta] = None) -> bool:
        """
        Blacklist all tokens associated with a user (for logout all devices scenario).

        Args:
            user_id: User ID whose tokens should be blacklisted
            expiration: Optional expiration time for the blacklisted tokens

        Returns:
            bool: True if tokens were successfully blacklisted
        """
        try:
            if self.redis_client:
                # In a real implementation, you'd track tokens by user_id
                # This is a simplified approach
                self.redis_client.setex(
                    f"user_logout:{user_id}",
                    expiration or timedelta(hours=24),
                    "true"
                )
            else:
                # For in-memory, we'll just note the user logout
                pass

            return True
        except Exception:
            return False

    def is_user_logged_out(self, user_id: str) -> bool:
        """
        Check if a user has been logged out (all tokens invalidated).

        Args:
            user_id: User ID to check

        Returns:
            bool: True if user has been logged out
        """
        try:
            if self.redis_client:
                return self.redis_client.exists(f"user_logout:{user_id}") > 0
            else:
                # For in-memory approach, this would be more complex to track
                return False
        except Exception:
            return False


# Global instance of the token service
token_service = TokenService()