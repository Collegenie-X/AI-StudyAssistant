import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class ProblemRepository:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProblemRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.problems_file = "data/problems/problem_bank.json"
            self.cache_file = "data/problems/problem_cache.json"
            self.history_file = "data/problems/problem_history.json"
            self._ensure_files_exist()
            self._is_initialized = True

    def _ensure_files_exist(self):
        """필요한 JSON 파일들이 존재하는지 확인하고 없으면 생성"""
        files = {
            self.problems_file: {"problems": [], "last_updated": ""},
            self.cache_file: {"cached_problems": {}, "last_accessed": ""},
            self.history_file: {"problem_history": [], "statistics": {}},
        }

        for file_path, initial_data in files.items():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)

    def save_problem(self, problem: Dict) -> str:
        """새로운 문제를 저장하고 ID 반환"""
        with open(self.problems_file, "r+", encoding="utf-8") as f:
            data = json.load(f)
            problem_id = str(len(data["problems"]) + 1).zfill(6)
            problem["id"] = problem_id
            problem["created_at"] = datetime.now().isoformat()
            data["problems"].append(problem)
            data["last_updated"] = datetime.now().isoformat()
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
        return problem_id

    def get_problem(self, problem_id: str) -> Optional[Dict]:
        """ID로 문제 조회"""
        with open(self.problems_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for problem in data["problems"]:
                if problem["id"] == problem_id:
                    return problem
        return None

    def get_problems_by_concept(self, concept: str, difficulty: str) -> List[Dict]:
        """개념과 난이도로 문제 검색"""
        with open(self.problems_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [
                p
                for p in data["problems"]
                if p["concept"].lower() == concept.lower()
                and p["difficulty"].lower() == difficulty.lower()
            ]

    def save_to_cache(self, key: str, problem: Dict):
        """문제를 캐시에 저장"""
        with open(self.cache_file, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["cached_problems"][key] = problem
            data["last_accessed"] = datetime.now().isoformat()
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

    def get_from_cache(self, key: str) -> Optional[Dict]:
        """캐시에서 문제 조회"""
        with open(self.cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["cached_problems"].get(key)

    def save_problem_history(self, user_id: str, problem_id: str, is_correct: bool):
        """문제 풀이 이력 저장"""
        with open(self.history_file, "r+", encoding="utf-8") as f:
            data = json.load(f)
            history_entry = {
                "user_id": user_id,
                "problem_id": problem_id,
                "is_correct": is_correct,
                "timestamp": datetime.now().isoformat(),
            }
            data["problem_history"].append(history_entry)

            # 통계 업데이트
            if user_id not in data["statistics"]:
                data["statistics"][user_id] = {"total": 0, "correct": 0}
            data["statistics"][user_id]["total"] += 1
            if is_correct:
                data["statistics"][user_id]["correct"] += 1

            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

    def get_user_statistics(self, user_id: str) -> Dict:
        """사용자의 문제 풀이 통계 조회"""
        with open(self.history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["statistics"].get(user_id, {"total": 0, "correct": 0})
