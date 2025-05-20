"""문제 유효성 검증 클래스

이 모듈은 생성된 문제의 유효성을 검증합니다.
"""

from typing import Dict, List


class ProblemValidator:
    def is_valid(self, problem: dict) -> bool:
        """문제 데이터의 유효성을 검증합니다.

        Args:
            problem (dict): 검증할 문제 데이터

        Returns:
            bool: 유효성 검증 결과
        """
        # 필수 필드 존재 여부 확인
        required_fields = [
            "question",
            "correct_answer",
            "explanation",
            "hints",
            "wrong_answers",
        ]
        if not all(field in problem for field in required_fields):
            return False

        # 필드 타입 검증
        if not isinstance(problem["question"], str) or not problem["question"].strip():
            return False

        if (
            not isinstance(problem["correct_answer"], str)
            or not problem["correct_answer"].strip()
        ):
            return False

        if (
            not isinstance(problem["explanation"], str)
            or not problem["explanation"].strip()
        ):
            return False

        if not isinstance(problem["hints"], list) or not problem["hints"]:
            return False

        if (
            not isinstance(problem["wrong_answers"], list)
            or len(problem["wrong_answers"]) < 3
        ):
            return False

        # 힌트 유효성 검증
        if not all(isinstance(hint, str) and hint.strip() for hint in problem["hints"]):
            return False

        # 오답 유효성 검증
        if not all(
            isinstance(answer, str) and answer.strip()
            for answer in problem["wrong_answers"]
        ):
            return False

        # 정답과 오답이 중복되지 않는지 확인
        if problem["correct_answer"] in problem["wrong_answers"]:
            return False

        # 오답끼리 중복되지 않는지 확인
        if len(set(problem["wrong_answers"])) != len(problem["wrong_answers"]):
            return False

        return True

    def validate_difficulty(self, difficulty: str) -> bool:
        """난이도 값의 유효성을 검증합니다.

        Args:
            difficulty (str): 검증할 난이도 값

        Returns:
            bool: 유효성 검증 결과
        """
        valid_difficulties = ["easy", "medium", "hard"]
        return difficulty.lower() in valid_difficulties

    def validate_concept(self, concept: str) -> bool:
        """수학 개념의 유효성을 검증합니다.

        Args:
            concept (str): 검증할 수학 개념

        Returns:
            bool: 유효성 검증 결과
        """
        # 개념이 비어있지 않은지 확인
        if not concept or not concept.strip():
            return False

        # 개념에 특수문자가 포함되어 있지 않은지 확인
        import re

        if re.search(r"[^a-zA-Z0-9가-힣\s]", concept):
            return False

        return True
