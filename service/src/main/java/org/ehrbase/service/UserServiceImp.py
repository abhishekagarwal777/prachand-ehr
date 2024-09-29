import uuid
import logging
from typing import Optional
from flask import current_app
from EHR.cache import CacheProvider  # Update with the correct import
from EHR.exceptions import InternalServerException  # Update with the correct import
from EHR.repository import PartyProxyRepository  # Update with the correct import
from EHR.security import IAuthenticationFacade  # Update with the correct import

class UserService:
    def get_current_user_id(self) -> uuid.UUID:
        """Retrieve the ID of the currently authenticated user."""
        pass

class UserServiceImp(UserService):
    def __init__(self, authentication_facade: IAuthenticationFacade, 
                 cache_provider: CacheProvider, 
                 party_proxy_repository: PartyProxyRepository):
        self.authentication_facade = authentication_facade
        self.cache_provider = cache_provider
        self.party_proxy_repository = party_proxy_repository
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_current_user_id(self) -> uuid.UUID:
        key = self.authentication_facade.get_authentication().name
        return self.cache_provider.get(CacheProvider.USER_ID_CACHE, key, 
                                       lambda: self.get_or_create_current_user_id_sync(key))

    def get_or_create_current_user_id_sync(self, key: str) -> uuid.UUID:
        internal_user_id = self.party_proxy_repository.find_internal_user_id(key)
        if internal_user_id:
            return internal_user_id

        try:
            return self.party_proxy_repository.create_internal_user(key)
        except Exception as ex:  # Catch specific exceptions as necessary
            if isinstance(ex, DataIntegrityViolationException):
                self.logger.info(str(ex))
                return self.party_proxy_repository.find_internal_user_id(key)

        raise InternalServerException("Cannot create User")
