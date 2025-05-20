"""Learning Path Manager

This module manages the learning paths and concept progression using the knowledge map.
"""

import json
import os
from typing import Dict, List, Optional
import networkx as nx


class LearningPathManager:
    def __init__(self, data_dir: str = "data"):
        """Initialize the learning path manager.

        Args:
            data_dir (str): Directory containing knowledge_map.json
        """
        self.knowledge_map_file = os.path.join(data_dir, "knowledge_map.json")
        self.knowledge_map = self._load_knowledge_map()
        self.concept_graph = self._build_concept_graph()

    def _load_knowledge_map(self) -> dict:
        """Load the knowledge map from JSON file."""
        try:
            with open(self.knowledge_map_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "knowledge_map.json not found. Please ensure it exists in the data directory."
            )

    def _build_concept_graph(self) -> nx.DiGraph:
        """Build a directed graph of concept relationships."""
        graph = nx.DiGraph()

        # Add nodes (concepts)
        for concept_id, concept_data in self.knowledge_map["concepts"].items():
            graph.add_node(concept_id, **concept_data)

        # Add edges (prerequisites)
        for concept_id, concept_data in self.knowledge_map["concepts"].items():
            for prereq in concept_data["prerequisites"]:
                graph.add_edge(prereq, concept_id)

        return graph

    def get_available_learning_paths(self) -> List[dict]:
        """Get all available learning paths.

        Returns:
            List[dict]: List of learning path information
        """
        return [
            {"id": path_id, **path_data}
            for path_id, path_data in self.knowledge_map["learning_paths"].items()
        ]

    def get_next_concepts(self, current_concept: str) -> List[str]:
        """Get the next concepts in the learning progression.

        Args:
            current_concept (str): Current concept ID

        Returns:
            List[str]: List of next concept IDs
        """
        if current_concept not in self.knowledge_map["concepts"]:
            return []

        return self.knowledge_map["concepts"][current_concept]["next_concepts"]

    def get_prerequisites(self, concept: str) -> List[str]:
        """Get prerequisites for a concept.

        Args:
            concept (str): Concept ID

        Returns:
            List[str]: List of prerequisite concept IDs
        """
        if concept not in self.knowledge_map["concepts"]:
            return []

        return self.knowledge_map["concepts"][concept]["prerequisites"]

    def check_concept_readiness(self, concept: str, user_progress: dict) -> bool:
        """Check if a user is ready to start a concept.

        Args:
            concept (str): Concept ID to check
            user_progress (dict): User's progress data containing mastery levels

        Returns:
            bool: Whether the user is ready for the concept
        """
        if concept not in self.knowledge_map["concepts"]:
            return False

        # Check prerequisites
        prerequisites = self.get_prerequisites(concept)
        for prereq in prerequisites:
            # Get required mastery threshold
            required_mastery = self.knowledge_map["concepts"][prereq][
                "mastery_threshold"
            ]

            # Check user's mastery level
            user_mastery = user_progress.get(prereq, 0)
            if user_mastery < required_mastery:
                return False

        return True

    def get_recommended_difficulty(self, concept: str, user_progress: dict) -> str:
        """Get recommended difficulty level for a concept based on user's progress.

        Args:
            concept (str): Concept ID
            user_progress (dict): User's progress data

        Returns:
            str: Recommended difficulty level ('easy', 'medium', or 'hard')
        """
        if concept not in self.knowledge_map["concepts"]:
            return "easy"

        mastery_level = user_progress.get(concept, 0)

        if mastery_level < 0.3:
            return "easy"
        elif mastery_level < 0.7:
            return "medium"
        else:
            return "hard"

    def get_learning_path_progress(self, path_id: str, user_progress: dict) -> dict:
        """Get user's progress in a specific learning path.

        Args:
            path_id (str): Learning path ID
            user_progress (dict): User's progress data

        Returns:
            dict: Progress information including completion percentage and next concepts
        """
        if path_id not in self.knowledge_map["learning_paths"]:
            return {"error": "Learning path not found"}

        path = self.knowledge_map["learning_paths"][path_id]
        sequence = path["sequence"]

        completed_concepts = []
        next_concepts = []
        current_concept = None

        for concept in sequence:
            mastery = user_progress.get(concept, 0)
            threshold = self.knowledge_map["concepts"][concept]["mastery_threshold"]

            if mastery >= threshold:
                completed_concepts.append(concept)
            elif current_concept is None:
                current_concept = concept
                next_concepts = self.get_next_concepts(concept)
                break

        completion_percentage = (len(completed_concepts) / len(sequence)) * 100

        return {
            "path_name": path["name"],
            "completed_concepts": completed_concepts,
            "current_concept": current_concept,
            "next_concepts": next_concepts,
            "completion_percentage": round(completion_percentage, 2),
        }

    def get_concept_details(self, concept: str) -> Optional[dict]:
        """Get detailed information about a concept.

        Args:
            concept (str): Concept ID

        Returns:
            Optional[dict]: Concept details or None if not found
        """
        return self.knowledge_map["concepts"].get(concept)
