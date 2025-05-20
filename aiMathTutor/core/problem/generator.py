"""문제 생성기 클래스

이 모듈은 OpenAI API를 사용하여 수학 문제를 생성합니다.
"""

import json
from typing import Dict, List, Optional
import openai
from ..openai.api_client import OpenAIClient
from .validator import ProblemValidator
from .formatter import ProblemFormatter


class ProblemGenerator:
    def __init__(self, openai_client: OpenAIClient):
        """
        Args:
            openai_client (OpenAIClient): OpenAI API 클라이언트
        """
        self.openai_client = openai_client
        self.validator = ProblemValidator()
        self.formatter = ProblemFormatter()

    async def generate_problem(self, concept: str, difficulty: str) -> Optional[dict]:
        """주어진 개념과 난이도에 맞는 수학 문제를 생성합니다.

        Args:
            concept (str): 수학 개념
            difficulty (str): 난이도 ('easy', 'medium', 'hard')

        Returns:
            Optional[dict]: 생성된 문제 데이터 또는 None
        """
        # 프롬프트 생성
        prompt = self._create_problem_prompt(concept, difficulty)

        try:
            # OpenAI API 호출
            response = await self.openai_client.generate_problem(prompt)

            # 응답 파싱 및 검증
            problem = self._parse_response(response)
            if not problem or not self.validator.is_valid(problem):
                return None

            # 문제 포맷팅
            formatted_problem = self.formatter.format(problem)
            formatted_problem.update({"concept": concept, "difficulty": difficulty})

            return formatted_problem

        except Exception as e:
            print(f"문제 생성 중 오류 발생: {str(e)}")
            return None

    def _create_problem_prompt(self, concept: str, difficulty: str) -> str:
        """문제 생성을 위한 프롬프트를 생성합니다.

        Args:
            concept (str): 수학 개념
            difficulty (str): 난이도

        Returns:
            str: 생성된 프롬프트
        """
        return f"""다음 조건에 맞는 수학 문제를 생성해주세요:
        
1. 개념: {concept}
2. 난이도: {difficulty}

다음 JSON 형식으로 응답해주세요:
{{
    "question": "문제 내용",
    "correct_answer": "정답",
    "explanation": "자세한 풀이 과정",
    "hints": ["힌트1", "힌트2"],
    "wrong_answers": ["오답1", "오답2", "오답3"]
}}"""

    def _parse_response(self, response: str) -> Optional[dict]:
        """API 응답을 파싱합니다.

        Args:
            response (str): API 응답 텍스트

        Returns:
            Optional[dict]: 파싱된 문제 데이터 또는 None
        """
        try:
            # JSON 응답에서 중괄호로 둘러싸인 부분 추출
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                return None

            json_str = response[start:end]
            problem_data = json.loads(json_str)

            # 필수 필드 확인
            required_fields = [
                "question",
                "correct_answer",
                "explanation",
                "hints",
                "wrong_answers",
            ]
            if not all(field in problem_data for field in required_fields):
                return None

            return problem_data

        except json.JSONDecodeError:
            return None
