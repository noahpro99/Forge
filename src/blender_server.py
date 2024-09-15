import json
import os
import socket
import threading

import bpy

# Define the file path for saving the scene information
SCENE_INFO_FILE = r"C:\\Users\noahp\tmp\scene_info.json"
PHOTO_FILE = r"C:\\Users\noahp\tmp\image.png"


def exec_script(script):
    global_namespace = {"__name__": "__main__"}
    try:
        exec(script, global_namespace)
    except Exception as e:
        import traceback

        traceback.print_exc()


def run_in_main_thread(script):
    # Use Blender's timers to defer execution to the main thread
    bpy.app.timers.register(lambda: exec_script(script), first_interval=0.1)


def gather_scene_info():
    # Gather scene information on the main thread
    scene_info = {}
    scene_info["objects"] = []

    for obj in bpy.data.objects:
        obj_info = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(coord, 2) for coord in obj.location],
            "rotation_euler": [round(angle, 2) for angle in obj.rotation_euler],
            "scale": [round(factor, 2) for factor in obj.scale],
            "dimensions": [round(size, 2) for size in obj.dimensions],
            "materials": (
                [mat.name for mat in obj.data.materials]
                if obj.data and hasattr(obj.data, "materials")
                else []
            ),
        }
        scene_info["objects"].append(obj_info)

    # Save the gathered information to a file
    with open(SCENE_INFO_FILE, "w") as file:
        json.dump(scene_info, file, indent=2)

    print(f"Scene information saved to {SCENE_INFO_FILE}.")
    return None  # Return None for bpy.app.timers requirements


def take_photo():
    sce = bpy.context.scene.name
    bpy.data.scenes[sce].render.filepath = PHOTO_FILE

    # Render image through viewport
    bpy.ops.render.opengl(write_still=True)
    print(f"Photo saved to {PHOTO_FILE}.")
    return None  # Return None for bpy.app.timers requirements


def execute_and_gather(script):
    # Run the received script on the main thread
    run_in_main_thread(script)

    # Schedule gathering scene info after script execution on the main thread
    bpy.app.timers.register(gather_scene_info, first_interval=0.2)


def set_all_viewport_color(color):
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.background_color = color
                    break


def set_viewport_green():
    # set_all_viewport_color((0.105744, 0.287725, 0.127732))
    set_all_viewport_color((0.002, 0.124, 0.002))


def set_viewport_normal():
    set_all_viewport_color((0.05, 0.05, 0.05))


def set_fairy_listening():
    # bpy.app.timers.register(
    #     set_viewport_green,
    #     first_interval=0.1,
    # )
    pass


def set_fairy_processing():
    # bpy.app.timers.register(
    #     set_viewport_normal,
    #     first_interval=0.1,
    # )
    pass


def handle_client(connection):
    script = []
    while True:
        data = connection.recv(4096)
        if not data:
            break
        script.append(data)
    script = b"".join(script)

    if script:
        script_text = script.decode("utf-8")
        if script_text.startswith("run script"):
            # Extract and execute the script after "run script"
            script_content = script_text[len("run script ") :].strip()
            print("Executing script on main thread...")
            execute_and_gather(script_content)
        elif script_text.startswith("take photo"):
            print("Taking photo of the current scene...")
            bpy.app.timers.register(take_photo, first_interval=0.1)
        elif script_text.startswith("fairy listening"):
            set_fairy_listening()
        elif script_text.startswith("fairy processing"):
            set_fairy_processing()
        else:
            print(f"Received unknown command: {script_text}")

    connection.close()


def server_thread():
    PORT = 8081
    HOST = "localhost"
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.listen(1)
    print(f"Listening on {HOST}:{PORT}")
    while True:
        connection, address = serversocket.accept()
        print(f"Connection from {address}")
        handle_client(connection)


def start_server():
    server = threading.Thread(target=server_thread, daemon=True)
    server.start()
    print("Server started in a separate thread.")


if __name__ == "__main__":
    start_server()

    # Keep Blender's main thread running to avoid blocking UI
    bpy.ops.mesh.primitive_plane_add()
    print("Blender is running and responsive.")
    # set to green
    set_viewport_green()

    # clear all objects, lights, and cameras
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.type in {"MESH", "LIGHT", "CAMERA"}:
            obj.select_set(True)
    bpy.ops.object.delete()

    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.background_type = "VIEWPORT"
                    found = True
                    break
            if found:
                break
