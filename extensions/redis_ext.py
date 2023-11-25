from IPython.core.magic import register_line_magic


def load_ipython_extension(ipython):
    print("Loaded extension watch_redis")

    @register_line_magic("watch_redis")
    def watch_redis(line: str):
        """Prints the whole redis store every 1 second.
        Uses the following objects if available (otherwise creates them):
        - redis_client
        - console
        """
        import json
        from time import sleep

        try:
            redis_client
        except NameError:
            from job_orchestration.kv_store.redis_job_client import JobStateClient

            job_state_client = JobStateClient()
            redis_client = job_state_client.in_progress_db.redis

        try:
            console
        except NameError:
            from rich.console import Console

            console = Console()

        previous_data = {}
        iteration = 0
        while True:
            iteration += 1
            data = {}
            for key in map(bytes.decode, redis_client.keys()):
                record = redis_client.get(key)
                if record:
                    if isinstance(record, bytes):
                        record = record.decode()
                        try:
                            record = json.loads(record)
                        except:
                            pass
                    data[key] = record
            if data != previous_data:
                print(f"─ {iteration = } ───────────────────────────────────────────")
                console.print_json(data=data, indent=4)
                previous_data = data
            sleep(1)
