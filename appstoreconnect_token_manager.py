import os
import jwt
from datetime import datetime, timezone, timedelta
from uuid import UUID
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from pydantic import BaseModel, constr, root_validator, validator, ValidationError
from pydantic.schema import Optional

class AppStoreConnectAPICredentials(BaseModel):
    issuer_id: Optional[UUID] = os.getenv("APPSTORE_ISSUER_ID")
    key_id: Optional[constr(  # type: ignore[valid-type]
        strip_whitespace=True, min_length=10, max_length=10
    )] = os.getenv("APPSTORE_API_KEY_ID")
    private_key: Optional[str] = os.getenv("APPSTORE_API_PRIVATE_KEY")
    password: Optional[str] = ""

    @validator("issuer_id")
    def issuer_id_not_none(cls, v):
        if not v:
            raise ValueError("APPSTORE_ISSUER_ID environment variable not set")
        return

    @validator("key_id")
    def key_id_not_none(cls, v):
        if not v:
            raise ValueError("APPSTORE_API_KEY_ID environment variable not set")
        return

    @validator("private_key")
    def private_key_not_none(cls, v):
        if not v:
            raise ValueError("APPSTORE_API_PRIVATE_KEY environment variable not set")
        return          

    @validator("password")
    def password_is_set(cls, v):
        if v:
            raise ValueError("password protected api keys not currently supported")

    class Config:
        extra = "forbid"

class AppStoreConnectTokenManager:
    TOKEN_TTL = timedelta(minutes=20)

    def __init__(self):
        try:
            self.credentials = AppStoreConnectAPICredentials()
        except ValidationError as e:
            print(e)
            return

        self.is_a_pem_private_key()

    def is_a_pem_private_key(self):
        try:
            load_pem_private_key(
                self.credentials.private_key.encode("utf-8"),
                password=None,
            )
        except Exception:
            raise ValueError("Not a valid private key")
        return


    def get_token(self):
        return jwt.encode(
            {
                "iss": self.credentials.issuer_id,
                "iat": datetime.now(tz=timezone.utc),
                "exp": datetime.now(tz=timezone.utc) + self.TOKEN_TTL,
                "aud": "appstoreconnect-v1"
                # TODO: define allowed scopes
            },
            key=self.credentials.private_key,
            algorithm="ES256",
            headers={"kid": self.credentials.key_id},
        )

