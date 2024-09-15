## Inspiration

The inspiration for Forge emerged from observing the hurdles that we faced when entering the world of 3D modeling. Traditional tools like Blender are powerful but come with a steep learning curve, often requiring hours of training and practice. We wanted to eliminate these barriers and make 3D design accessible to everyone, regardless of their technical background. By leveraging AI and voice technology, we envisioned a platform where creativity isn't limited by technical skill, allowing anyone to bring their ideas to life simply by speaking.

## What It Does

Forge is an AI-powered voice assistant that allow you to use your voice to engineer 3D models in real time using Blender. Users can describe the objects they want to create—such as "Build a red brick house with a blue door and a chimney"—and Forge interprets these instructions to generate the model instantly. This hands-free approach simplifies the 3D modeling process, making it intuitive and engaging for designers, hobbyists, educators, and students alike.

## How We Built It

- **Voice Recording & Transcription:** The process begins when the user speaks a command into the microphone. Your voice command is recorded and transcribed using OpenAI’s Whisper that accurately converts spoken language into text.
- **Viewport Capture:** Simultaneously, Blender takes a snapshot of the current 3D scene viewport and the state of the blender scene. This provides context for the AI to understand the existing state of the model and how the new command should modify it.
- **AI Script Generation**: The transcribed text and the captured image are sent to GPT-4 model that generates a tailored Blender script. This script is designed and customized based on the current scene and user prompt.
- **Real-Time Execution**: Through socket and multithreading, the generated script runs in Blender instantly, updating the scene in real-time. This immediate execution allows users to see the results of their voice commands right away.

## Challenges We Ran Into

During the development of Forge, we encountered several significant challenges:

- **Blender Script Execution While GUI Is Open:** We faced difficulties getting Blender to run the generated scripts while the GUI was open, which interfered with the real-time interaction we aimed for. The solution was to schedule the script execution on Blender's main thread while simultaneously listening for incoming Python scripts over a socket connection. This required careful threading and synchronization to ensure stability and responsiveness.
- **Visual Cues for Voice Activation:** Providing a visual cue to indicate when the model was actively listening to voice commands proved challenging. Initially, we wanted a clear on-screen indicator within Blender, but integrating this feature smoothly was complex. We ended up with a compromise: implementing audio cues and changing the background color to signal when the system was listening. 

## Accomplishments That We're Proud Of

We are proud of several key accomplishments:

- **Innovative Interaction Model:** Introducing voice-controlled 3D modeling, which is a novel approach in the industry, making design more accessible and engaging.
- **Technical Achievement:** Successfully integrating complex technologies to work together seamlessly in real-time.
- **Democratizing 3D Design:** Lowering the barriers to entry for 3D modeling, allowing a broader audience to express their creativity without the steep learning curve.

## What We Learned

Throughout the development of Forge, we learned:

- **The Importance of User-Centered Design:** Focusing on the needs and experiences of the end-user leads to a more intuitive and successful product.
- **Interdisciplinary Collaboration Is Key:** Combining expertise from different fields such as AI, software development, and design results in more innovative solutions.
- **Adaptability and Iteration:** Being open to feedback and willing to iterate on our designs and algorithms significantly improved the final product.
- **The Potential of AI in Creative Fields:** Leveraging AI technologies can open up new avenues for creativity and user interaction.

## What's Next for Forge

Looking ahead, we have exciting plans for Forge:

- **Enhanced Features:** Adding more complex modeling capabilities, such as being able to influence model with hand drawn sketch in the viewport.
- **Multilingual Support:** Expanding voice recognition and NLP capabilities to support multiple languages, making Forge accessible globally.
- **Platform Expansion:** Integrating Forge with other 3D platforms and VR/AR environments to broaden its applications.

We are excited about the future of Forge and its potential to transform how people approach 3D modeling, making it an inclusive and creative experience for all.
