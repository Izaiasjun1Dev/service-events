from __future__ import annotations

import tempfile

from boto3 import client
from botocore.exceptions import ClientError
from judici.application.settings import secrets
from pydantic import (
    BaseModel,
    Field,
)


class RepositoryBucket(BaseModel):
    bucket: str = Field(secrets.app_bucket_name, title="Nome do bucket")

    def s3_client(self):
        try:
            if secrets.environment == "dev":
                return client(
                    service_name="s3",
                    aws_access_key_id=secrets.aws_access_key_id,
                    aws_secret_access_key=secrets.aws_secret_access_key,
                    endpoint_url=secrets.aws_endpoint_local_url,
                    region_name=secrets.aws_region,
                )
            else:
                return client(
                    service_name="s3",
                    region_name=secrets.aws_region,
                    aws_access_key_id=secrets.aws_access_key_id,
                    aws_secret_access_key=secrets.aws_secret_access_key,
                )

        except ClientError as e:
            raise e

        except Exception as e:
            raise e

    def download_file(self, key: str, local_file: str = None):
        """Realiza o download de um arquivo do bucket S3.

        Args:
            key (str): Nome do arquivo no bucket S3.
            local_file (str, optional): Caminho do arquivo local. Defaults to None.

        Raises:
            aws_error: erros retornados pelo boto3
            genaral_error: erros gerais

        Returns:
            str: Caminho do arquivo local.
        """
        try:
            s3 = self.s3_client()
            local_file = local_file or f"{tempfile.gettempdir()}/{key}"

            # faz o download do arquivo para o local_file especificado
            s3.download_file(self.bucket, key, local_file)

            return local_file

        except ClientError as aws_error:
            raise aws_error

        except Exception as general_error:
            raise general_error

    def upload_file(self, key: str, local_file: str) -> bool:
        """Realiza o upload de um arquivo para o bucket S3.

        Args:
            key (str): Nome do arquivo no bucket S3.
            local_file (str): Caminho do arquivo local.

        Raises:
            aws_error: erros retornados pelo boto3
            genaral_error: erros gerais

        Returns:
            bool: True se o upload foi realizado com sucesso
        """
        try:
            s3 = self.s3_client()
            s3.upload_file(local_file, self.bucket, key)
            return True

        except ClientError as aws_error:
            raise aws_error

        except Exception as general_error:
            raise general_error

    def list_folders(self) -> list:
        """Retorna uma lista de diretórios do bucket S3.

        Args:
            prefix (str, optional): Possibilita filtrar
            os diretórios. Defaults to None.

        Returns:
            list: Lista de diretórios.
        """

        try:
            s3 = self.s3_client()
            response = s3.list_objects_v2(Bucket=self.bucket, Delimiter="/")
            folders = [
                prefix["Prefix"].strip("/")
                for prefix in response.get("CommonPrefixes", [])
            ]
            return folders
        except ClientError as general_error:
            raise general_error

        except Exception as general_error:
            raise general_error

    def create_folder(self, folder_name: str) -> bool:
        """Cria um diretório no bucket S3.

        Args:
            folder_name (str): Nome do diretório.

        Returns:
            bool: True se o diretório foi criado com sucesso.
        """
        try:
            s3 = self.s3_client()
            s3.put_object(Bucket=self.bucket, Key=folder_name)
            return True

        except ClientError as aws_error:
            raise aws_error

        except Exception as general_error:
            raise general_error
