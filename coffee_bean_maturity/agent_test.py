import streamlit as st
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.google_genai import GoogleGenAI
import nest_asyncio
import os
import cv2

from dotenv import load_dotenv
from inference import detect_coffee_labels

nest_asyncio.apply()
load_dotenv()

# Get Google API key
google_api_key = os.getenv('GOOGLE_API_KEY')

# Initialize LLM and embedding model

llm = GoogleGenAI(
    model_name="gemini-1.5-flash",
    max_output_tokens=1000,
    temperature=0.2,
    api_key=google_api_key,
)

def coffee_detection_tools(image_path: str) -> str:
    """
    Wrapper function to detect coffee bean maturity levels in an image.
    Args:
        image_path (str): Path to the image file
    Returns:
        str: Detection results describing coffee bean maturity in a readable format
    """
    try:
        # Load image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return "Error: Could not load the image. Please check the file path."
        results = detect_coffee_labels(img)
        
        if not results['boxes'] or not results['labels']:
            return "No coffee beans detected in the image."
        
        formatted_result = f"Detected {len(results['boxes'])} coffee bean(s):\n"
        
        label_counts = {}
        for label in results['labels']:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        formatted_result += f"\nTotal beans: {len(results['labels'])} - Distribution:\n"
        for label, count in label_counts.items():
            formatted_result += f"- {label}: {count} bean(s)\n"
        return formatted_result
        
    except Exception as e:
        return f"Error during coffee bean detection: {str(e)}"

# build tool
coffee_tool = FunctionTool.from_defaults(
    fn=coffee_detection_tools,
    name="detect_coffee_maturity",
    description="Analyze an image to detect coffee bean maturity levels. " \
    "This tool identifies different stages of coffee bean ripeness including underripe, semi_ripe, ripe, " \
    "dry and overripe beans. Use this when user uploads an image of coffee beans, asks about coffee bean analysis."
)

#  simple agent
agent = FunctionAgent(
    tools=[ coffee_tool ],
    llm=llm,
    system_prompt="You are an assistant that can use tools to analyze coffee bean maturity levels in images and answer question related to coffee bean knowledge field. ",
    verbose=True,
)

sample_query = "Can I harvest this tree? how many beans are there?."
# sample_query = "What is the maturity level of the coffee beans in this image? Can you analyze it?"
# sample_query = "What's wrong with my tree?"

sample_image_path = "./sample/IMG_6583-1.jpg"

from llama_index.core.agent.workflow import AgentStream, ToolCallResult

