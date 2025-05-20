"""Learning Path Visualizer Component

This module provides visualization of learning paths and user progress.
"""

import streamlit as st
from core.knowledge.learning_path_manager import LearningPathManager


class PathVisualizer:
    def __init__(self, learning_path_manager: LearningPathManager):
        """Initialize the path visualizer.

        Args:
            learning_path_manager (LearningPathManager): Learning path manager instance
        """
        self.path_manager = learning_path_manager

    def display_available_paths(self, user_id: str, user_progress: dict):
        """Display available learning paths and their progress.

        Args:
            user_id (str): User ID
            user_progress (dict): User's progress data
        """
        st.header("📚 Learning Paths")

        # Get all available paths
        paths = self.path_manager.get_available_learning_paths()

        for path in paths:
            with st.expander(f"🎯 {path['name']}", expanded=False):
                # Get progress information
                progress = self.path_manager.get_learning_path_progress(
                    path["id"], user_progress
                )

                # Display progress bar
                st.progress(progress["completion_percentage"] / 100)
                st.write(f"Progress: {progress['completion_percentage']}%")

                # Display path description
                st.write(path["description"])

                # Create columns for concept progression
                cols = st.columns(len(path["sequence"]))

                # Display concepts in sequence
                for i, concept_id in enumerate(path["sequence"]):
                    concept = self.path_manager.get_concept_details(concept_id)
                    with cols[i]:
                        self._display_concept_card(
                            concept,
                            completed=(concept_id in progress["completed_concepts"]),
                            current=(concept_id == progress["current_concept"]),
                            user_progress=user_progress,
                        )

                # Display current status and recommendations
                if progress["current_concept"]:
                    current_concept = self.path_manager.get_concept_details(
                        progress["current_concept"]
                    )
                    st.write("#### Current Focus")
                    st.write(
                        f"You are currently working on: **{current_concept['name']}**"
                    )

                    # Show recommended difficulty
                    recommended_difficulty = (
                        self.path_manager.get_recommended_difficulty(
                            progress["current_concept"], user_progress
                        )
                    )
                    st.write(
                        f"Recommended difficulty: **{recommended_difficulty.title()}**"
                    )

                    # Show prerequisites status
                    prerequisites = self.path_manager.get_prerequisites(
                        progress["current_concept"]
                    )
                    if prerequisites:
                        st.write("Prerequisites status:")
                        for prereq in prerequisites:
                            prereq_data = self.path_manager.get_concept_details(prereq)
                            mastery = user_progress.get(prereq, 0)
                            threshold = prereq_data["mastery_threshold"]
                            status = "✅" if mastery >= threshold else "⚠️"
                            st.write(
                                f"{status} {prereq_data['name']}: {mastery*100:.1f}%"
                            )

    def _display_concept_card(
        self, concept: dict, completed: bool, current: bool, user_progress: dict
    ):
        """Display a concept card with progress information.

        Args:
            concept (dict): Concept details
            completed (bool): Whether the concept is completed
            current (bool): Whether this is the current concept
            user_progress (dict): User's progress data
        """
        # Determine card style
        if completed:
            card_color = "success"
            icon = "✅"
        elif current:
            card_color = "primary"
            icon = "🎯"
        else:
            card_color = "light"
            icon = "⭕"

        # Create card container
        card_html = f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid {'#28a745' if completed else '#007bff' if current else '#dee2e6'};
            background-color: {'#d4edda' if completed else '#cce5ff' if current else '#f8f9fa'};
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0;">{icon} {concept['name']}</h4>
            <div style="margin-top: 0.5rem;">
                <small>Mastery: {user_progress.get(concept['id'], 0)*100:.1f}%</small>
                <div style="
                    height: 4px;
                    background-color: #e9ecef;
                    border-radius: 2px;
                    margin-top: 0.25rem;
                ">
                    <div style="
                        width: {user_progress.get(concept['id'], 0)*100}%;
                        height: 100%;
                        background-color: {'#28a745' if completed else '#007bff' if current else '#6c757d'};
                        border-radius: 2px;
                    "></div>
                </div>
            </div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        # Show action button for current concept
        if current:
            if st.button(f"Start {concept['name']}", key=f"start_{concept['id']}"):
                st.session_state.selected_concept = concept["id"]
