import asyncio
import websockets
import socket
import json

C_SERVER_IP = "127.0.0.1"
C_SERVER_PORT = 9527

async def forward_to_c_server(websocket):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((C_SERVER_IP, C_SERVER_PORT))
        sock.setblocking(False)
        print("浏览器已连接，转发到 C++ 服务器")

        async def ws_to_c():
            async for message in websocket:
                sock.send((message + "\n").encode())

        async def c_to_ws():
            while True:
                try:
                    data = sock.recv(4096).decode()
                    if data:
                        await websocket.send(data)
                except BlockingIOError:
                    await asyncio.sleep(0.01)
                except:
                    break

        await asyncio.gather(ws_to_c(), c_to_ws())

    except Exception as e:
        print(f"连接错误: {e}")
    finally:
        sock.close()

async def main():
    async with websockets.serve(forward_to_c_server, "0.0.0.0", 8765):
        print("WebSocket 网关运行在 ws://0.0.0.0:8765")
        await asyncio.Future()

asyncio.run(main())
