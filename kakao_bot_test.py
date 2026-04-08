from fastapi import FastAPI, Request
import uvicorn
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv

# [추가됨] 구글 Gemini 라이브러리
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# .env 파일 로드
load_dotenv()

app = FastAPI(title="Kakao Chatbot Test v2.0 - AI Powered")

# Gemini API 설정 (발급받은 API 키가 .env 파일에 있어야 함)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

@app.post("/api/kakao")
def kakao_webhook(body: dict):
    """
    카카오 i 오픈빌더에서 스킬로 연결될 웹훅 엔드포인트입니다.
    고객의 문제를 파악하고 사진/영상 첨부를 유도하는 봇 로직 (v2.0 AI 연동)
    """
    try:
        user_utterance = ""
        if "userRequest" in body and "utterance" in body["userRequest"]:
            user_utterance = body["userRequest"]["utterance"].strip()
            
        print(f"고객 발화 수신: '{user_utterance}'")
        
        reply_message = ""
        
        if GEMINI_API_KEY:
            # ----------------------------------------------------
            # [진짜 AI 모드] Gemini를 통한 문맥 완벽 이해
            # ----------------------------------------------------
            prompt = f"""
            너는 프리미엄 쇼핑몰 고객센터를 담당하는 전문적이고 신뢰감 있는 '실제 사람(시니어 상담원)'이야. 
            절대 본인이 AI나 챗봇이라는 사실이나 뉘앙스를 풍기지 말고, 베테랑 상담원이 직접 응대하는 것처럼 완벽하게 행세해.
            
            [핵심 행동 수칙: 눈치 있는 상황 판단 - 가장 중요!!!]
            먼저 고객의 말 문맥을 파악해!
            상황 A) 구체적 문의 없이 단순히 "안녕하세요", "저기요", "하이" 등 짧은 인사나 부름만 있는 경우: 
               -> 절대로 [폼 양식]을 출력하지 마! 그저 인사를 받아주며 "안녕하십니까, 무엇을 도와드릴까요?" 정중하게 한 문장으로만 응대해!
            상황 B) 단순 인사가 아니라, 제품 문의, 불만, 고장, 교환, 누락, 배송 등 구체적인 사연이나 증상이 조금이라도 포함된 경우: 
               -> 깊이 공감하거나 다독이는 맞춤형 멘트를 1문장 건네고, 신속/정확하게 처리하기 위해 아래 [폼 양식 안내]를 반드시 기재해 달라고 요청해.
            상황 C) 이벤트, 커피, 쿠폰, 사은품, 리뷰 혜택 등에 대해 질문하거나 언급하는 경우:
               -> 아래의 [이벤트 안내 텍스트]를 토씨 하나 빼먹지 말고 그대로 출력하여 친절하게 안내해.
               ※ 만약 고객이 상황 B와 상황 C를 동시에 언급한다면, B의 폼 양식 안내와 C의 이벤트 안내를 모두 포함시켜서 안내해!
            
            [폼 양식 안내 - 오직 상황 B 관련된 경우일때만 출력할 것]
            - 주문자 성함: 
            - 구매 채널(쿠팡, 스토어 등): 
            - 연락처: 
            - 제품명: 
            
            [이벤트 안내 텍스트 - 오직 상황 C 관련된 경우일때만 출력할 것]
            ✨포토 리뷰 작성하면 메가커피 아메리카노 100% 증정!
            ✨1. 구매내역과 2. 포토리뷰를 캡쳐해서 https://tally.so/r/MeOXLX 으로 전송 해주세요.
            
            조건 (절대 엄수):
            1. 어조 제어 ('다나까' 필수): 모든 답변의 끝부분은 가벼운 '~요' 체 대신, 격식 있고 정중한 '하십시오체(~입니다, ~합니다, ~바랍니다, ~까?)'로만 마무리해. 과도한 이모티콘 사용 금지.
            2. 마크다운 사용 원천 금지: 글씨를 강조하려는 별표(**), 샵(#), 숫자 목록 등의 마크다운 기호를 절대 쓰지 말고 오직 평범하고 깨끗한 텍스트 문자와 일반 기호(- 등)만 사용해.
            3. 어색한 멘트 금지: 시작할 때 "저는 상담원입니다" 같은 기계적인 자기소개는 무조건 생략하고, 곧바로 공감과 인사를 진행해.
            4. (매우 중요) 상황 B에서 고장/파손/불량/누락 문맥이 감지되면, 폼 양식 하단에 반드시 아래 [시각 자료 요청 멘트]를 요약하거나 생략하지 말고 온전히 덧붙여 안내해.
               [시각 자료 요청 멘트 내용]: "증상에 맞는 가장 적합한 솔루션을 제공해 드리기 위해 관련 사진이나 영상이 꼭 필요합니다. 단순한 설명만으로는 자칫 잘못된 안내가 나갈 수 있어, 시각 자료를 통해 세밀히 판독하고자 합니다. 정확한 진단이 있어야 고객님께 최선의 해결 방법을 제시해 드릴 수 있으니, 불편하시더라도 잠시만 시간을 내어 하단 메뉴의 '+' 버튼을 눌러 첨부를 부탁드립니다."
            5. 카카오톡 타임아웃 차단을 위해 가급적 간결하게 답변하되, 4번의 [시각 자료 요청 멘트]나 상황 C의 [이벤트 안내 텍스트]가 포함될 경우엔 답변 길이 제한(4~5문장)을 예외적으로 해제함.
            
            고객의 말: "{user_utterance}"
            상담원 답변:
            """
            
            try:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=4.5)
                if res.status_code == 200:
                    reply_message = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    print("🧠 AI 응답 성공!")
                else:
                    err_msg = res.text[:200]
                    print("Gemini API 호출 에러:", res.text)
                    reply_message = f"죄송합니다, AI 분석 중 문제가 발생했습니다. 상태코드: {res.status_code}, 요약: {err_msg}"
            except requests.exceptions.Timeout:
                reply_message = "현재 문의 처리량이 많아 답변 생성에 시간이 걸리고 있습니다. 상담원이 곧바로 이어받아 시원하게 해결해 드리겠습니다! 잠시만 기다려주세요."
            except Exception as e:
                print("Gemini API 요청 중 예외 발생:", e)
                reply_message = "죄송합니다, AI를 연결할 수 없습니다."
                
        else:
            # ----------------------------------------------------
            # [기본 키워드 모드] API 키가 없을 때 동작하는 예비용 로직
            # ----------------------------------------------------
            problem_keywords = ["고장", "파손", "깨져", "불량", "작동", "안되", "안켜져", "에러", "오류", "문제", "누락", "이상", "스크래치"]
            info_keywords = ["시간", "언제", "얼마", "결제", "배송", "안녕", "반품", "교환", "영업"]
            
            is_problem = any(kw in user_utterance for kw in problem_keywords)
            is_info = any(kw in user_utterance for kw in info_keywords)
            
            if is_problem:
                reply_message = (
                    f"고객님, 겪고 계신 '{user_utterance}' 상황을 확인했습니다.\n\n"
                    "가장 신속정확하게 원인을 파악하기 위해 "
                    "해당 문제가 나타나는 부분의 **사진이나 짧은 영상**을 여기에 첨부해 주시겠어요?\n\n"
                    "(💡 현재 AI 키가 등록되지 않아 기본 머신 모드로 작동 중입니다. .env에 키를 등록하세요!)"
                )
            elif is_info and not is_problem:
                reply_message = (
                    f"말씀하신 '{user_utterance}' 관련 일반 안내입니다.\n\n"
                    "추가로 궁금한 점이 있으실까요?\n\n"
                    "(💡 현재 AI 키가 등록되지 않아 기본 머신 모드로 작동 중입니다. .env에 키를 등록하세요!)"
                )
            else:
                reply_message = (
                    "문의하신 내용을 확인 중입니다.\n\n"
                    "혹시 제품 문제가 있으시다면 관련된 **사진이나 영상**을 함께 남겨주세요!\n\n"
                    "(💡 현재 AI 키가 등록되지 않아 기본 머신 모드로 작동 중입니다. .env에 키를 등록하세요!)"
                )

    except Exception as e:
        print("데이터 파싱 에러:", e)
        reply_message = "알 수 없는 오류가 발생했습니다. 잠시 후 다시 말씀해 주시겠어요?"
    
    # 카카오톡 스킬 응답(JSON) 규격에 맞추어 반환
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": reply_message
                    }
                }
            ]
        }
    }
    return response

if __name__ == "__main__":
    print("==================================================")
    print("🤖 카카오톡 CS 챗봇 서버가 구동 중입니다. (v2.0 - AI 탑재 완료)")
    print("로컬 주소: http://127.0.0.1:5055")
    print("웹훅 URL 경로: /api/kakao")
    if GEMINI_API_KEY:
        print("✅ 구글 Gemini AI 엔진 작동 중 (매우 똑똑함 - REST API)")
    else:
        print("⚠️ Gemini API 키가 발견되지 않아 '기본 키워드 매칭 모드'로 작동 중입니다.")
        print("   (.env 파일에 GEMINI_API_KEY 를 넣어주세요)")
    print("==================================================")
    
    uvicorn.run(app, host="0.0.0.0", port=5055)
