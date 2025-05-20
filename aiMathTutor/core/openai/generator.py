from openai import OpenAI
import os
import random
from typing import Dict, List
from dotenv import load_dotenv
import streamlit as st
import json
import uuid
import logging
from ..problem.problem_repository import ProblemRepository

logger = logging.getLogger(__name__)


class OpenAIProblemGenerator:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIProblemGenerator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """OpenAI API를 사용하여 문제를 생성하는 클래스"""
        if not self._is_initialized:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요."
                )
            self.client = OpenAI(api_key=api_key)
            self.cache = {}  # 문제 캐시
            self.repository = ProblemRepository()  # 문제 저장소 초기화
            self._is_initialized = True

    def _generate_problem_id(self) -> str:
        """UUID를 사용하여 고유한 문제 ID 생성"""
        return str(uuid.uuid4())

    def generate_problem(self, concept: str, difficulty: str) -> dict:
        """수학 문제 생성"""
        try:
            # 문제 유형 및 변형 패턴 정의
            problem_patterns = {
                "최대공약수": [
                    "두 수의 최대공약수 찾기",
                    "여러 물건을 동일하게 나누기",
                    "공통 약수 중 가장 큰 수 찾기",
                    "실생활 응용 문제",
                ],
                "최소공배수": [
                    "두 수의 최소공배수 찾기",
                    "주기가 다른 상황의 일치 시점 찾기",
                    "공통 배수 중 가장 작은 수 찾기",
                    "실생활 응용 문제",
                ],
                "약수 구하기": [
                    "한 수의 모든 약수 찾기",
                    "약수의 개수 구하기",
                    "약수의 합 구하기",
                    "실생활 응용 문제",
                ],
                "소수 판별": [
                    "주어진 수가 소수인지 판별하기",
                    "소수의 성질 이해하기",
                    "소인수분해를 통한 소수 관계 이해",
                    "실생활 응용 문제",
                ],
            }

            # 난이도별 변형 요소
            difficulty_variations = {
                "하": {
                    "숫자_범위": "1~50",
                    "계산_단계": "1~2단계",
                    "문제_유형": "기본 개념 이해",
                },
                "중": {
                    "숫자_범위": "1~100",
                    "계산_단계": "2~3단계",
                    "문제_유형": "개념 응용",
                },
                "상": {
                    "숫자_범위": "1~1000",
                    "계산_단계": "3단계 이상",
                    "문제_유형": "복합 개념 활용",
                },
            }

            # 선택된 패턴과 변형 요소
            selected_pattern = random.choice(
                problem_patterns.get(concept, ["기본 문제"])
            )
            diff_var = difficulty_variations.get(
                difficulty, difficulty_variations["중"]
            )

            # knowledge_map.json에서 문제 유형 가져오기
            try:
                with open(
                    "data/knowledge_base/knowledge_map.json", "r", encoding="utf-8"
                ) as f:
                    knowledge_map = json.load(f)
                    for domain in knowledge_map:
                        if "concept" in domain and domain["concept"] == concept:
                            if "problem" in domain:
                                problem_types = [
                                    p["question"] for p in domain["problem"].values()
                                ]
                                if problem_types:
                                    selected_pattern = random.choice(problem_types)
            except Exception as e:
                logger.error(f"knowledge_map.json 로드 중 오류 발생: {str(e)}")
                # knowledge_map.json 로드 실패 시 기본 패턴 사용

            prompt = f"""
            다음 조건에 맞는 초등학교 수학 객관식 문제를 생성해주세요.
            이전에 생성된 문제와 다른 새로운 유형의 문제를 만들어주세요.
            JSON 형식으로 응답해주세요.

            조건:
            - 개념: {concept}
            - 난이도: {difficulty}
            - 문제 패턴: {selected_pattern}
            - 숫자 범위: {diff_var['숫자_범위']}
            - 계산 단계: {diff_var['계산_단계']}
            - 문제 유형: {diff_var['문제_유형']}
            
            추가 요구사항:
            1. 실생활과 연관된 흥미로운 상황을 포함해주세요.
            2. 문제에 사용되는 숫자는 매번 다르게 생성해주세요.
            3. 문제 해설은 단계별로 자세히 설명해주세요.
            4. 오답도 교육적 가치가 있는 것으로 선택해주세요.
            
            다음 JSON 형식으로 정확히 응답해주세요:
            {{
                "question": "실생활 상황이 포함된 문제 내용",
                "options": [
                    "1번 보기",
                    "2번 보기",
                    "3번 보기",
                    "4번 보기"
                ],
                "correct_answer": 정답 번호(1~4),
                "explanation": "단계별 자세한 해설",
                "concept": "{concept}",
                "difficulty": "{difficulty}",
                "pattern": "{selected_pattern}"
            }}
            """

            logger.info(f"OpenAI API 호출 시작 - 개념: {concept}, 난이도: {difficulty}")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates math problems. Always respond in JSON format.",
                    },
                    {
                        "role": "user",
                        "content": "Please generate a response in JSON format following the structure below.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            logger.info("OpenAI API 호출 완료")

            # JSON 파싱
            try:
                result = json.loads(response.choices[0].message.content)
                logger.info("OpenAI 응답 JSON 파싱 성공")
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {str(e)}")
                raise ValueError("OpenAI 응답을 JSON으로 파싱할 수 없습니다.")

            # 필수 필드 검증
            required_fields = ["question", "options", "correct_answer", "explanation"]
            for field in required_fields:
                if field not in result:
                    logger.error(f"필수 필드 누락: {field}")
                    raise ValueError(
                        f"생성된 문제에 필수 필드가 누락되었습니다: {field}"
                    )

            # correct_answer 유효성 검증
            if not isinstance(result["correct_answer"], int) or not (
                1 <= result["correct_answer"] <= 4
            ):
                logger.error(f"잘못된 correct_answer 값: {result['correct_answer']}")
                raise ValueError("correct_answer는 1부터 4까지의 정수여야 합니다.")

            # options 길이 검증
            if not isinstance(result["options"], list) or len(result["options"]) != 4:
                logger.error(f"잘못된 options 길이: {len(result.get('options', []))}")
                raise ValueError("options는 정확히 4개의 선택지를 포함해야 합니다.")

            # UUID 기반 문제 ID 추가
            result["id"] = self._generate_problem_id()

            # 캐시에 문제 저장
            self.cache[result["id"]] = result

            # 문제 저장소에 저장
            try:
                self.repository.save_problem(result)
                logger.info(f"문제가 저장소에 저장되었습니다. ID: {result['id']}")
            except Exception as e:
                logger.error(f"문제 저장소 저장 실패: {str(e)}")

            return result

        except Exception as e:
            logger.error(f"문제 생성 중 예외 발생: {str(e)}")
            return {
                "id": self._generate_problem_id(),
                "question": "문제 생성 중 오류가 발생했습니다.",
                "options": ["오류가 발생했습니다"] * 4,
                "correct_answer": 1,
                "explanation": f"죄송합니다. 문제 생성 중 오류가 발생했습니다. 다시 시도해주세요. (오류: {str(e)})",
                "concept": concept,
                "difficulty": difficulty,
            }