async def main():
    enhanced_query = f"""You have access to a coffee bean detection tool. The user has uploaded an image located at: {sample_image_path}
    User question: {sample_query}
    To answer this question, please use the detect_coffee_maturity tool with the exact image path: {sample_image_path}
        - If the user has not uploaded an image (path is invalid or empty), please inform them to upload an image first.
        - If the image is not suitable for analysis (return tools are empty or error), please inform them that the image is invalid.
        - If user not asking about coffee bean maturity, please answer the question directly without using the tool.
        - Don't return any keywords related to tool usage, just return the answer in a human-readable format.
    """
    handler = agent.run(enhanced_query)
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCallResult):
            print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
        if isinstance(ev, AgentStream):
            print(f"{ev.delta}", end="", flush=True)
    response = await handler
    print(f"\n\nFinal response: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# def main():
#     st.set_page_config(
#         page_title="Coffee Bean Maturity Agent",
#         page_icon="☕",
#         layout="wide"
#     )
    
#     st.title("☕ Coffee Bean Maturity Detection Agent")
#     st.markdown("Upload an image of coffee beans and ask questions about their maturity using AI!")
    
#     # Sidebar for image upload
#     with st.sidebar:
#         st.header("🖼️ Image Upload")
#         uploaded_file = st.file_uploader(
#             "Choose an image file", 
#             type=['png', 'jpg', 'jpeg'],
#             help="Upload an image of coffee beans for analysis"
#         )
        
#         if uploaded_file is not None:
#             image = Image.open(uploaded_file)
#             st.image(image, caption="Uploaded Image", use_column_width=True)
            
#             # Save uploaded file with proper extension handling
#             file_extension = uploaded_file.name.split('.')[-1].lower()
#             temp_dir = tempfile.gettempdir()
#             temp_image_path = os.path.join(temp_dir, f"uploaded_coffee_image.{file_extension}")
            
#             # Write the file
#             with open(temp_image_path, "wb") as f:
#                 f.write(uploaded_file.getvalue())
            
#             # Verify file was created
#             if os.path.exists(temp_image_path):
#                 st.session_state.current_image_path = temp_image_path
#                 st.success(f"Image uploaded successfully! Saved to: {temp_image_path}")
                
#                 # Debug info
#                 file_size = os.path.getsize(temp_image_path)
#                 st.info(f"File size: {file_size} bytes")
#             else:
#                 st.error("Failed to save uploaded image")
        
#         # Control buttons
#         if st.button("🗑️ Clear Image"):
#             if hasattr(st.session_state, 'current_image_path'):
#                 try:
#                     os.unlink(st.session_state.current_image_path)
#                 except:
#                     pass
#                 del st.session_state.current_image_path
#             st.rerun()
        
#         if st.button("🧹 Clear Chat"):
#             st.session_state.messages = []
#             st.rerun()
    
#     # Main chat interface
#     st.subheader("💬 Chat with the Coffee Expert Agent")
    
#     # Initialize chat history
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
    
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Suggested prompts
#     if not st.session_state.messages:
#         st.markdown("**💡 Try these prompts:**")
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             if st.button("Analyze uploaded image"):
#                 if hasattr(st.session_state, 'current_image_path'):
#                     prompt = "Please analyze the coffee beans in the uploaded image and tell me about their maturity levels."
#                 else:
#                     prompt = "Please upload an image first to analyze coffee beans."
#                 st.session_state.messages.append({"role": "user", "content": prompt})
#                 st.rerun()
        
#         with col2:
#             if st.button("What can you detect?"):
#                 prompt = "What types of coffee bean maturity can you detect and analyze?"
#                 st.session_state.messages.append({"role": "user", "content": prompt})
#                 st.rerun()
        
#         with col3:
#             if st.button("How does detection work?"):
#                 prompt = "How does the coffee bean maturity detection process work?"
#                 st.session_state.messages.append({"role": "user", "content": prompt})
#                 st.rerun()
    
#     # Chat input
#     if prompt := st.chat_input("Ask about coffee bean maturity or request image analysis..."):
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         # Get agent response
#         with st.chat_message("assistant"):
#             with st.spinner("🤔 Analyzing..."):
#                 try:
#                     # Enhanced query with image context if available
#                     if hasattr(st.session_state, 'current_image_path'):
#                         # Create a more explicit instruction for the agent
#                         enhanced_query = f"""You have access to a coffee bean detection tool. The user has uploaded an image located at: {st.session_state.current_image_path}

#     User question: {prompt}

#     To answer this question, please use the detect_coffee_maturity tool with the exact image path: {st.session_state.current_image_path}"""
#                     else:
#                         if any(keyword in prompt.lower() for keyword in ['analyze', 'detect', 'image', 'beans', 'harvest']):
#                             enhanced_query = f"{prompt}\n\nNote: No image has been uploaded yet. Please upload an image to perform coffee bean detection and analysis."
#                         else:
#                             enhanced_query = prompt
                    
#                     response = agent.chat(enhanced_query)
#                     st.markdown(str(response))
                    
#                     # Add assistant response to chat history
#                     st.session_state.messages.append({"role": "assistant", "content": str(response)})
                    
#                 except Exception as e:
#                     error_msg = f"❌ Error: {str(e)}"
#                     st.error(error_msg)
#                     st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
#     # Status indicator
#     with st.sidebar:
#         st.markdown("---")
#         if hasattr(st.session_state, 'current_image_path'):
#             st.success("✅ Image loaded and ready for analysis")
#         else:
#             st.info("📁 No image uploaded")
        
#         if google_api_key:
#             st.success("✅ Gemini API connected")
#         else:
#             st.error("❌ Missing GOOGLE_API_KEY in environment")

# if __name__ == "__main__":
#     main()
