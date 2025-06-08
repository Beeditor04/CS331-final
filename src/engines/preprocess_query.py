from fast_langdetect import detect
import re
from llama_index.llms.azure_openai import AzureOpenAI
from src.prompts.chatbot_prompt import add_tone_marks_prompt
from dotenv import load_dotenv
import os
from difflib import SequenceMatcher
from pydantic import BaseModel
from typing import Literal, Optional, Tuple, Dict, Any, List
from llama_index.core.program import LLMTextCompletionProgram
from src.engines.llm_engine import LLMEngine


class QueryOutput(BaseModel):
    query_str: str
    lang: Literal["Tiếng Việt", "Tiếng Anh", "Others"]


class TextPreprocessor:
    def __init__(self):
        load_dotenv()
        self.abbreviation_dict = {
            "hcm": "hồ chí minh",
            "hn": "hà nội",
            "dn": "đà nẵng",
            "ct": "cần thơ",
            "tp": "thành phố",
            "ttdt": "trung tâm đào tạo nghề",
            "csdt": "cơ sở đào tạo",
            "câm": "khuyết tật nói nặng",
            # "mù": "khuyết tật nhìn nặng",
            # "điếc": "khuyết tật nghe nặng",
            "cv": "công việc",
            # ...
        }
        self.short_chat = [
            # short_chat term
            "chào bạn",
            "chào bạn",
            "chaofo bạn",
            "chao ban",
            "hello",
            "hi",
            "xin chào",
            "xin chao",
            "hihi",
            "haha",
            "hoho",
            "hehe",
            "lol",
            "kk",
            "xin chào",
            "chào",
            "hello",
            "hi",
            "bạn khỏe không",
            "ban khoe khong",
            "khỏe không",
            "khoe khong",
            "dạ vâng",
            "da vang",
            "vâng",
            "vang",
            "cảm ơn bạn",
            "cam on ban",
            "cảm ơn",
            "cam on",
            "thank you",
            "thanks",
            "haha",
            "hihi",
            "hoho",
            "hehe",
            "lol",
            "kk",
            "đúng rồi",
            "dung roi",
            "đúng",
            "dung",
            "tạm biệt",
            "tam biet",
            "bye",
            "goodbye",
            "uh huh",
            "uhm",
            "uh",
            "uhhuh",
            "ồ thật sao",
            "o that sao",
            "thật sao",
            "that sao",
            "thế à",
            "the a",
            "thật à",
            "that a",
            "ồ",
            "o",
            "wow",
            "woww",
            "wowww",
            "ừ",
            "u",
            "ừm",
            "um",
            "dạ",
            "da",
        ]
        self.config = LLMEngine()
        self.llm = self.config.llm2
        self.program = self.init_program()
        self.INTAB = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ" \
                     "ẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐ"


    def replace_abbreviations(self, text):
        words = text.split()
        replaced_words = [
            self.abbreviation_dict.get(word.lower(), word) for word in words
        ]
        return " ".join(replaced_words)
    
    def detect_short_chat(self, text):
        normalized_text = text.lower().strip()
        def is_similar(text1, text2, threshold=0.85):
            return SequenceMatcher(None, text1, text2).ratio() >= threshold

        matches_pattern = any(
            is_similar(normalized_text, pattern) for pattern in self.short_chat
        )

        if matches_pattern:
            return (text, 'Tiếng Việt')
        else:
            return False
    
    def language_check(self, text):
        try:
            lang = detect(text)
            if lang['lang'] == 'vi':
                return 'Vietnamese'
            elif lang['lang'] == 'en':
                return 'English'
            else:
                return 'Other'
        except Exception as e:
            print(f"Error in language detection: {e}")
            return 'Unknown'

    def remove_punctuation(self, text):
        return re.sub(r'[^\w\s]', '', text)


    def check_tone_mark(self, text):
        try:
            words = self.remove_punctuation(text).split()
            count = sum(
                all(char not in self.INTAB for char in word) for word in words
            )

            ratio = count / len(words)
            return ratio < 0.7
        except Exception as e:
            print(f"Error in tone mark check: {e}")

    def add_tone_marks(self, text):
        result = self.llm.complete(prompt=add_tone_marks_prompt.format(query_str=text))
        return result.text

    def translate_to_vn(self, text):
        result = self.llm.complete(prompt=f"Dịch câu sau của người dùng sang tiếng việt: {text}")
        return result.text
    
    def init_program(self):
        program = LLMTextCompletionProgram.from_defaults(
            output_cls=QueryOutput,
            llm=self.llm,
            prompt_template_str=add_tone_marks_prompt,
        )
        return program
    
    def refine_special_case(self, text):
        text = re.sub(r'(?<!\btôi\s)(\bbị\b)', r'tôi \1', text, flags=re.IGNORECASE)
        # Replace "là sao" with "là gì"
        text = re.sub(r'\blà sao\b', ' là gì ', text, flags=re.IGNORECASE)
        
        return text

    def preprocess_text(self, text):

        if self.detect_short_chat(text):
            return (text, 'Tiếng Việt')

        elif self.language_check(text) == 'Vietnamese':
            text = self.replace_abbreviations(text)
            text = self.refine_special_case(text)
            return (text, 'Tiếng Việt')
        else:
            result = self.program(query_str=text)
            preprocessed_text = result.query_str
            lang = result.lang

            return (preprocessed_text, lang)


        # lang = self.language_check(text)
        # if lang == 'Other':
        #     return(
        #     """
        #     Xin lỗi, tôi chỉ hỗ trợ Tiếng Việt hoặc Tiếng Anh. Vui lòng thử lại với câu hỏi khác.
        #     Sorry, I only support Vietnamese or English. Please try again with another question.
        #     """,
        #     True
        #     )
        # else:
        #     if lang == 'Vietnamese':
        #         if not self.check_tone_mark(text):
        #             return (self.add_tone_marks(text), False)
        #         else:
        #             return text, False
        #     elif lang == 'English':
        #         return (self.translate_to_vn(text), False)

