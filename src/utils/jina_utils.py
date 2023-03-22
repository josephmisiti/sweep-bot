import requests  # type: ignore
from pydantic import BaseModel
from docarray import DocumentArray


class JinaClient(BaseModel):
    url: str

    def __init__(self, host: str):
        super().__init__(url=host)

    def search(self, query: str):
        payload = {"data": [{"text": query}], "parameters": {}}
        response = requests.post(f"{self.url}/search", json=payload)
        return response.json()["data"]
    
    def index(self, docs: DocumentArray):
        docs_array = docs.to_dict()
        payload = {"data": docs_array, "parameters": {}}
        response = requests.post(f"{self.url}/index", json=payload)
        return response.json()["data"]
