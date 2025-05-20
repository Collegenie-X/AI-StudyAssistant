"""OpenAI 기반 문제 생성기

knowledge_map.json의 개념 구조를 활용하여 맞춤형 문제를 생성합니다.
"""

import json
import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv


class OpenAIProblemGenerator:
    def __init__(self, data_dir: str = "data"):
        """OpenAI 문제 생성기를 초기화합니다.

        Args:
            data_dir (str): 데이터 디렉토리 경로
        """
        # 환경 변수 로드
        load_dotenv()

        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API 키가 설정되지 않았습니다. "
                ".env 파일에 OPENAI_API_KEY를 설정하거나 "
                "환경 변수로 지정해주세요."
            )

        self.knowledge_map_file = os.path.join(data_dir, "knowledge_map.json")
        self.knowledge_map = self._load_knowledge_map()
        self.client = OpenAI(api_key=api_key)  # API 키로 클라이언트 초기화

    def _load_knowledge_map(self) -> dict:
        """지식 맵을 로드합니다."""
        try:
            with open(self.knowledge_map_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("knowledge_map.json 파일을 찾을 수 없습니다.")

    def _get_concept_details(self, concept_id: str) -> Optional[Dict]:
        """개념 ID에 해당하는 상세 정보를 조회합니다."""
        for domain in self.knowledge_map["domains"]:
            for unit in domain["units"]:
                for concept in unit["concepts"]:
                    if concept["id"] == concept_id:
                        return {
                            "domain": domain["name"],
                            "unit": unit["name"],
                            "concept": concept["name"],
                            "description": concept["description"],
                            "prerequisites": concept["prerequisites"],
                            "difficulty_levels": concept["difficulty_levels"],
                        }
        return None

    def _get_prerequisite_concepts(self, concept_id: str) -> List[Dict]:
        """선수 개념들의 정보를 조회합니다."""
        concept_details = self._get_concept_details(concept_id)
        if not concept_details:
            return []

        prereq_concepts = []
        for prereq_id in concept_details["prerequisites"]:
            prereq_details = self._get_concept_details(prereq_id)
            if prereq_details:
                prereq_concepts.append(prereq_details)
        return prereq_concepts

    def generate_problem(self, concept_id: str, difficulty: str) -> dict:
        """주어진 개념과 난이도에 맞는 문제를 생성합니다.

        Args:
            concept_id (str): 개념 ID
            difficulty (str): 난이도 ('상', '중', '하')

        Returns:
            dict: 생성된 문제 정보
        """
        # 개념 정보 조회
        concept_details = self._get_concept_details(concept_id)
        if not concept_details:
            raise ValueError(f"개념 ID {concept_id}를 찾을 수 없습니다.")

        # 선수 개념 정보 조회
        prereq_concepts = self._get_prerequisite_concepts(concept_id)

        # 프롬프트 구성
        prompt = self._create_problem_prompt(
            concept_details, difficulty, prereq_concepts
        )

        # OpenAI API 호출
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 수학 교육 전문가입니다. 학생의 수준과 교육과정에 맞는 최적의 문제를 생성해주세요.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            # 응답 파싱 및 반환
            problem_data = self._parse_response(response.choices[0].message.content)
            problem_data.update(
                {
                    "concept": concept_details["concept"],
                    "difficulty": difficulty,
                    "domain": concept_details["domain"],
                    "unit": concept_details["unit"],
                }
            )
            return problem_data

        except Exception as e:
            raise Exception(f"문제 생성 중 오류 발생: {str(e)}")

    def _create_problem_prompt(
        self, concept_details: Dict, difficulty: str, prereq_concepts: List[Dict]
    ) -> str:
        """문제 생성을 위한 프롬프트를 생성합니다."""
        prompt = f"""다음 조건에 맞는 수학 문제를 생성해주세요:

1. 학습 개념:
   - 도메인: {concept_details['domain']}
   - 단원: {concept_details['unit']}
   - 개념: {concept_details['concept']}
   - 개념 설명: {concept_details['description']}

2. 난이도: {difficulty}

3. 선수 개념:
"""
        if prereq_concepts:
            for prereq in prereq_concepts:
                prompt += f"   - {prereq['concept']}: {prereq['description']}\n"
        else:
            prompt += "   - 선수 개념 없음\n"

        prompt += """
4. 요구사항:
   - 객관식 4지선다 문제로 생성
   - 실생활 연계 문제 포함
   - 명확한 해설 제공
   - 오답 보기에 대한 설명 포함
   - 난이도에 맞는 적절한 계산량과 복잡도 조절

5. 문제 유형 가이드라인:
   - '하' 난이도: 기본 개념 이해도 확인, 단순 계산 위주
   - '중' 난이도: 개념 응용력 확인, 2-3단계 문제 해결
   - '상' 난이도: 심화 개념 적용, 복합적 문제 해결 능력 평가

다음 JSON 형식으로 응답해주세요:
{
    "question": "문제 내용",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "correct_answer": 정답번호(1-4),
    "explanation": "상세한 해설",
    "next_problems": {
        "similar": {"concept": "개념ID", "difficulty": "난이도"},
        "harder": {"concept": "개념ID", "difficulty": "난이도"},
        "related": {"concept": "개념ID", "difficulty": "난이도"}
    }
}"""

        return prompt

    def _parse_response(self, response_text: str) -> dict:
        """API 응답을 파싱하여 문제 데이터로 변환합니다."""
        try:
            # JSON 응답 파싱
            problem_data = json.loads(response_text)

            # 필수 필드 검증
            required_fields = ["question", "options", "correct_answer", "explanation"]
            for field in required_fields:
                if field not in problem_data:
                    raise ValueError(f"응답에서 필수 필드 {field}를 찾을 수 없습니다.")

            return problem_data

        except json.JSONDecodeError:
            raise ValueError("API 응답을 JSON으로 파싱할 수 없습니다.")
        except Exception as e:
            raise Exception(f"응답 파싱 중 오류 발생: {str(e)}")
