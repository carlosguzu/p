
import concurrent.futures
import time
import requests
import psutil  # For monitoring system metrics
import matplotlib.pyplot as plt

# List of URLs to fetch
URLS = [
    'http://www.google.com',
    'http://www.bing.com',
    'http://www.yahoo.com',
    'http://www.duckduckgo.com',
    'http://www.example.com',
    'http://www.python.org',
    'http://www.github.com',
    'http://www.stackoverflow.com',
    'http://www.wikipedia.org',
    'http://www.reddit.com',
]


def fetch_url(url):
    try:
        # Added timeout for robustness
        response = requests.get(url, timeout=10)
        # print(f"{url} fetched with {len(response.content)} bytes")
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_with_workers(worker_type, max_workers, urls):
    if worker_type == "thread":
        executor_class = concurrent.futures.ThreadPoolExecutor
    else:
        executor_class = concurrent.futures.ProcessPoolExecutor

    start_time = time.time()
    start_cpu = psutil.cpu_percent(interval=None)  # CPU usage before execution
    start_memory = psutil.virtual_memory().used  # Memory usage before execution

    with executor_class(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_url, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Ensures all tasks are completed

    end_time = time.time()
    end_cpu = psutil.cpu_percent(interval=None)
    end_memory = psutil.virtual_memory().used

    duration = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    memory_consumed = (end_memory - start_memory) / \
        (1024 * 1024)  # Convert to MB

    print(f"{worker_type.capitalize()}s with {
          max_workers} workers took: {duration:.2f} seconds")
    print(f"CPU usage change: {cpu_usage:.2f}% | Memory consumed: {
          memory_consumed:.2f} MB")
    return duration


def run_experiments():
    worker_counts = [1, 2, 4, 8, 16, 32]
    urls = URLS * 8  # Increase the number of tasks
    results = {"thread": {}, "process": {}}

    for worker_type in ["thread", "process"]:
        for count in worker_counts:
            duration = fetch_with_workers(worker_type, count, urls)
            results[worker_type][count] = duration

    # Plotting results
    plt.figure(figsize=(10, 6))
    for worker_type, durations in results.items():
        plt.plot(worker_counts, list(durations.values()),
                 label=f'{worker_type.capitalize()}s')

    plt.xlabel('Number of Workers')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs Number of Workers (Threads vs Processes)')
    plt.legend()
    plt.grid(True)
    plt.show()


# Run the experiments
if __name__ == "__main__":
    run_experiments()
