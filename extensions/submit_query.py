from IPython.core.magic import register_line_magic


def load_ipython_extension(ipython):
    def parse_args(line) -> dict:
        """Parses:
        SQL_QUERY (first positional argument)
        -j, --job-type {query,preview}
        """
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("SQL_QUERY", help="SQL query to execute", nargs="*")
        parser.add_argument("-j", "--job-type", help="Job type", choices=["query", "preview"], default="query")
        args = parser.parse_args(line.split())
        return vars(args)

    @register_line_magic("submit_query")
    def submit_query(line: str):
        import json
        import time

        import requests
        from rich import print as rprint

        job_type = 'query'
        query_type = 'query'
        query = 'SELECT 9'
        node = 'entity'
        if line:
            args = parse_args(line)
            if args["SQL_QUERY"]:
                query = " ".join(args["SQL_QUERY"])
            if args["job_type"]:
                job_type = args["job_type"]
        data = {'queries': {node: {'compiled_query': query, 'query_type': query_type, 'job_type': job_type}}}
        query_id = requests.post('http://localhost:8000/api/v2/queries/1/2/submit',
                                 headers={'x-tenant-id': 'tenant'},
                                 data=json.dumps(data)).json()[node]
        for _ in range(50):
            response = requests.get(f'http://localhost:8000/api/v2/queries/{query_id}/status').json()
            rprint(_, response)
            time.sleep(0.5)
