from typing import Optional

from data_provider.base_data_provider import IDataProvider
from data_provider.tinkoff_downloaded.tinkoff_downloaded import TinkoffDownloaded
from data_provider.tinkoff_historic.tinkoff_historic import TinkoffHistoric

__all__ = ("DataProviderFactory")


class DataProviderFactory:
    """
    Fabric for data providers. Put here a new provider.
    """
    @staticmethod
    def new_factory(provider_name: str, *args, **kwargs) -> Optional[IDataProvider]:
        match provider_name:
            case "TinkoffHistoric":
                return TinkoffHistoric(*args, **kwargs)
            case "TinkoffDownloaded":
                return TinkoffDownloaded(*args, **kwargs)
            case _:
                return None
