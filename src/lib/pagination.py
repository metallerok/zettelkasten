import abc
import sqlalchemy as sa
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from math import ceil

DEFAULT_PAGE_SIZE = 20


class PaginationABC(abc.ABC):
    def __init__(self, page: int, page_size: int):
        self.page = page
        self.page_size = page_size

    @property
    @abc.abstractmethod
    def items(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def total(self):
        raise NotImplementedError

    @property
    def total_pages(self) -> int:
        return ceil(self.total / self.page_size) or 1


class SAPagination(PaginationABC):
    def __init__(self, query, page: int, page_size: int):
        self._total = None
        self._items = None

        self._query = query
        super().__init__(page, page_size)

    @property
    def total(self) -> int:
        if not self._total:
            self._total = self._query.count()
        return self._total

    @property
    def items(self) -> List:
        if not self._items:
            if self.page > self.total_pages:
                self.page = 1

            query = self._paginate()

            self._items = query.all()

        return self._items

    def _paginate(self):
        return self._query.limit(self.page_size).offset(
            (self.page - 1) * self.page_size
        )


class AsyncSAPagination(PaginationABC):
    def __init__(self, db_session: AsyncSession, page: int, page_size: int):
        super().__init__(page, page_size)
        self._db_session = db_session
        self._items = None
        self._total = None

    async def create(self, query) -> 'AsyncSAPagination':
        self._total = await self._get_total(query)

        if self.page > self.total_pages:
            self.page = 1

        self._items = await self._paginate(query)

        return self

    @property
    def total(self) -> int:
        return self._total

    @property
    def items(self) -> List:
        return self._items

    async def _paginate(self, query):
        query = query.limit(self.page_size).offset(
            (self.page - 1) * self.page_size
        )

        result = await self._db_session.execute(query)

        items = result.scalars().unique().all()

        return items

    async def _get_total(self, query) -> int:
        query = query.with_only_columns([sa.func.count()]).order_by(None)

        result = await self._db_session.execute(query)
        total = result.scalar()

        return total
