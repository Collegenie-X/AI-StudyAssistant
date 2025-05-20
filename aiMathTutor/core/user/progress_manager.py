"""User Progress Manager

This module manages user progress data and learning achievements.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class UserProgressManager:
    def __init__(self, data_dir: str = "data"):
        """Initialize the user progress manager.

        Args:
            data_dir (str): Directory for storing progress data
        """
        self.data_dir = data_dir
        self.progress_file = os.path.join(data_dir, "user_progress.json")

        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        self._initialize_progress_file()

    def _initialize_progress_file(self):
        """Initialize the progress file if it doesn't exist."""
        if not os.path.exists(self.progress_file):
            self._save_progress({"users": {}})

    def _load_progress(self) -> dict:
        """Load progress data from file."""
        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": {}}

    def _save_progress(self, data: dict):
        """Save progress data to file."""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_user_progress(self, user_id: str) -> dict:
        """Get a user's progress data.

        Args:
            user_id (str): User ID

        Returns:
            dict: User's progress data
        """
        data = self._load_progress()
        return data["users"].get(
            user_id,
            {
                "concepts": {},
                "completed_paths": [],
                "current_path": None,
                "achievements": [],
                "last_activity": None,
            },
        )

    def update_concept_progress(self, user_id: str, concept: str, is_correct: bool):
        """Update a user's progress for a specific concept.

        Args:
            user_id (str): User ID
            concept (str): Concept ID
            is_correct (bool): Whether the user answered correctly
        """
        data = self._load_progress()

        # Initialize user data if not exists
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "concepts": {},
                "completed_paths": [],
                "current_path": None,
                "achievements": [],
                "last_activity": None,
            }

        # Initialize concept data if not exists
        if concept not in data["users"][user_id]["concepts"]:
            data["users"][user_id]["concepts"][concept] = {
                "attempts": 0,
                "correct": 0,
                "mastery": 0.0,
                "last_attempt": None,
            }

        # Update concept progress
        concept_data = data["users"][user_id]["concepts"][concept]
        concept_data["attempts"] += 1
        if is_correct:
            concept_data["correct"] += 1
        concept_data["mastery"] = concept_data["correct"] / concept_data["attempts"]
        concept_data["last_attempt"] = datetime.now().isoformat()

        # Update last activity
        data["users"][user_id]["last_activity"] = datetime.now().isoformat()

        self._save_progress(data)

    def set_current_path(self, user_id: str, path_id: str):
        """Set a user's current learning path.

        Args:
            user_id (str): User ID
            path_id (str): Learning path ID
        """
        data = self._load_progress()

        if user_id not in data["users"]:
            data["users"][user_id] = {
                "concepts": {},
                "completed_paths": [],
                "current_path": None,
                "achievements": [],
                "last_activity": None,
            }

        data["users"][user_id]["current_path"] = path_id
        data["users"][user_id]["last_activity"] = datetime.now().isoformat()

        self._save_progress(data)

    def complete_path(self, user_id: str, path_id: str):
        """Mark a learning path as completed for a user.

        Args:
            user_id (str): User ID
            path_id (str): Learning path ID
        """
        data = self._load_progress()

        if user_id not in data["users"]:
            data["users"][user_id] = {
                "concepts": {},
                "completed_paths": [],
                "current_path": None,
                "achievements": [],
                "last_activity": None,
            }

        if path_id not in data["users"][user_id]["completed_paths"]:
            data["users"][user_id]["completed_paths"].append(path_id)

        # Add achievement for completing path
        achievement = {
            "type": "path_completion",
            "path_id": path_id,
            "timestamp": datetime.now().isoformat(),
        }
        data["users"][user_id]["achievements"].append(achievement)

        data["users"][user_id]["last_activity"] = datetime.now().isoformat()

        self._save_progress(data)

    def get_user_achievements(self, user_id: str) -> List[dict]:
        """Get a user's achievements.

        Args:
            user_id (str): User ID

        Returns:
            List[dict]: List of user achievements
        """
        data = self._load_progress()
        if user_id not in data["users"]:
            return []

        return data["users"][user_id]["achievements"]

    def get_concept_mastery(self, user_id: str, concept: str) -> float:
        """Get a user's mastery level for a specific concept.

        Args:
            user_id (str): User ID
            concept (str): Concept ID

        Returns:
            float: Mastery level (0.0 to 1.0)
        """
        data = self._load_progress()
        if user_id not in data["users"]:
            return 0.0

        if concept not in data["users"][user_id]["concepts"]:
            return 0.0

        return data["users"][user_id]["concepts"][concept]["mastery"]
