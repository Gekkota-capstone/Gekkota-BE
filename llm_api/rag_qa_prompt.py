import os
import json
import faiss
import numpy as np
import openai
import time
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from typing import List, Dict

from repository.chat_repository import ChatRepository
from repository.pet_repository import PetRepository
from repository.pet_health_repository import PetHealthRepository

CONVERSATION_LOG = "conversation_log.json"

# ===== 설정 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX = os.path.join(BASE_DIR, "rag_faiss.index")
METADATA_JSON = os.path.join(BASE_DIR, "rag_metadata.json")
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 3
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
GPT_MODEL = "gpt-3.5-turbo-0125"
ALLOWED_KEYWORDS = [
    # 기본 주제
    "도마뱀", "게코", "레오파드게코", "레오파드", "파충류", "생물",

    # 행동 및 스트레스
    "스트레스", "움직임", "움직이지", "가만히", "멍", "반응 없음", "공격", "물었", "위협", "도망", "숨었", "행동 변화",

    # 먹이 관련
    "먹이", "식욕", "밥", "안 먹", "잘 먹", "급여", "사료", "강제급여", "코오로기", "밀웜", "소화", "체중",

    # 환경/사육장
    "온도", "습도", "조명", "UVB", "바닥재", "히터", "매트", "케이지", "사육장", "환경", "은신처", "배경지", "청소", "설치", "환기",

    # 건강/질병/상태
    "탈피", "기생충", "상처", "눈", "피부", "꼬리", "부러짐", "질병", "감염", "건강", "비정상", "증상", "창백", "색이 변함", "혈변", "구토", "약",

    # 배변
    "똥", "배변", "변", "설사", "소변", "대변", "배설", "화장실", "변비",

    # 성장/나이/수명
    "성장", "크기", "나이", "몇 살", "수명", "언제 성체", "성체", "노령", "노화",

    # 관리 및 청결
    "청소", "위생", "주기", "물", "정수", "먹이통", "온도계", "습도계",

    # 비용 및 병원
    "병원", "진료", "진료비", "가격", "비용", "치료", "수의사", "약값", "진단", "검사", "예약",

    # 합사/사이
    "합사", "싸움", "무는", "같이 키워", "수컷", "암컷", "번식", "교배", "임신", "알",

    # 수면/일상
    "잠", "자는", "낮잠", "밤에 움직", "야행성", "낮에도 움직", "활동 시간",

    # 기타 실생활 질문 유추
    "추천", "초보", "처음", "키우기 쉬운", "처음 키움", "장비", "장점", "단점", "주의사항", "기초", "처방", "상담", "소리", "울음소리",

    # 대화 흐름 / 말 걸기 / 일반 표현 허용
    "안녕", "하이", "ㅎㅇ", "있어?", "있나요", "있음?", "있니", "어때", "그래서", "응", "맞아", "그럼",
    "근데", "혹시", "이건", "그건", "이게", "저기", "잠깐", "계속", "뭐더라", "그거", "이렇게", "저렇게",
    "다시", "계속해", "이어서", "추가로", "말해줘", "좀 더", "조금 더", "정리해줘", "도와줘", "설명해줘",
    "뭐야", "뭔데", "왜", "어떻게", "알려줘", "말해", "답해줘", "뭔가", "그니까", "그런데", "또", "계속", "그러면"

]
SIMILARITY_THRESHOLD = 1.2
LOG_RETENTION_HOURS = 24

# ===== 초기화 =====
embed_model = None
index = None
metadata = None


def init_llm_system():
    global embed_model, index, metadata
    print("모델과 인덱스를 불러오는 중...")
    openai.api_key = OPENAI_API_KEY
    openai.organization = OPENAI_ORG_ID
    embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    index = faiss.read_index(FAISS_INDEX)
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print("✅ 시스템 초기화 완료!")


def embed_text(text, model):
    return model.encode([text], convert_to_numpy=True)


def retrieve(query_embedding, index, metadata, top_k=TOP_K):
    distances, indices = index.search(query_embedding, top_k)
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])
    return results, distances[0]


