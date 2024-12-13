import json
from typing import IO
from openai import OpenAI
from pydantic import BaseModel
from IPython.display import display

class File(BaseModel):
    id: str

class VectorStorage(BaseModel):
    id: str

class Run(BaseModel):
    thread_id: str
    run_id: str
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class Agent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client: OpenAI = OpenAI(api_key=self.api_key)

    def create_file(self, file: IO[bytes]) -> File:
        create_file_response = self.client.files.create(
            file=file,
            purpose='assistants'
        )
        show_json(create_file_response)
        return File(id=create_file_response.id)

    def create_vector_storage(self, name: str, file_ids: list[str]) -> VectorStorage:
        create_vector_storage_response = self.client.beta.vector_stores.create(
            name=name,
            file_ids=file_ids
        )
        show_json(create_vector_storage_response)
        return VectorStorage(id=create_vector_storage_response.id)
    
    def create_thread_run_poll(self, vs_id: str, prompt: str, assistant_id: str) -> Run:
        create_thread_run_poll_response = self.client.beta.threads.create_and_run_poll(
            assistant_id=assistant_id,
            thread = {
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'tool_resources': {
                    'file_search': {
                        'vector_store_ids': [vs_id]
                    }
                }
            }
        )
        show_json(create_thread_run_poll_response)
        return Run(
            thread_id=create_thread_run_poll_response.thread_id, 
            run_id=create_thread_run_poll_response.id, 
            completion_tokens=create_thread_run_poll_response.usage.completion_tokens if create_thread_run_poll_response.usage else -1,
            prompt_tokens=create_thread_run_poll_response.usage.prompt_tokens if create_thread_run_poll_response.usage else -1,
            total_tokens=create_thread_run_poll_response.usage.total_tokens if create_thread_run_poll_response.usage else -1
            )
    
    def run_poll(self, thread_id: str, prompt: str, assistant_id: str) -> Run:
        run_poll_response = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
            additional_messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        show_json(run_poll_response)
        return Run(
            thread_id=thread_id, 
            run_id=run_poll_response.id,
            completion_tokens=run_poll_response.usage.completion_tokens if run_poll_response.usage else -1,
            prompt_tokens=run_poll_response.usage.prompt_tokens if run_poll_response.usage else -1,
            total_tokens=run_poll_response.usage.total_tokens if run_poll_response.usage else -1
            )
    
    def list_run_messages(self, thread_id: str, run_id: str):
        run_messages_list_response = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            run_id=run_id
        )
        show_json(run_messages_list_response)
        return run_messages_list_response.data
    
def show_json(obj):
    # display(json.loads(obj.json()))
    pass