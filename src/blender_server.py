# Updated Server script: blender_server.py
PORT = 8081
HOST = "localhost"

import socket
import threading


def exec_script(script):
    global_namespace = {
        "__name__": "__main__",
    }
    exec(script, global_namespace)


def server_thread():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.listen(1)

    print(f"Listening on {HOST}:{PORT}")
    while True:
        connection, address = serversocket.accept()
        print(f"Connection from {address}")

        script = b""
        while True:
            data = connection.recv(4096)
            if not data:
                break
            script += data

        if script:
            print("Executing script...")
            try:
                exec_script(script.decode("utf-8"))
            except Exception as e:
                import traceback

                traceback.print_exc()
        connection.close()


def start_server():
    server = threading.Thread(target=server_thread, daemon=True)
    server.start()
    print("Server started in a separate thread.")


if __name__ == "__main__":
    start_server()

    # Keep Blender's main thread running to avoid blocking UI
    import bpy

    # Example: add a plane (this is just a placeholder, keep Blender responsive)
    bpy.ops.mesh.primitive_plane_add()
    print("Blender is running and responsive.")