def truncate_text(text, max_chars):
    if not text:
        return ""
    return text if len(text) <= max_chars else text[:max_chars] + "..."


def get_pet_info(db: Session, pet_id: str, firebase_uid: str) -> dict:
    """Get pet information from database"""
    pet_repo = PetRepository()
    pet = pet_repo.get_by_id(db, pet_id)

    if not pet or pet.firebase_uid != firebase_uid:
        return None

    return {
        "id": pet.pet_id,
        "name": pet.name,
        "species": pet.species,
        "gender": pet.gender,
        "birthdate": pet.birthdate.isoformat() if pet.birthdate else None,
        "traits": []  # This would come from another table if needed
    }


def get_latest_health_record(db: Session, pet_id: str) -> dict:
    """Get the latest health record for a pet"""
    health_repo = PetHealthRepository()
    health_records = health_repo.get_by_pet(db, pet_id)

    if not health_records:
        return {
            "date": None,
            "weight": None,
            "memo": None,
            "shedding_status": None,
            "photo_urls": None
        }

    # Sort by date (most recent first)
    health_records.sort(key=lambda x: x.date, reverse=True)
    latest = health_records[0]

    return {
        "date": latest.date.isoformat() if latest.date else None,
        "weight": latest.weight,
        "memo": latest.memo,
        "shedding_status": latest.shedding_status,
        "photo_urls": None  # Assuming no photo URLs in current schema
    }


def format_pet_context(pet_info, latest_record):
    if not pet_info:
        return "[반려동물 정보를 찾을 수 없습니다]"

    return f"""
[도마뱀 프로필]
이름: {pet_info['name']}
종: {pet_info['species']}
성별: {pet_info['gender']}
생일: {pet_info['birthdate']}
특징: {', '.join(pet_info['traits'])}

[최근 건강 기록]
날짜: {latest_record['date']}
몸무게: {latest_record['weight']}g
메모: {truncate_text(latest_record['memo'], 100)}
탈피 상태: {latest_record['shedding_status']}
"""


def load_recent_conversation_from_db(db: Session, firebase_uid: str) -> List[Dict]:
    repo = ChatRepository()
    all_chats = repo.get_by_user(db, firebase_uid)

    # timezone-aware datetime으로 생성
    from datetime import timezone
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOG_RETENTION_HOURS)

    recent_chats = [
        chat for chat in all_chats
        if chat.created_at and chat.created_at > cutoff
    ]

    # Sort by created_at
    recent_chats.sort(key=lambda x: x.created_at)

    # Convert to conversation format
    conversation = []
    for chat in recent_chats:
        conversation.append({"role": "user", "question": chat.question})
        if chat.answer:
            conversation.append({"role": "assistant", "answer": chat.answer})

    return conversation


