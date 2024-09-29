from pydantic import BaseModel, Field
from typing import Optional

class SecurityProperties(BaseModel):
    auth_type: str = Field(..., alias='authType')
    auth_user: Optional[str] = Field(None, alias='authUser')
    auth_password: Optional[str] = Field(None, alias='authPassword')
    auth_admin_user: Optional[str] = Field(None, alias='authAdminUser')
    auth_admin_password: Optional[str] = Field(None, alias='authAdminPassword')
    oauth2_user_role: Optional[str] = Field(None, alias='oauth2UserRole')
    oauth2_admin_role: Optional[str] = Field(None, alias='oauth2AdminRole')

    class Config:
        alias_generator = lambda s: s.replace('_', '')

    @property
    def auth_type_enum(self):
        return AuthTypes[self.auth_type.upper()]

    @property
    def oauth2_user_role_upper(self):
        return self.oauth2_user_role.upper() if self.oauth2_user_role else None

    @property
    def oauth2_admin_role_upper(self):
        return self.oauth2_admin_role.upper() if self.oauth2_admin_role else None

class AuthTypes(str):
    NONE = "NONE"
    BASIC = "BASIC"
    OAUTH = "OAUTH"

class AccessType(str):
    ADMIN_ONLY = "ADMIN_ONLY"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
