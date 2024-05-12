from __future__ import annotations

import json
import re
from typing import List

from judici.application.settings import (
    SecretsManager,
    secrets,
)
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import (
    BaseModel,
    Field,
    validator,
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel as Base
from pydantic import ConfigDict
from pydantic import Field as FieldData
import spacy


class DataSensitivePrompt(BaseModel):
    list_emails: List[str] = Field(description="List of emails identified")
    list_phones: List[str] = Field(description="List of phone numbers identified")
    list_names: List[str] = Field(
        description="list all names identified in the text"
    )
    list_names_in_uppercase: List[str] = Field(
        description="List of names in uppercase identified"
    )
    list_names_companies: List[str] = Field(
        description="List of names of companies identified"
    )
    list_addresses: List[str] = Field(description="List all addresses identified")
    list_cpfs: List[str] = Field(description="List of CPFs identified")
    list_cnpjs: List[str] = Field(description="List of CNPJs identified")
    list_rgs: List[str] = Field(description="List of RGs identified")
    list_autos_of_process: List[str] = Field(
        description="List of autos of process identified"
    )
    list_ip_addresses: List[str] = Field(description="List of IP addresses identified")


class AjusteText(BaseModel):
    text_to_correct: str = Field(description="Text to be corrected")


class DataPattern(Base):
    list_phones: List[str] = FieldData(
        default=[
            # (99) 9999-9999
            r"\(\d{2}\) \d{4}-\d{4}",
            # (99) 99999-9999
            r"\(\d{2}\) \d{5}-\d{4}",
            # 9999-9999
            r"\d{4}-\d{4}",
            # 99999-9999
            r"\d{5}-\d{4}",
            # 999999-9999
            r"\d{6}-\d{4}",
            # 9999999-9999
            r"\d{7}-\d{4}",
            # +55 99999-9999
            r"\+\d{2} \d{5}-\d{4}",
            # +55 999999-9999
            r"\+\d{2} \d{6}-\d{4}",
            # +55 9999999-9999
            r"\+\d{2} \d{7}-\d{4}",
        ],
        description="List of phone numbers",
    )


class DlpText(Base):
    text: str = FieldData(description="Text to be analyzed")
    user_query: str = FieldData(
        default="classify all confidential information, from every line"
        "like people's names, each time CPF appears,"
        "CNPJ, RG, CEP, email, phone, card number, IP, addresses's",
        description="User query",
    )
    pattern: DataPattern = FieldData(default=DataPattern())
    secrets: SecretsManager = FieldData(default=secrets)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def openai(self):

        model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            api_key=self.secrets.openai_token,
        )

        return model

    def parser(self, parser: object = DataSensitivePrompt):
        return PydanticOutputParser(pydantic_object=parser)

    def prompt(self):

        parser = self.parser()

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        return prompt

    def chain(self):
        prompt = self.prompt()
        model = self.openai()
        parser = self.parser()
        return prompt | model | parser

    def search_data_by_pattern(self):
        for key, value in self.pattern.model_dump().items():
            for data in value:
                self.text = re.sub(data, "****", self.text, flags=re.IGNORECASE)

        return self.text

    @classmethod
    def mask_sensitive_data(cls, text: str):
        obj = cls(text=text)
        chain = cls(text=text).chain()
        response = chain.invoke({"query": text})
        
        text = text.replace("\n", " ")
        
        for list_key, list_value in response.dict().items():
            for data in list_value:
                text = str(text)
                text = re.sub(data, "****", text, flags=re.IGNORECASE)
                
        for list_key, list_value_pattern in obj.pattern.model_dump().items():
            for data in list_value_pattern:
                text = re.sub(data, "****", text, flags=re.IGNORECASE)
                
        return response.dict(), str(text)