def is_valid_query(query, db: Session = None, firebase_uid: str = None):
    if not query.strip():
        return False  # 빈 입력 방지

    # 키워드 기반 검사 (기존 로직 유지)
    if any(k.replace(" ", "") in query.replace(" ", "") for k in ALLOWED_KEYWORDS):
        return True

    # DB에서 최근 대화 기록 확인
    if db and firebase_uid:
        try:
            history = load_recent_conversation_from_db(db, firebase_uid)
        except Exception as e:
            print(f"DB 대화 기록 로드 오류: {e}")
            history = []
    else:
        history = []

    last_user_questions = [entry["question"] for entry in reversed(history) if entry["role"] == "user"][:5]

    # GPT에게 흐름을 판단시키기 (기존 로직 유지)
    context = "다음은 사용자의 최근 대화 흐름입니다.\n"
    for i, q in enumerate(reversed(last_user_questions)):
        context += f"{i + 1}. {q}\n"
    context += f"{len(last_user_questions) + 1}. {query}\n\n"
    context += (
        "이 대화 흐름은 사용자가 도마뱀(또는 파충류)에 관심을 가지고 이어가는 일관된 주제의 대화입니까?\n"
        "도마뱀에 대한 직접적인 질문뿐 아니라, 해당 주제를 바탕으로 한 감정 표현, 외모 언급, 반응 유도, 생각 공유, 사육 관련 간접적 대화 등도 포함됩니다.\n"
        "예를 들어 인사, 감탄, 의견 교환, 자연스러운 연결 질문 등은 도마뱀과의 관련성이 이어진다면 Y입니다.\n"
        "단, 도마뱀과 무관한 일상 대화(예: 날씨, 음식, 뉴스 등)로 주제가 명확히 바뀐 경우만 N으로 판단하세요.\n"
        "대화 흐름이 도마뱀 중심이라면 반드시 Y, 관련 없다면 N으로만 답하세요."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 대화 흐름이 주제 안에서 유지되는지 판단하는 전문가야. 반드시 Y 또는 N으로만 답해."},
                {"role": "user", "content": context}
            ],
            max_tokens=1,
            temperature=0
        )
        result = response.choices[0].message.content.strip().upper()
        print(f"🔍 흐름 기반 GPT 판단: {result}")
        return result == "Y"
    except Exception as e:
        print("흐름 판단 오류:", e)
        return True  # 오류 시 통과


def generate_answer(contexts, question, pet_info=None, latest_record=None, db=None, firebase_uid=None):
    context_text = "\n".join([truncate_text(c["content"], 400) for c in contexts])
    personal_info = format_pet_context(pet_info, latest_record) if pet_info and latest_record else ""

    history = load_recent_conversation_from_db(db, firebase_uid) if db and firebase_uid else []

    message_history = [
                          {"role": "system", "content": "당신은 도마뱀 사육 전문가입니다."},
                      ] + [
                          {"role": "user", "content": h["question"]} if h.get("role") == "user" else {
                              "role": "assistant", "content": h["answer"]}
                          for h in history[-10:]
                      ]

    message_history.append({"role": "user", "content": f"""
{personal_info}

[질문]
{question}

[참고자료]
{context_text}

지침:
1. 위의 반려동물 정보를 참고하여 개인화된 조언을 제공하세요.
2. 최근 건강 기록이 있다면 이를 바탕으로 구체적인 조언을 하세요.
3. 질문이 도마뱀 관련이 아닐 경우, "저는 도마뱀에 대한 질문만 답변할 수 있습니다."라고만 응답하세요.
4. 응답은 완결된 문장으로 끝나도록 하세요.
"""})

    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=message_history,
            temperature=0.3,
            max_tokens=800,  # 400 -> 800으로 증가
            top_p=0.9  # 응답 품질 개선
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"OpenAI API 호출 오류: {e}")
        return "죄송합니다. 현재 AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."


def handle_query(query: str, pet_id: str, firebase_uid: str, db: Session) -> str:
    """
    Main function to handle user queries

    Args:
        query: User's question
        pet_id: Pet ID
        firebase_uid: User's Firebase UID
        db: Database session

    Returns:
        Generated answer
    """
    if not embed_model or not index or not metadata:
        raise RuntimeError("시스템이 초기화되지 않았습니다. init_llm_system()을 먼저 호출하세요.")

    # Validate query
    if not is_valid_query(query, db, firebase_uid):
        return "❗ 이 시스템은 도마뱀 관련 질문만 처리합니다."

    # Get pet information
    pet_info = get_pet_info(db, pet_id, firebase_uid)
    if not pet_info:
        return "죄송합니다. 해당 반려동물 정보를 찾을 수 없거나 접근 권한이 없습니다."

    # Get latest health record
    latest_record = get_latest_health_record(db, pet_id)

    # Retrieve relevant contexts
    query_emb = embed_text(query, embed_model)
    contexts, distances = retrieve(query_emb, index, metadata)
    if distances[0] > SIMILARITY_THRESHOLD:
        contexts = [{"content": ""}]

    # Generate answer
    return generate_answer(contexts, query, pet_info, latest_record, db, firebase_uid)