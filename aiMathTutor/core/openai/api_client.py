"""OpenAI API 클라이언트 클래스

이 모듈은 OpenAI API를 호출하여 문제를 생성합니다.
"""

import os
from typing import Optional
import openai
from openai import AsyncOpenAI


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key (Optional[str]): OpenAI API 키. 없으면 환경 변수에서 가져옵니다.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")

        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_problem(self, prompt: str) -> str:
        """OpenAI API를 사용하여 문제를 생성합니다.

        Args:
            prompt (str): 문제 생성을 위한 프롬프트

        Returns:
            str: 생성된 문제 텍스트

        Raises:
            Exception: API 호출 중 오류 발생 시
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # 또는 다른 적절한 모델
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 수학 문제를 생성하는 AI 튜터입니다. "
                        "주어진 개념과 난이도에 맞는 문제를 생성하고, "
                        "정확한 JSON 형식으로 응답해야 합니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")

    async def validate_answer(self, problem: str, answer: str) -> bool:
        """OpenAI API를 사용하여 답안의 정확성을 검증합니다.

        Args:
            problem (str): 문제 텍스트
            answer (str): 검증할 답안

        Returns:
            bool: 답안의 정확성 여부

        Raises:
            Exception: API 호출 중 오류 발생 시
        """
        try:
            prompt = f"""다음 수학 문제의 답안이 정확한지 검증해주세요:

문제: {problem}
제출한 답안: {answer}

다음 JSON 형식으로 응답해주세요:
{{
    "is_correct": true/false,
    "explanation": "답안이 정확하거나 틀린 이유에 대한 설명"
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # 또는 다른 적절한 모델
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 수학 문제의 답안을 검증하는 AI 튜터입니다. "
                        "제출된 답안이 정확한지 판단하고, 그 이유를 설명해야 합니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            result = response.choices[0].message.content
            return result["is_correct"]

        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")

    async def generate_hint(self, problem: str, previous_hints: list) -> str:
        """OpenAI API를 사용하여 새로운 힌트를 생성합니다.

        Args:
            problem (str): 문제 텍스트
            previous_hints (list): 이전에 제공된 힌트 목록

        Returns:
            str: 생성된 힌트

        Raises:
            Exception: API 호출 중 오류 발생 시
        """
        try:
            previous_hints_text = "\n".join(f"- {hint}" for hint in previous_hints)
            prompt = f"""다음 수학 문제에 대한 새로운 힌트를 생성해주세요:

문제: {problem}

이전에 제공된 힌트:
{previous_hints_text}

이전 힌트와 중복되지 않고, 문제 해결에 도움이 되는 새로운 힌트를 생성해주세요.
힌트는 직접적인 답을 알려주지 않고, 문제 해결 방향을 제시해야 합니다."""

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # 또는 다른 적절한 모델
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 수학 문제 해결을 돕는 AI 튜터입니다. "
                        "학생이 스스로 문제를 해결할 수 있도록 적절한 힌트를 제공해야 합니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=200,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"OpenAI API 호출 중 오류 발생: {str(e)}")
