import json
import random
import uuid
from typing import List, Dict
from .embeddings import ProblemEmbedding


class ProblemGenerator:
    def __init__(self):
        """RAG 기반 문제 생성기 초기화"""
        self.embedding_model = ProblemEmbedding()
        self.load_problem_database()
        self.current_difficulty = "중"

    def load_problem_database(self):
        """문제 데이터베이스 로드"""
        try:
            with open(
                "data/problems/fifth_grade_problems_all_english_v2.json",
                "r",
                encoding="utf-8",
            ) as f:
                self.problems = json.load(f)["problems"]
        except FileNotFoundError:
            self.problems = []

    def find_similar_problems(
        self, concept: str, difficulty: str, top_k: int = 3
    ) -> List[Dict]:
        """
        개념과 난이도에 맞는 유사 문제 검색
        Args:
            concept (str): 수학 개념
            difficulty (str): 난이도
            top_k (int): 검색할 유사 문제 수
        Returns:
            List[Dict]: 유사 문제 목록
        """
        filtered_problems = [
            p
            for p in self.problems
            if p["concept"].lower() == concept.lower()
            and p["difficulty"].lower() == difficulty.lower()
        ]

        if not filtered_problems:
            return []

        return random.sample(filtered_problems, min(top_k, len(filtered_problems)))

    def modify_problem(self, base_problem: Dict) -> Dict:
        """
        기존 문제를 변형하여 새로운 객관식 문제 생성
        Args:
            base_problem (Dict): 기준이 되는 문제
        Returns:
            Dict: 변형된 새로운 문제
        """
        modified_problem = base_problem.copy()

        # 문제 텍스트에서 숫자 추출 및 변경
        numbers = [int(n) for n in str(base_problem["text"]).split() if n.isdigit()]
        if numbers:
            for num in numbers:
                modified_num = num + random.randint(-5, 5)
                modified_problem["text"] = modified_problem["text"].replace(
                    str(num), str(modified_num)
                )

        # 객관식 보기 생성
        correct_answer = int(modified_problem.get("answer", "0"))
        options = self._generate_options(correct_answer)

        return {
            "text": modified_problem["text"],
            "options": options,
            "correct_answer": 1,  # 정답은 항상 첫 번째 보기로 설정
            "solution": modified_problem.get("solution", ""),
        }

    def _generate_options(self, correct_answer: int) -> List[str]:
        """객관식 보기 생성"""
        options = [str(correct_answer)]  # 정답을 첫 번째 보기로

        # 오답 생성
        while len(options) < 4:
            wrong_answer = correct_answer + random.randint(-10, 10)
            if wrong_answer != correct_answer and str(wrong_answer) not in options:
                options.append(str(wrong_answer))

        return options

    def generate_problem(self, concept: str, difficulty: str) -> Dict:
        """
        주어진 개념과 난이도에 맞는 객관식 문제 생성
        Args:
            concept (str): 수학 개념
            difficulty (str): 난이도
        Returns:
            Dict: 생성된 문제 정보
        """
        similar_problems = self.find_similar_problems(concept, difficulty)

        if not similar_problems:
            return {
                "id": str(uuid.uuid4()),  # UUID 기반 문제 ID 추가
                "question": f"죄송합니다. {concept} 개념의 {difficulty} 난이도 문제를 찾을 수 없습니다.",
                "options": [],
                "correct_answer": None,
                "explanation": "",
                "concept": concept,
                "difficulty": difficulty,
                "next_problems": self._generate_next_problems(concept, difficulty),
            }

        base_problem = random.choice(similar_problems)
        modified_problem = self.modify_problem(base_problem)

        return {
            "id": str(uuid.uuid4()),  # UUID 기반 문제 ID 추가
            "question": modified_problem["text"],
            "options": modified_problem["options"],
            "correct_answer": modified_problem["correct_answer"],
            "explanation": modified_problem.get("solution", "해설 정보가 없습니다."),
            "concept": concept,
            "difficulty": difficulty,
            "next_problems": self._generate_next_problems(concept, difficulty),
        }

    def _generate_next_problems(self, concept: str, current_difficulty: str) -> Dict:
        """다음 문제 옵션 생성"""
        difficulties = {"하": 0, "중": 1, "상": 2}
        current_level = difficulties.get(current_difficulty, 1)

        return {
            "similar": {
                "concept": concept,
                "difficulty": current_difficulty,
                "description": "비슷한 유형의 문제로 연습하기",
            },
            "harder": {
                "concept": concept,
                "difficulty": list(difficulties.keys())[min(current_level + 1, 2)],
                "description": "더 어려운 문제에 도전하기",
            },
            "related": {
                "concept": self._get_related_concept(concept),
                "difficulty": current_difficulty,
                "description": "관련된 다른 개념 학습하기",
            },
        }

    def _get_related_concept(self, concept: str) -> str:
        """관련 개념 반환"""
        concept_relations = {
            "최대공약수": ["최소공배수", "약수"],
            "최소공배수": ["최대공약수", "배수"],
            "약수 구하기": ["최대공약수", "소수"],
            "소수 판별": ["약수 구하기", "소인수분해"],
        }
        related = concept_relations.get(concept, [])
        return random.choice(related) if related else concept
