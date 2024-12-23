# app/cache.py
import shelve

class Cache:
    def __init__(self, cache_file="cache.db"):
        self.cache_file = cache_file

    def get(self, key):
        """Retrieve a value from the cache."""
        with shelve.open(self.cache_file) as cache:
            return cache.get(key)

    def set(self, key, value):
        """Store a value in the cache."""
        with shelve.open(self.cache_file) as cache:
            cache[key] = value

    def clear(self):
        """Clear all cached values."""
        with shelve.open(self.cache_file) as cache:
            cache.clear()

    def get_browser_cookies(self, domain):
        """
        Retrieve browser cookies for a specific domain.

        Args:
            domain (str): The domain for which to retrieve cookies.

        Returns:
            The cookies for the specified domain, or None if not found.
        """
        # Open the shelve cache file
        with shelve.open(self.cache_file) as cache:
            # Retrieve and return cookies for the given domain
            return cache.get(f"cookies:{domain}")

    def set_browser_cookies(self, domain, cookies):
        """Store browser cookies for a specific domain.

        Args:
            domain (str): The domain for which to store the cookies.
            cookies (str): The cookies to store as a string.
        """
        with shelve.open(self.cache_file) as cache:
            cache[f"cookies:{domain}"] = cookies
