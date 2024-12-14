import argparse
import socket
import threading
from typing import List, Dict

from settings import rlog, Config, HTTP_429
from ratelimiter.tokenbucket import TokenBucket


def handle_client_request(
    client_conn: socket.socket, 
    client_addr: tuple, 
    upstreams_config: List[Dict[str, str]], 
    rate_limiter: TokenBucket
) -> None:
    """
    Handles the communication between the client and upstream servers. 
    It forwards the request from the client to upstream servers, 
    enforces rate-limiting, and returns the response back to the client.

    Args:
        client_conn (socket.socket): The client connection object.
        client_addr (tuple): The client's address (host, port).
        upstreams_config (List[Dict[str, str]]): List of upstream servers' details.
        rate_limiter (TokenBucket): The rate limiter instance.
    """
    while True:
        rlog.debug("Awaiting data from client: %s", client_addr)
        request_data = client_conn.recv(2046)

        if not request_data:
            rlog.debug("Client disconnected: %s", client_addr)
            break

        if not rate_limiter.consume():
            rlog.warning("Rate limit exceeded for client: %s", client_addr)
            client_conn.sendall(HTTP_429.encode())
            continue

        upstream_sockets = establish_upstream_connections(upstreams_config)
        rlog.debug("Tokens remaining: %s", rate_limiter.tokensleft)

        # Sequentially forward the request to each upstream server
        for upstream_socket in upstream_sockets:
            rlog.debug("Forwarding data to upstream: %s", upstream_socket.getpeername())
            upstream_socket.sendall(request_data)

            rlog.debug("Awaiting response from upstream: %s", upstream_socket.getpeername())
            upstream_response = upstream_socket.recv(2046)

            rlog.debug("Forwarding upstream response to client: %s", client_addr)
            client_conn.sendall(upstream_response)

            # Close the upstream connection after response is sent
            rlog.info("Closing upstream connection: %s", upstream_socket.getpeername())
            upstream_socket.close()


def establish_upstream_connections(upstreams_config: List[Dict[str, str]]) -> List[socket.socket]:
    """
    Establishes connections to the upstream servers based on provided configuration.

    Args:
        upstreams_config (List[Dict[str, str]]): List of upstream servers' details.

    Returns:
        List[socket.socket]: List of socket connections to the upstream servers.
    """
    upstream_connections = []

    for upstream in upstreams_config:
        upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream_socket.connect((upstream['host'], upstream['port']))
        upstream_connections.append(upstream_socket)

    return upstream_connections


def start_server(port: int, upstreams_config: List[Dict[str, str]]) -> None:
    """
    Starts the server that listens for client connections, handles rate-limiting, 
    and forwards the requests to upstream servers.

    Args:
        port (int): The port on which the server will listen.
        upstreams_config (List[Dict[str, str]]): The list of upstream server configurations.
    """
    rlog.info("Starting service on port: %d", port)
    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    rate_limiter = TokenBucket()

    while True:
        connection, client_addr = server_socket.accept()
        rlog.info("Client connected: %s", client_addr)
        threading.Thread(target=handle_client_request, args=[connection, client_addr, upstreams_config, rate_limiter]).start()


def parse_command_line_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for configuring the rate limiter service.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    rlog.info("Initializing Rate Limiter Service")
    parser = argparse.ArgumentParser(description='Rate Limiter Service Args')
    parser.add_argument("--port", help="Rate limiter service port", type=int, default=8005)
    parser.add_argument("--config", help="Rate limiter service configuration file", type=str, default="config.yaml")
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_command_line_arguments()

    # Load configuration for upstream servers
    upstreams_config = Config(args.config).get_upstream()

    # Start the rate-limiting server
    start_server(args.port, upstreams_config)
