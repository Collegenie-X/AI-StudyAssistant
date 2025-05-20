"""
문제 생성을 위한 메인 생성기 모듈
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
import random
import uuid

from .templates.gcd_template import GCDProblemTemplate


class ProblemGenerator:
    def __init__(self, knowledge_map_path: str):
        """
        문제 생성기 초기화

        Args:
            knowledge_map_path: knowledge_map.json 파일의 경로
        """
        self.knowledge_map = self._load_knowledge_map(knowledge_map_path)
        self.templates = {"Greatest Common Divisor": GCDProblemTemplate()}

    def _load_knowledge_map(self, path: str) -> Dict:
        """knowledge_map.json 파일 로드"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_concept_info(self, concept: str) -> Optional[Dict]:
        """주어진 개념에 대한 정보 조회"""
        for item in self.knowledge_map:
            if item.get("concept") == concept:
                return item
        return None

    def _generate_problem_id(self) -> str:
        """UUID를 사용하여 고유한 문제 ID 생성"""
        return str(uuid.uuid4())

    def generate_problem(
        self, concept: str, difficulty: str = "medium", problem_type: str = None
    ) -> Dict:
        """
        주어진 개념과 난이도에 맞는 문제 생성

        Args:
            concept: 문제를 생성할 수학 개념
            difficulty: 문제 난이도 ('easy', 'medium', 'hard')
            problem_type: 문제 유형 (None인 경우 랜덤 선택)

        Returns:
            생성된 문제 딕셔너리
        """
        concept_info = self._get_concept_info(concept)
        if not concept_info:
            raise ValueError(f"Unknown concept: {concept}")

        # 템플릿 가져오기
        template = self.templates.get(concept)
        if not template:
            raise ValueError(f"No template available for concept: {concept}")

        # 문제 유형 선택
        if not problem_type and "problem_types" in concept_info:
            problem_type = random.choice(concept_info["problem_types"])

        # 문제 생성
        problem = template.generate_problem(difficulty)

        # 메타데이터 추가
        problem["metadata"] = {
            "concept": concept,
            "difficulty": difficulty,
            "type": problem_type,
        }

        # UUID 기반 문제 ID 추가
        problem["id"] = self._generate_problem_id()

        return problem

    def generate_similar_problem(
        self, original_problem: Dict, variation_type: str = "numbers"
    ) -> Dict:
        """
        기존 문제와 유사한 새로운 문제 생성

        Args:
            original_problem: 원본 문제 딕셔너리
            variation_type: 변형 유형 ('numbers', 'scale', 'context')

        Returns:
            생성된 유사 문제 딕셔너리
        """
        concept = original_problem.get("metadata", {}).get("concept")
        if not concept:
            raise ValueError("Original problem missing concept metadata")

        template = self.templates.get(concept)
        if not template:
            raise ValueError(f"No template available for concept: {concept}")

        problem = template.generate_similar_problem(original_problem, variation_type)

        # UUID 기반 문제 ID 추가
        problem["id"] = self._generate_problem_id()

        return problem

    def get_related_concepts(self, concept: str) -> List[str]:
        """
        주어진 개념과 관련된 개념들 반환

        Args:
            concept: 기준 개념

        Returns:
            관련 개념 리스트
        """
        concept_info = self._get_concept_info(concept)
        if not concept_info:
            return []

        related = concept_info.get("related", [])
        parent = concept_info.get("parent")
        children = concept_info.get("child", [])

        all_related = set(related)
        if parent:
            all_related.add(parent)
        all_related.update(children)

        return list(all_related)
