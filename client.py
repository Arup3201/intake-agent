import sys
import time
from enum import Enum
from agent import Agent
from constants import queries

class Method(str, Enum):
    SINGLE = 'single'
    MULTI = 'multi'

perform: int = int(sys.argv[1]) if len(sys.argv) > 1 else 0

combination = [
    {
        # Develop Testing
        'product_limit': 10,
        'method': Method.MULTI,
        'query_limit': 2,
        'intake_assistant_id': '',
        'api_key': ''
    },
    {   
        # POC-50P100QS
        'product_limit': 50,
        'method': Method.SINGLE,
        'query_limit': 100,
        'intake_assistant_id': '',
        'api_key': ''
    },
    {
        # POC-50P100QM
        'product_limit': 50,
        'method': Method.MULTI,
        'query_limit': 100,
        'intake_assistant_id': '',
        'api_key': ''
    },
    {
        # POC-100P100QS
        'product_limit': 100,
        'method': Method.SINGLE,
        'query_limit': 100,
        'intake_assistant_id': '',
        'api_key': ''
    },
    {
        # POC-100P100QM
        'product_limit': 100,
        'method': Method.MULTI,
        'query_limit': 100,
        'intake_assistant_id': '',
        'api_key': ''
    },
    {
        # POC-200P100QS
        'product_limit': 200,
        'method': Method.SINGLE,
        'query_limit': 100,
        'intake_assistant_id': '',
        'api_key': ''
    },
    {
        # POC-200P100QM
        'product_limit': 200,
        'method': Method.MULTI,
        'query_limit': 100,
        'intake_assistant_id': '',
        'api_key': ''
    }
]

class Client:
    def __init__(self, product_limit: int, method: Method, query_limit: int, agent_api_key: str, intake_assistant_id: str):
        self.product_limit: int = product_limit
        self.method: str = method.value
        self.query_limit: int = query_limit
        self.agent_api_key: str = agent_api_key
        self.intake_assistant_id: str = intake_assistant_id
        self.agent = self.create_agent(self.agent_api_key)
        self.prepare_agent()
    
    def create_agent(self, agent_api_key: str):
        agent = Agent(api_key=agent_api_key)
        return agent

    def prepare_agent(self):
        # Create client product file
        product_file = open(f'./files/{self.product_limit}_products.txt', 'rb')
        file = self.agent.create_file(product_file)
        self.file_id = file.id

        # Create client vector storage
        vector_storage = self.agent.create_vector_storage(name=f'{self.product_limit}-products-{self.query_limit}-queries-{self.method}-method', file_ids=[file.id])
        self.vs_id = vector_storage.id

        # Run client queries
        self.run_queries()

    def run_queries(self):
        if self.method == Method.SINGLE.value:
            time_list = []
            in_token_list = []
            out_token_list = []
            total_token_list = []
            time_1 = time.time()
            first_query_run_response = self.agent.create_thread_run_poll(vs_id=self.vs_id, prompt=queries[0], assistant_id=self.intake_assistant_id)
            first_query_msg_list_response = self.agent.list_run_messages(thread_id=first_query_run_response.thread_id, run_id=first_query_run_response.run_id)
            time_2 = time.time()
            time_taken = time_2-time_1
            time_list.append(time_taken)
            in_token_list.append(first_query_run_response.prompt_tokens)
            out_token_list.append(first_query_run_response.completion_tokens)
            total_token_list.append(first_query_run_response.total_tokens)
            print(f"Query 1 Done in new thread in {time_taken:.2f}s with {first_query_run_response.prompt_tokens} in_tokens, {first_query_run_response.completion_tokens} out_tokens")
            thread_id = first_query_run_response.thread_id
            for index, query in enumerate(queries[1:self.query_limit]):
                time_1 = time.time()
                run_response = self.agent.run_poll(thread_id=thread_id, prompt=query, assistant_id=self.intake_assistant_id)
                msg_list_response = self.agent.list_run_messages(thread_id=run_response.thread_id, run_id=run_response.run_id)
                time_2 = time.time()
                time_taken = time_2-time_1
                time_list.append(time_taken)
                in_token_list.append(first_query_run_response.prompt_tokens)
                out_token_list.append(first_query_run_response.completion_tokens)
                total_token_list.append(first_query_run_response.total_tokens)
                print(f"Query {index+2} Done in same thread in {time_taken:.2f}s with {run_response.prompt_tokens} in_tokens, {run_response.completion_tokens} out_tokens")
            print(f"Total time: {sum(time_list):.2f}s/{self.query_limit} queries | Average time: {sum(time_list)/len(time_list):.2f}s/query")
            print(f"Total In_token {sum(in_token_list)} | Total Out_token {sum(out_token_list)} | Total Total_token {sum(total_token_list)}")
            print(f"Average In_token {sum(in_token_list)/len(in_token_list)} | Average Out_token {sum(out_token_list)/len(out_token_list)} | Average Total_token {sum(total_token_list)/len(total_token_list)}")


        elif self.method == Method.MULTI.value:
            time_list = []
            in_token_list = []
            out_token_list = []
            total_token_list = []
            for index, query in enumerate(queries[:self.query_limit]):
                time_1 = time.time()
                run_response = self.agent.create_thread_run_poll(vs_id=self.vs_id, prompt=query, assistant_id=self.intake_assistant_id)
                msg_list_response = self.agent.list_run_messages(thread_id=run_response.thread_id, run_id=run_response.run_id)
                time_2 = time.time()
                time_taken = time_2-time_1
                time_list.append(time_taken)
                in_token_list.append(run_response.prompt_tokens)
                out_token_list.append(run_response.completion_tokens)
                total_token_list.append(run_response.total_tokens)
                print(f"Query {index+1} Done in new thread in {time_taken:.2f}s with {run_response.prompt_tokens} in_tokens, {run_response.completion_tokens} out_tokens")
            print(f"Total time: {sum(time_list):.2f}s/{self.query_limit} queries | Average time: {sum(time_list)/len(time_list):.2f}s/query")
            print(f"Total In_token {sum(in_token_list)} | Total Out_token {sum(out_token_list)} | Total Total_token {sum(total_token_list)}")
            print(f"Average In_token {sum(in_token_list)/len(in_token_list)} | Average Out_token {sum(out_token_list)/len(out_token_list)} | Average Total_token {sum(total_token_list)/len(total_token_list)}")
        
        

client = Client(
    product_limit=combination[perform]['product_limit'], 
    method=combination[perform]['method'], 
    query_limit=combination[perform]['query_limit'], 
    agent_api_key=combination[perform]['api_key'], 
    intake_assistant_id=combination[perform]['intake_assistant_id']
)