import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProblemRepository:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProblemRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """문제 저장소 초기화"""
        if not self._is_initialized:
            self.problems_dir = "data/problems"
            self.problems_file = os.path.join(
                self.problems_dir, "generated_problems.json"
            )
            self.history_file = os.path.join(self.problems_dir, "user_history.json")
            self.problems_by_concept = {}  # 개념별 문제 캐시
            self._ensure_files_exist()
            self._load_problems()
            self._is_initialized = True

    def _ensure_files_exist(self):
        """필요한 디렉토리와 파일이 존재하는지 확인하고 없으면 생성"""
        os.makedirs(self.problems_dir, exist_ok=True)

        # 문제 저장 파일 초기화
        if not os.path.exists(self.problems_file):
            self._save_problems([])

        # 사용자 히스토리 파일 초기화
        if not os.path.exists(self.history_file):
            self._save_history(
                {
                    "history": [],
                    "statistics": {},
                    "last_updated": datetime.now().isoformat(),
                }
            )

    def _save_history(self, data: Dict):
        """사용자 히스토리 저장"""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> Dict:
        """사용자 히스토리 불러오기"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"히스토리 불러오기 실패: {str(e)}")
            return {
                "history": [],
                "statistics": {},
                "last_updated": datetime.now().isoformat(),
            }

    def _save_problems(self, problems: List[Dict]):
        """문제 목록을 JSON 파일로 저장"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_problems": len(problems),
            "problems": problems,
        }
        with open(self.problems_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"문제 {len(problems)}개가 저장되었습니다.")

    def _load_problems(self):
        """저장된 문제 불러오기"""
        try:
            with open(self.problems_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                problems = data.get("problems", [])

                # 개념별로 문제 분류
                self.problems_by_concept = {}
                for problem in problems:
                    concept = problem.get("concept")
                    if concept:
                        if concept not in self.problems_by_concept:
                            self.problems_by_concept[concept] = []
                        self.problems_by_concept[concept].append(problem)

                logger.info(f"문제 {len(problems)}개를 불러왔습니다.")
                return problems
        except Exception as e:
            logger.error(f"문제 불러오기 실패: {str(e)}")
            return []

    def save_problem(self, problem: Dict) -> str:
        """새로운 문제를 저장하고 ID 반환"""
        try:
            # 기존 문제 불러오기
            problems = self._load_problems()

            # 문제 ID 및 생성 시간 추가
            if "id" not in problem:
                problem["id"] = str(len(problems) + 1).zfill(6)
            problem["created_at"] = datetime.now().isoformat()

            # 문제 추가 및 저장
            problems.append(problem)
            self._save_problems(problems)

            # 개념별 캐시 업데이트
            concept = problem.get("concept")
            if concept:
                if concept not in self.problems_by_concept:
                    self.problems_by_concept[concept] = []
                self.problems_by_concept[concept].append(problem)

            logger.info(f"새로운 문제가 저장되었습니다. ID: {problem['id']}")
            return problem["id"]
        except Exception as e:
            logger.error(f"문제 저장 실패: {str(e)}")
            raise

    def get_problem_by_id(self, problem_id: str) -> Optional[Dict]:
        """ID로 문제 검색"""
        problems = self._load_problems()
        for problem in problems:
            if problem.get("id") == problem_id:
                return problem
        return None

    def get_problems_by_concept(self, concept: str) -> List[Dict]:
        """특정 개념의 모든 문제 반환"""
        return self.problems_by_concept.get(concept, [])

    def get_problems_by_difficulty(self, difficulty: str) -> List[Dict]:
        """특정 난이도의 모든 문제 반환"""
        problems = self._load_problems()
        return [p for p in problems if p.get("difficulty") == difficulty]

    def get_recent_problems(self, limit: int = 10) -> List[Dict]:
        """최근 생성된 문제 반환"""
        problems = self._load_problems()
        sorted_problems = sorted(
            problems, key=lambda x: x.get("created_at", ""), reverse=True
        )
        return sorted_problems[:limit]

    def delete_problem(self, problem_id: str) -> bool:
        """문제 삭제"""
        try:
            problems = self._load_problems()
            filtered_problems = [p for p in problems if p.get("id") != problem_id]

            if len(filtered_problems) < len(problems):
                self._save_problems(filtered_problems)

                # 개념별 캐시 업데이트
                for concept in self.problems_by_concept:
                    self.problems_by_concept[concept] = [
                        p
                        for p in self.problems_by_concept[concept]
                        if p.get("id") != problem_id
                    ]

                logger.info(f"문제가 삭제되었습니다. ID: {problem_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"문제 삭제 실패: {str(e)}")
            return False

    def get_statistics(self) -> Dict:
        """문제 저장소 통계 정보"""
        problems = self._load_problems()

        stats = {
            "total_problems": len(problems),
            "problems_by_concept": {},
            "problems_by_difficulty": {},
            "last_updated": datetime.now().isoformat(),
        }

        for problem in problems:
            # 개념별 통계
            concept = problem.get("concept")
            if concept:
                if concept not in stats["problems_by_concept"]:
                    stats["problems_by_concept"][concept] = 0
                stats["problems_by_concept"][concept] += 1

            # 난이도별 통계
            difficulty = problem.get("difficulty")
            if difficulty:
                if difficulty not in stats["problems_by_difficulty"]:
                    stats["problems_by_difficulty"][difficulty] = 0
                stats["problems_by_difficulty"][difficulty] += 1

        return stats

    def save_user_attempt(
        self, user_id: str, problem_id: str, is_correct: bool, answer: str
    ):
        """사용자의 문제 풀이 시도 저장"""
        try:
            history_data = self._load_history()

            # 새로운 시도 기록
            attempt = {
                "user_id": user_id,
                "problem_id": problem_id,
                "is_correct": is_correct,
                "answer": answer,
                "timestamp": datetime.now().isoformat(),
            }
            history_data["history"].append(attempt)

            # 통계 업데이트
            if user_id not in history_data["statistics"]:
                history_data["statistics"][user_id] = {
                    "total_attempts": 0,
                    "correct_answers": 0,
                    "problems_attempted": set(),
                    "last_attempt": None,
                }

            stats = history_data["statistics"][user_id]
            stats["total_attempts"] += 1
            if is_correct:
                stats["correct_answers"] += 1
            stats["problems_attempted"] = list(
                set(stats["problems_attempted"]).union({problem_id})
            )
            stats["last_attempt"] = datetime.now().isoformat()

            # 저장
            history_data["last_updated"] = datetime.now().isoformat()
            self._save_history(history_data)
            logger.info(f"사용자 {user_id}의 문제 풀이 시도가 저장되었습니다.")

        except Exception as e:
            logger.error(f"사용자 시도 저장 실패: {str(e)}")
            raise

    def get_user_statistics(self, user_id: str) -> Dict:
        """사용자의 문제 풀이 통계 조회"""
        try:
            history_data = self._load_history()
            stats = history_data["statistics"].get(
                user_id,
                {
                    "total_attempts": 0,
                    "correct_answers": 0,
                    "problems_attempted": [],
                    "last_attempt": None,
                },
            )

            # 정답률 계산
            accuracy = (
                (stats["correct_answers"] / stats["total_attempts"] * 100)
                if stats["total_attempts"] > 0
                else 0
            )

            return {
                "total_attempts": stats["total_attempts"],
                "correct_answers": stats["correct_answers"],
                "accuracy": round(accuracy, 2),
                "unique_problems": len(stats["problems_attempted"]),
                "last_attempt": stats["last_attempt"],
            }

        except Exception as e:
            logger.error(f"사용자 통계 조회 실패: {str(e)}")
            return {
                "total_attempts": 0,
                "correct_answers": 0,
                "accuracy": 0,
                "unique_problems": 0,
                "last_attempt": None,
            }

    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """사용자의 최근 문제 풀이 기록 조회"""
        try:
            history_data = self._load_history()
            user_attempts = [
                attempt
                for attempt in history_data["history"]
                if attempt["user_id"] == user_id
            ]

            # 최신 순으로 정렬
            sorted_attempts = sorted(
                user_attempts, key=lambda x: x["timestamp"], reverse=True
            )

            # 문제 정보 추가
            result = []
            for attempt in sorted_attempts[:limit]:
                problem = self.get_problem_by_id(attempt["problem_id"])
                if problem:
                    result.append({**attempt, "problem": problem})

            return result

        except Exception as e:
            logger.error(f"사용자 히스토리 조회 실패: {str(e)}")
            return []
