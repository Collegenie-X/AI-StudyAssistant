"""문제 포맷 변환 클래스

이 모듈은 생성된 문제의 포맷을 변환합니다.
"""

from typing import Dict, List
import re


class ProblemFormatter:
    def format(self, problem: dict) -> dict:
        """문제 데이터의 포맷을 변환합니다.

        Args:
            problem (dict): 변환할 문제 데이터

        Returns:
            dict: 변환된 문제 데이터
        """
        formatted = {
            "question": self._format_question(problem["question"]),
            "correct_answer": self._format_answer(problem["correct_answer"]),
            "explanation": self._format_explanation(problem["explanation"]),
            "hints": [self._format_hint(hint) for hint in problem["hints"]],
            "wrong_answers": [
                self._format_answer(answer) for answer in problem["wrong_answers"]
            ],
        }

        # 추가 필드가 있다면 복사
        for key, value in problem.items():
            if key not in formatted:
                formatted[key] = value

        return formatted

    def _format_question(self, question: str) -> str:
        """문제 텍스트를 포맷팅합니다.

        Args:
            question (str): 원본 문제 텍스트

        Returns:
            str: 포맷팅된 문제 텍스트
        """
        # 앞뒤 공백 제거
        question = question.strip()

        # 문제 번호가 있다면 제거
        question = re.sub(r"^\d+[\.\)]?\s*", "", question)

        # 여러 줄의 공백을 하나로 통일
        question = re.sub(r"\s+", " ", question)

        # 문장 끝에 마침표가 없다면 추가
        if not question.endswith((".", "?", "!")):
            question += "."

        return question

    def _format_answer(self, answer: str) -> str:
        """답안을 포맷팅합니다.

        Args:
            answer (str): 원본 답안

        Returns:
            str: 포맷팅된 답안
        """
        # 앞뒤 공백 제거
        answer = answer.strip()

        # 답안 번호가 있다면 제거
        answer = re.sub(r"^\d+[\.\)]?\s*", "", answer)

        # 불필요한 공백 제거
        answer = re.sub(r"\s+", " ", answer)

        return answer

    def _format_explanation(self, explanation: str) -> str:
        """풀이 과정을 포맷팅합니다.

        Args:
            explanation (str): 원본 풀이 과정

        Returns:
            str: 포맷팅된 풀이 과정
        """
        # 앞뒤 공백 제거
        explanation = explanation.strip()

        # 단계 번호 포맷 통일
        explanation = re.sub(r"^\d+[\.\)]?\s*", "", explanation)
        explanation = re.sub(r"\n\s*\d+[\.\)]?\s*", "\n", explanation)

        # 여러 줄의 공백을 하나로 통일
        explanation = re.sub(r"\n\s*\n", "\n", explanation)

        return explanation

    def _format_hint(self, hint: str) -> str:
        """힌트를 포맷팅합니다.

        Args:
            hint (str): 원본 힌트

        Returns:
            str: 포맷팅된 힌트
        """
        # 앞뒤 공백 제거
        hint = hint.strip()

        # 힌트 번호가 있다면 제거
        hint = re.sub(r"^\d+[\.\)]?\s*", "", hint)

        # 불필요한 공백 제거
        hint = re.sub(r"\s+", " ", hint)

        # 문장 끝에 마침표가 없다면 추가
        if not hint.endswith((".", "?", "!")):
            hint += "."

        return hint
