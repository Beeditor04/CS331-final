from pydantic import BaseModel
import random
from src.utils.utility import create_new_id
from src.demo.default_prompt import reference_prompt
from src.services.service import Service
from datetime import datetime
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage
from src.routers.dependencies import (
    get_service
)
from src.prompts.default_answer import not_supported_language
from src.engines.preprocess_query import TextPreprocessor
from fastapi import (
    APIRouter, 
    status, 
    Depends, 
    HTTPException, 
    File, 
    UploadFile, 
    Form, 
    Query,
    BackgroundTasks
)
from fastapi.responses import StreamingResponse
from src.schemas.chatbot import (
    InputChatbotMessage,
    ChatbotMessage
)
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN_LIMIT = int(os.getenv("TOKEN_LIMIT", 10000))

chatbot_router = APIRouter(
    tags=["chatbot"],
    prefix="/chatbot",
)

text_preprocessor = TextPreprocessor()

@chatbot_router.post("/chat")
async def chat_with_agent(request: InputChatbotMessage , service: Service = Depends(get_service)):
    try:

        # Initialize memory
        memory = ChatMemoryBuffer(token_limit=TOKEN_LIMIT)

        user_message = request.message
        session_id = request.session_id

        # Initialize memory for the session if it doesn't exist
        if not session_id:
            session_id  = create_new_id("chatbot-session")

        conversation_histories = service.chatbot_mess_mgmt.get_conversation_history(session_id)
        memory.put_messages(conversation_histories)
        
        # Preprocess the user message
        preprocessed_message, lang = text_preprocessor.preprocess_text(user_message)
        print(f"Preprocessed message: {preprocessed_message}")
        print(f"Language detected: {lang}")
        # Check if the language is supported
        if lang == "Others":
            return not_supported_language
        if lang == "Tiếng Anh":
            chat_history = [
            ChatMessage(role="user", content="Từ bây giờ bạn phải trả lời bằng tiếng anh"),
            ChatMessage(role="assistant", content="Okay, I will respond in English from now on."),
            ] 
            memory.put_messages(chat_history)  

        memory.put_messages([
            ChatMessage(role="user", content=reference_prompt),
            ChatMessage(role="assistant", content="Tôi nhớ rồi, tôi sẽ luôn trích dẫn thông tin đúng theo yêu cầu nếu có."),
        ])

        reply = await service.chatbot.handle_query(
            query=preprocessed_message,
            memory=memory,

        )
        chat_message = ChatbotMessage(
            session_id=session_id,
            chat_message=user_message,
            answer=reply,
            datetime=datetime.now(),
        )

        service.chatbot_mess_mgmt.insert_chat_record(chat_message)
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@chatbot_router.post("/chat-stream")
async def chat_with_agent_stream(request: InputChatbotMessage, service: Service = Depends(get_service)):
    try:
        memory = ChatMemoryBuffer(token_limit=TOKEN_LIMIT)
        user_message = request.message
        session_id = request.session_id

        conversation_histories = service.chatbot_mess_mgmt.get_conversation_history(session_id)
        memory.put_messages(conversation_histories)

        preprocessed_message, lang = text_preprocessor.preprocess_text(user_message)
        print(f"Preprocessed message: {preprocessed_message}")
        print(f"Language detected: {lang}")
        if lang == "Others":
            return not_supported_language

        # memory.put_messages([
        #     ChatMessage(role="user", content=reference_prompt),
        #     ChatMessage(role="assistant", content="Tôi nhớ rồi, tôi sẽ luôn trích dẫn thông tin đúng theo yêu cầu nếu có."),
        # ])

        if lang == "Tiếng Anh":
            memory.put_messages([
                ChatMessage(role="user", content="The next prompt you be given is the translated version of the original prompt, the original prompt is in English so you have to answer in English"),
                ChatMessage(role="assistant", content="I understand. I'll continue responding in English. If you need any information or assistance, feel free to ask!"),
            ])

        async def event_generator():
            reply_parts = []
            async for chunk in service.chatbot.stream_query(preprocessed_message, memory=memory):
                reply_parts.append(chunk)
                yield chunk

            reply = ''.join(reply_parts)
            
            chat_message = ChatbotMessage(
                session_id=session_id,
                chat_message=user_message,
                answer=reply,
                datetime=datetime.now(),
            )
            service.chatbot_mess_mgmt.insert_chat_record(chat_message)

        return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        # raise HTTPException(status_code=500, detail=str(e))
        print(f"Error in chat_with_agent_stream: {e}")
        return "Có vẻ như câu hỏi của bạn có chứa thông tin nhạy cảm mà tôi không thể xử lý được. Vui lòng thử lại với câu hỏi khác nhé!"
    

@chatbot_router.get("/chat/get-suggest-questions")
async def get_suggest_questions():
    """Get the suggest questions for job search chat.

    Returns:
        List of suggest questions.
    """
    try:
        default_questions = [
            "Cây cà phê có được hỗ trợ kỹ thuật miễn phí không?",
            "Có trung tâm khuyến nông nào hỗ trợ chẩn đoán bệnh cây cà phê ở Hà Nội không?",
            "Tôi muốn biết về các loại bệnh thường gặp trên cây cà phê",
            "Bạn có thể tư vấn kỹ thuật trồng cà phê cho tôi không?",
            "Có trung tâm giống cà phê nào ở Đà Nẵng không?",
            "Cây cà phê không phát triển tốt thì nguyên nhân có thể là gì?",
            "Người trồng cà phê có được hưởng chính sách hỗ trợ nào không?",
            "Tôi muốn biết về các chính sách hỗ trợ trồng và chăm sóc cà phê",
            "Có nơi nào hỗ trợ phát hiện sớm bệnh rỉ sắt trên cà phê không?",
            "Có giống cà phê nào năng suất cao và kháng bệnh không?",
            "Tôi muốn biết về các bước đánh giá sức khỏe vườn cà phê",
            "Tôi là nông dân trồng cà phê thì có nhận được trợ cấp phân bón hay giống không?",
            "Cây cà phê của tôi bị vàng lá và tôi muốn cải thiện năng suất",
            "Cây cà phê bị rụng trái hàng loạt thì tôi nên xử lý thế nào?",
            "Tôi cần tư vấn cách bón phân để tăng năng suất cà phê",
            "Tôi muốn biết các biện pháp canh tác phù hợp với vùng đất bazan",
            "Tôi muốn biết các giống cà phê phù hợp với vùng Tây Nguyên",
            "Tôi muốn biết cách cải tạo vườn cà phê già cỗi để tăng sản lượng",
            "Tôi muốn biết các biện pháp phòng bệnh thối rễ trên cà phê",
            "Tôi muốn biết cách xử lý cây cà phê bị nấm gây chết chậm",
            "Tôi muốn biết biện pháp canh tác cho cây cà phê bị thiếu nước",
            "Tôi muốn biết cách chăm sóc cây cà phê trong mùa khô",
            "Tôi muốn biết cách tưới nước và tỉa cành cho cà phê để tăng năng suất",
            "Tôi không biết nên bắt đầu chăm sóc vườn cà phê như thế nào, bạn giúp tôi nhé"
        ]

        language_preference = ["I want to be supported in English"]
        random_questions = random.sample(default_questions, 5)
        random_questions = random_questions + language_preference
        

        return random_questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e