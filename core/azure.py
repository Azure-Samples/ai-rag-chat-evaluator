import json
import logging
from abc import ABC
from typing import Awaitable, Callable, Optional, Union, AsyncGenerator, List
from dataclasses import asdict, is_dataclass

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI, AzureOpenAI
from typing_extensions import TypedDict

from core.error import error_dict


class ClientService(ABC):
    class AuthArgs(TypedDict, total=False):
        api_key: str
        azure_ad_token_provider: Callable[[], Union[str, Awaitable[str]]]

    def __init__(
        self,
        open_ai_service: str,
        open_ai_api_version: str,
        open_ai_emb_deployment: Optional[str] = None,
        open_ai_emb_model: Optional[str] = None,
        credential: Optional[Union[AsyncTokenCredential, AzureKeyCredential, DefaultAzureCredential]] = None,
    ):
        self.open_ai_api_version = open_ai_api_version
        self.open_ai_service = open_ai_service
        self.open_ai_emb_deployment = open_ai_emb_deployment
        self.open_ai_emb_model = open_ai_emb_model

        self.auth_args = self.AuthArgs()
        self.credential = credential if credential is not None else DefaultAzureCredential()

        self._init_auth()

        self.embedding_client: AsyncAzureOpenAI = self._create_embedding_client()

    def _init_auth(self):
        if isinstance(self.credential, AzureKeyCredential):
            self.auth_args["api_key"] = self.credential.key
        elif isinstance(self.credential, (AsyncTokenCredential, DefaultAzureCredential)):
            self.auth_args["azure_ad_token_provider"] = get_bearer_token_provider(
                self.credential, "https://cognitiveservices.azure.com/.default"
            )
        else:
            raise TypeError("Invalid credential type")

    def _create_embedding_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            azure_endpoint=f"https://{self.open_ai_service}.openai.azure.com",
            api_version=self.open_ai_api_version,
            timeout=120,
            **self.auth_args,
        )

    def compute_text_embedding(self, q: str) -> List[float]:
        embedding = self.embedding_client.embeddings.create(
            # Azure OpenAI takes the deployment name as the model name
            model=self.open_ai_emb_deployment if self.open_ai_emb_deployment else self.open_ai_emb_model,
            input=q,
        )
        query_vector: List[float] = embedding.data[0].embedding
        return query_vector


class JSONEncoder(json.JSONEncoder):
    """
    Class to handle custom objects created using the dataclasses module.
    It checks if the object is a data class and, if so, converts it into a dictionary using dataclasses.asdict().
    Otherwise, it utilizes the default JSON encoding behavior.
    """

    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


async def format_as_ndjson(r: AsyncGenerator[dict, None]) -> AsyncGenerator[str, None]:
    """
    Function takes an asynchronous generator r yielding dictionaries and converts each dictionary into a
    newline-delimited JSON (NDJSON) string. It ensures non-ASCII characters are preserved and handles exceptions
    gracefully, logging any encountered errors and yielding their corresponding JSON representations.
    """
    try:
        async for event in r:
            yield json.dumps(event, ensure_ascii=False, cls=JSONEncoder) + "\n"
    except Exception as error:
        logging.exception("Exception while generating response stream: %s", error)
        yield json.dumps(error_dict(error))
