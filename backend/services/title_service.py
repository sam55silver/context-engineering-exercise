"""Title service - business logic for title operations."""

from repositories.title_repository import TitleRepository
from models.schemas import TitleResponse


class TitleService:
    """Service for title business logic."""

    @staticmethod
    def get_all_titles() -> list[TitleResponse]:
        """
        Get all titles from the catalog.

        Returns:
            List of title response models
        """
        titles = TitleRepository.get_all_titles()
        return [
            TitleResponse(
                id=title["id"],
                title=title["title"],
                kind=title["kind"],
                release_year=title["release_year"],
                genre=title["genre"],
            )
            for title in titles
        ]
