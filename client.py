import asyncio
import argparse


class RpcVal:
    def __init__(self, key):
        self.key = key


class RpcClient:
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.local_data = {}

    async def _send_request(self, request):
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            writer.write(request.encode())
            await writer.drain()

            data = await reader.read(1024)
            response = data.decode()

            writer.close()
            await writer.wait_closed()

            return response
        except Exception as e:
            return f"Error: {str(e)}"

    async def __agetitem__(self, key):
        if key in self.local_data:
            return self.local_data[key]
        response = await self._send_request(f'get "{key}"')
        if response.startswith("Result:"):
            return int(response.split(":")[1].strip())
        elif "Error" in response:
            return response
        else:
            raise ValueError("Unexpected server response")

    async def __asetitem__(self, key, value):
        if key in self.local_data:
            self.local_data[key] = value
        else:
            if not isinstance(value, int):
                raise ValueError("Only integers are allowed for remote values")
            response = await self._send_request(f'set "{key}" {value}')
            if "Error" in response:
                raise ValueError(response)

    def add_val(self, rpc_val):
        if not isinstance(rpc_val, RpcVal):
            raise ValueError("Expected an RpcVal instance")
        self.local_data[rpc_val.key] = None

    async def increment(self, value):
        if isinstance(value, int):
            key = next(iter(self.local_data), None)
            if key:
                current = await self.__agetitem__(key)
                await self.__asetitem__(key, current + value)


async def main():
    parser = argparse.ArgumentParser(description="Async RPC Client")
    parser.add_argument("--host", required=True, help="Server host")
    parser.add_argument("--port", required=True, help="Server port")
    args = parser.parse_args()

    rpc_client = RpcClient(host=args.host, port=args.port)
    print("Async client initialized.")

    rpc_client.add_val(RpcVal("test_key"))
    await rpc_client.__asetitem__("test_key", 10)
    val = await rpc_client.__agetitem__("test_key")
    print(f"Key value 'test_key': {val}")

    await rpc_client.increment(5)
    updated_val = await rpc_client.__agetitem__("test_key")
    print(f"New value 5: {updated_val}")


if __name__ == "__main__":
    asyncio.run(main())
