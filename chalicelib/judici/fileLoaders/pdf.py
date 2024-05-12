from __future__ import annotations

import io
import os
import tempfile

from PIL import Image
import fitz
from judici.application.settings import secrets
from judici.dlp.data_sensitive import DlpText
from judici.repository.repository_s3 import RepositoryBucket
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class LoaderPdf(BaseModel):
    keyFile: str = Field(default=None, alias="keyFile")
    s3Repository: RepositoryBucket = Field(
        default=RepositoryBucket(bucket_name=secrets.app_bucket_name),
        alias="s3Repository",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def read_doc(self):
        try:

            # faz o download do arquivo do bucket S3
            local = self.s3Repository.download_file(self.keyFile)
            ext = os.path.splitext(local)[1]

            if ext != ".pdf":
                raise Exception("Arquivo não é um PDF")

            file = fitz.open(local)

            pages = []
            for idx in range(len(file)):
                page = file[idx]
                pages.append(page)

            return pages, file
        except Exception as e:
            print(f"[!] Erro ao processar o arquivo {self.keyFile}: {e}")
            raise e

    def get_images(self):
        try:
            pages, file = self.read_doc()
            for idx, page in enumerate(pages, start=1):
                image_list = page.get_images()

                if len(image_list) == 0:
                    continue

                for idx_image, img in enumerate(image_list, start=1):
                    xref = img[0]
                    base_image = file.extract_image(xref)
                    image = Image.open(io.BytesIO(base_image["image"]))
                    yield (idx, idx_image, image)

        except Exception as e:
            print(f"[!] Erro ao processar o arquivo {self.keyFile}: {e}")
            raise e

    def key_file(self):
        # remove a extensão do arquivo
        key = os.path.splitext(self.keyFile)[0]
        return key
    
    def get_text(self):
        pages, _ = self.read_doc()
        
        for page in pages:
            text = page.get_textpage()
            text = text.extractText()
            yield DlpText.mask_sensitive_data(text)[1]



    def extract_images_to_bucket(self, path_to_save: str = "extracted_images"):
        try:
            for idx, image in enumerate(self.get_images()):
                idx_page, idx_image, image = image
                image_path = f"{self.key_file()}_{idx_page}_{idx_image}.png"
                with tempfile.TemporaryDirectory() as tmpdirname:
                    image.save(f"{tmpdirname}/{image_path}")
                    self.s3Repository.upload_file(
                        f"{path_to_save}/{image_path}", 
                        f"{tmpdirname}/{image_path}"
                    )

        except Exception as e:
            print(f"[!] Erro ao processar o arquivo {self.keyFile}: {e}")
            raise e

    def get_text_page(self, page: int = 1):
        doc = self._document()
        text = doc.pages[page - 1].extract_text()
        return text

    def get_info_pdf(self):
        doc = self._document()

        return {
            "producer": doc.metadata.get("/Producer"),
            "title": doc.metadata.get("/Title"),
            "author": doc.metadata.get("/Author"),
        }

    def get_engine(self):
        engine = self.get_info_pdf()["producer"]
        return engine
