from __future__ import annotations

from enum import Enum
import os
from typing import (
    Any,
    Dict,
    Tuple,
    Type,
)

from boto3 import client
from botocore.exceptions import ClientError
from dotenv import (
    dotenv_values,
    load_dotenv,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
)


class Environment(str, Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prd"


class SecretSource(PydanticBaseSettingsSource):
    def aws_secrets_manager(self):
        try:
            env = {
                **dotenv_values(".env"),
                **os.environ,
            }

            environment = env.get("ENVIRONMENT")
            aws_access_key_id = None
            aws_secret_access_key = None
            aws_region = None

            if environment == Environment.DEV:
                aws_access_key_id = env.get("AWS_ACCESS_KEY_ID")
                aws_secret_access_key = env.get("AWS_SECRET_ACCESS_KEY")
                aws_region = env.get("AWS_REGION")
                aws_endpoint_url = env.get("AWS_ENDPOINT_URL")

                return client(
                    "secretsmanager",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=aws_region,
                    endpoint_url=aws_endpoint_url,
                )

            if environment == Environment.PROD:
                aws_access_key_id = env.get("AWS_ACCESS_KEY_ID_SM_AUTHENTICATION")
                aws_secret_access_key = env.get(
                    "AWS_SECRET_ACCESS_KEY_SM_AUTHENTICATION"
                )
                aws_region = env.get("AWS_REGION")
                return client(
                    "secretsmanager",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=aws_region,
                )

        except ClientError as e:
            raise e

    def get_field_value(
        self,
        field: FieldInfo,
        field_name: str,
    ):
        """buscas o valor do campo no aws secrets manager"""
        try:
            if field_name:
                secret = self.aws_secrets_manager()
                value = secret.get_secret_value(SecretId=field_name)
                return value["SecretString"]

        except ClientError as e:
            error = e.response["Error"]["Code"]
            if error in [
                "ResourceNotFoundException",
                "InvalidRequestException",
                "InvalidParameterException",
                "DecryptionFailure",
                "InternalServiceError",
                "AccessDeniedException",
            ]:
                return field.default

        return field.default

    def __call__(self) -> Dict[str, Any]:
        data = {}

        for field_name, field in self.settings_cls.model_fields.items():
            data[field_name] = self.get_field_value(field, field_name)

        return data


class SecretsManagerSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (SecretSource(settings_cls),)


class SecretsManager(SecretsManagerSettings):
    environment: Environment = Environment.TEST
    app_bucket_name: str = Field(default="judicial-service-events")
    aws_access_key_id: str = Field(default="test")
    aws_secret_access_key: str = Field(default="test")
    aws_endpoint_local_url: str = Field(
        default="http://localstack:4566" if environment == "dev" else "http://localhost:4566"
    )
    aws_region: str = Field(default="us-east-1")
    openai_token: str = Field(default="test")




class AppConfig(BaseSettings):
    environment: Environment = Environment.DEV
    description: str = Field("Service Events")
    app_debug: bool = Field(True)
    app_name: str = Field("judicial-service-events")
    app_host: str = Field("0.0.0.0")
    app_port: int = Field(8080)
    log_level: str = Field("DEBUG")
    open_ai_api_key: str = Field("")
    app_bucket_name: str = Field("")
    aws_access_key_id: str = Field("")
    aws_secret_access_key: str = Field("")
    aws_region: str = Field(default="us-east-1")
    aws_endpoint_local_url: str = Field(default="http://localhost:4566")

    model_config = ConfigDict(arbitrary_types_allowed=True)


load_dotenv(verbose=True)

settings = AppConfig()
secrets = SecretsManager()
