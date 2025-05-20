"""문제 저장소 관리 클래스

이 모듈은 생성된 문제와 사용자 풀이 기록을 관리합니다.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class ProblemRepository:
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir (str): 데이터 저장 디렉토리 경로
        """
        self.data_dir = data_dir
        self.problems_file = os.path.join(data_dir, "generated_problems.json")
        self.history_file = os.path.join(data_dir, "user_history.json")

        # 디렉토리와 파일 존재 확인 및 생성
        os.makedirs(data_dir, exist_ok=True)
        self._initialize_files()

    def _initialize_files(self) -> None:
        """필요한 JSON 파일들을 초기화합니다."""
        if not os.path.exists(self.problems_file):
            self._save_json(self.problems_file, {"problems": []})
        if not os.path.exists(self.history_file):
            self._save_json(self.history_file, {"history": []})

    def _load_json(self, file_path: str) -> dict:
        """JSON 파일을 로드합니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return (
                {"problems": []} if file_path == self.problems_file else {"history": []}
            )

    def _save_json(self, file_path: str, data: dict) -> None:
        """JSON 파일을 저장합니다."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_problem(self, problem: dict) -> str:
        """새로운 문제를 저장합니다.

        Args:
            problem (dict): 저장할 문제 데이터

        Returns:
            str: 생성된 문제 ID
        """
        data = self._load_json(self.problems_file)

        # 문제 ID 생성
        problem_id = f"prob_{len(data['problems']) + 1}"
        problem["id"] = problem_id
        problem["created_at"] = datetime.now().isoformat()

        data["problems"].append(problem)
        self._save_json(self.problems_file, data)

        return problem_id

    def save_solution_history(self, history_entry: dict) -> None:
        """사용자의 문제 풀이 기록을 저장합니다.

        Args:
            history_entry (dict): 저장할 풀이 기록 데이터
        """
        data = self._load_json(self.history_file)

        history_entry["timestamp"] = datetime.now().isoformat()
        data["history"].append(history_entry)

        self._save_json(self.history_file, data)

    def get_user_stats(self, user_id: str) -> dict:
        """사용자의 풀이 통계를 계산합니다.

        Args:
            user_id (str): 사용자 ID

        Returns:
            dict: 사용자 통계 정보
        """
        data = self._load_json(self.history_file)
        user_history = [h for h in data["history"] if h["user_id"] == user_id]

        total_attempts = len(user_history)
        correct_answers = len([h for h in user_history if h["is_correct"]])
        unique_problems = len(set(h["problem_id"] for h in user_history))

        accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0

        return {
            "total_attempts": total_attempts,
            "correct_answers": correct_answers,
            "unique_problems_solved": unique_problems,
            "accuracy_rate": round(accuracy, 2),
        }

    def get_problem_by_id(self, problem_id: str) -> Optional[dict]:
        """ID로 문제를 조회합니다.

        Args:
            problem_id (str): 문제 ID

        Returns:
            Optional[dict]: 문제 데이터 또는 None
        """
        data = self._load_json(self.problems_file)
        for problem in data["problems"]:
            if problem["id"] == problem_id:
                return problem
        return None

    def get_user_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """사용자의 최근 풀이 기록을 조회합니다.

        Args:
            user_id (str): 사용자 ID
            limit (int): 조회할 기록 수

        Returns:
            List[dict]: 풀이 기록 목록
        """
        data = self._load_json(self.history_file)
        user_history = [h for h in data["history"] if h["user_id"] == user_id]

        # 최신 기록순으로 정렬
        user_history.sort(key=lambda x: x["timestamp"], reverse=True)

        return user_history[:limit]
