import asyncio

async def echo(reader, writer):
    data = (await reader.readline()).decode().strip()
    try:
        res = sqroot
    except Exception:
        res = ""
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())