import socket
import os
from urllib.request import urlopen
from urllib.error import HTTPError
import argparse
from datetime import datetime

CACHE_DIR = "./cache"
CACHING_TIMEOUT = 1000

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-p", "--port", type=int)
arg_parser.add_argument("-o", "--origin")
arg_parser.add_argument("--clear-cache", action="store_true")
args = arg_parser.parse_args()


def fetch_from_cache(url):
    cache_file_path = os.path.join(CACHE_DIR, url.replace("/", "_"))

    if not os.path.exists(cache_file_path):
        return None

    file_modified_time = os.path.getmtime(filename=cache_file_path)
    current_time = datetime.now().timestamp()
    if current_time - file_modified_time > CACHING_TIMEOUT:
        os.remove(cache_file_path)
        return None

    with open(cache_file_path, "r") as cache_file:
        return cache_file.read()


def save_to_cache(url, content):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    cache_file_path = os.path.join(CACHE_DIR, url.replace("/", "_"))
    with open(cache_file_path, "w") as cache_file:
        cache_file.write(content)


def parse_url_from_request(request):
    if not request:
        return None

    request_parts = request.split("\r\n")

    url = request_parts[0].split(" ")[1]
    url = args.origin + url
    return url


def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    url = parse_url_from_request(request)
    cached_content = fetch_from_cache(url)

    if cached_content:
        print("Cache hit. Serving from cache.")
        response = f"HTTP/1.0 200 OK\r\nX-Cache: HIT\r\nContent-Length: {len(cached_content)}\r\n\r\n{cached_content}"
        client_socket.sendall(response.encode())
    else:
        print("Cache miss. Fetching from server.")

        try:
            response = urlopen(url)
            content = response.read().decode()
            save_to_cache(url, content)
            response = f"HTTP/1.0 200 OK\r\nX-Cache: MISS\r\nContent-Length: {len(content)}\r\n\r\n{content}"

        except HTTPError as e:
            response = f"HTTP/1.0 {e.status} FAIL\r\nContent-Length: {len(e.msg)}\r\n\r\n{e.msg}"

        client_socket.sendall(response.encode())
    client_socket.close()


def start_proxy_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Proxy server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client(client_socket)


if __name__ == "__main__":
    if args.clear_cache is True:
        for file in os.listdir(CACHE_DIR):
            os.remove(f"{CACHE_DIR}/{file}")

        print("Cache cleared")
        exit()

    start_proxy_server("127.0.0.1", args.port)
