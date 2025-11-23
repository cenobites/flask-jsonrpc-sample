from __future__ import annotations

from lms.domain.catalogs.repositories import ItemRepository


class ItemUniquenessService:
    def __init__(self, /, *, item_repository: ItemRepository) -> None:
        self.item_repository = item_repository

    def is_title_unique(self, title: str) -> bool:
        return not self.item_repository.exists_by_title(title)
