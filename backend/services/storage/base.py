import abc
from typing import BinaryIO

class StorageBackend(abc.ABC):
    """
    Abstract Base Class for file storage operations.
    """
    
    @abc.abstractmethod
    def upload(self, bucket: str, path: str, file_obj: BinaryIO) -> str:
        """Uploads a file object to the specified bucket and path. Returns the URL or path."""
        pass

    @abc.abstractmethod
    def download(self, bucket: str, path: str) -> bytes:
        """Downloads a file from the specified bucket and path."""
        pass

    @abc.abstractmethod
    def delete(self, bucket: str, path: str) -> bool:
        """Deletes a file from the specified bucket and path."""
        pass

    @abc.abstractmethod
    def exists(self, bucket: str, path: str) -> bool:
        """Checks if a file exists in the specified bucket and path."""
        pass

    @abc.abstractmethod
    def get_url(self, bucket: str, path: str) -> str:
        """Returns the public or accessible URL for the file."""
        pass
