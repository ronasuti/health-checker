import asyncio
from urllib.parse import urlparse
import yaml
import sys
import httpx


async def parseHttpEndpoints(yaml_file_path) -> list:
    # get dictionary from YAML file
    data = None
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    # fix endpoint keys to match client.request parameters
    for i in range(len(data)):
        data[i]['content'] = data[i].pop('body', "")
        data[i].pop("name")
    return data

async def healthCheck(endpoints: list, latency_threshold: int = 500, retry_interval: int = 15):
    # Call endpoint 1 and check if it returns a 2XX OK response and within latency target
    # keep track of per-domain health [total, healthy]
    domains = {urlparse(endpoint["url"]).netloc : [0, 0] for endpoint in endpoints}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Call all endpoints concurrently, then add to domains dict
        async def oneRoundOfChecks():
            tasks = []
            for endpoint in endpoints:
                # endpoint dicts should match request parameters, spread them
                tasks.append(client.request(**endpoint))
            responses = await asyncio.gather(*tasks)
            # get request health, keep track in domains dict
            for response in responses:
                if (response.status_code >= 200 and 
                    response.status_code < 300 and 
                    response.elapsed.total_seconds() * 1000 < latency_threshold):
                    domains[urlparse(response.url).netloc][1] += 1
                domains[urlparse(response.url).netloc][0] += 1
            # print health status
            for domain, (total, healthy) in domains.items():
                print(f"{domain} has {healthy / total}% availability percentage")
        
        # Rerun the checks every retry_interval seconds.
        while True:
            asyncio.gather(oneRoundOfChecks(), asyncio.sleep(retry_interval))

async def main():
    # Get the YAML file as the first argument, parse it
    yaml_file_path = sys.argv[1]
    endpoints = await parseHttpEndpoints(yaml_file_path)
    # Call the health check function for each endpoint, goes into infinite loop
    await healthCheck(endpoints)

if __name__ == "__main__":
    asyncio.run(main())