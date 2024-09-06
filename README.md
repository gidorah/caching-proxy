# caching-proxy

CLI tool that starts a caching proxy server, it will forward requests to the actual server and cache the responses.

This project build as one of roadmap.sh Backend Projects: https://roadmap.sh/projects/caching-server

## usage

### start proxy-server

    caching-proxy --port <number> --origin <url>

### query with curl

    curl "http://127.0.0.1:3000/carts/2"

### clear cache

    caching-proxy --clear-cache