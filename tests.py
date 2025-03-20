import pytest
import asyncio
from client import (
    RpcClient,
    RpcVal,
)


@pytest.mark.asyncio
async def test_set_and_get():
    client = RpcClient("127.0.0.1", 53554)
    key = "test_key"
    value = 42

    client.add_val(RpcVal(key))

    await client.__asetitem__(key, value)

    result = await client.__agetitem__(key)
    assert result == value


@pytest.mark.asyncio
async def test_increment():
    client = RpcClient("127.0.0.1", 53554)
    key = "inc_key"
    start_value = 10
    increment_value = 5

    client.add_val(RpcVal(key))
    await client.__asetitem__(key, start_value)

    await client.increment(increment_value)

    result = await client.__agetitem__(key)
    assert result == start_value + increment_value
