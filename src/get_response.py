import base64

from openai import OpenAI


def prompt_for_response(query: str, scene_info: str) -> str | None:
    return f"""
### Role
You are an expert blender script writer. 

### Task
Your task is to write a Blender script based on the user's query. The script should be executed in a live Blender console and must:

## Rules
- Clear any existing objects in the scene, if needed.
- Create objects as specified in the user query with realistic dimensions, positions, and orientations relative to each other.
- Ensure all objects are named descriptively and uniquely based on their function and characteristics.
- Place objects in logical positions within the scene, ensuring connections or joints between objects are precise (e.g., legs touching a table top).
- Avoid syntax errors and ensure the script is ready to run without modification.

Enclose the script in a code block like the following example:
```python
import bpy

scale = 0.5

def add_sphere(name, location, radius):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, enter_editmode=False)
    obj = bpy.context.object
    obj.name = name

# Add three spheres to form a snowman at x = 0
add_sphere('Snowman Base', (0, 0, 0), scale * 0.5) 
add_sphere('Snowman Middle', (0, 0, 1.5), 0.8)
add_sphere('Snowman Head', (0, 0, 2.7), 0.6)
```

### User Query
{query}

### Current Scene Information
{scene_info}
"""


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_ai_response(
    client: OpenAI, query: str, scene_info: str, photo_path: str
) -> str | None:

    text_prompt = prompt_for_response(query, scene_info)
    if text_prompt is None:
        return None
    try:
        base64_image = encode_image(photo_path)
    except Exception as e:
        print(f"Error while encoding image: {e}")
        return None

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        model="gpt-4o",
    )
    res = chat_completion.choices[0].message.content
    return res
