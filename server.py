import asyncio

data = {}


def handle_request(request):
    global data
    try:
        command, *args = request.split()
        if command == "get":
            key = args[0].strip('"')
            if key in data:
                return f"Result: {data[key]}"
            return "Error: empty value"
        elif command == "set":
            key = args[0].strip('"')
            value = args[1]
            if value.isdigit():
                data[key] = int(value)
                return f"Result: {value}"
            return "Error: not a number"
        elif command == "getkeys":
            return " ".join(data.keys())
        else:
            return "Error: invalid command"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connected by {addr}")

    try:
        data_bytes = await reader.read(1024)
        request = data_bytes.decode()
        print(f"Received: {request}")

        response = handle_request(request)
        writer.write(response.encode())
        await writer.drain()
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def start_server(host="0.0.0.0", port=53554):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Async server is listening on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(start_server())
