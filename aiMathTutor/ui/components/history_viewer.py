import streamlit as st
from datetime import datetime
from core.problem.problem_repository import ProblemRepository


class HistoryViewer:
    def __init__(self):
        self.problem_repo = ProblemRepository()

    def format_datetime(self, iso_date: str) -> str:
        """ISO 형식의 날짜를 보기 좋은 형식으로 변환"""
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime("%Y-%m-%d %H:%M")

    def display_history(self, user_id: str):
        """사용자의 문제 풀이 히스토리를 표시"""
        with st.expander("📚 문제 풀이 히스토리", expanded=False):
            # 통계 정보 표시
            stats = self.problem_repo.get_user_statistics(user_id)
            total_attempts = stats["total_attempts"]
            correct_answers = stats["correct_answers"]
            accuracy = stats["accuracy"]

            # 통계 카드들을 나란히 표시
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("총 시도 횟수", f"{total_attempts}회")
            with col2:
                st.metric("정답 수", f"{correct_answers}회")
            with col3:
                st.metric("정답률", f"{accuracy:.1f}%")
            with col4:
                st.metric("푼 문제 수", f"{stats['unique_problems']}개")

            # 최근 풀이 기록 표시
            history = self.problem_repo.get_user_history(user_id)

            if not history:
                st.info("아직 풀이한 문제가 없습니다.")
                return

            # 히스토리 테이블 표시
            for entry in history:  # 이미 최신 순으로 정렬되어 있음
                with st.container():
                    problem = entry.get("problem")
                    if problem:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(
                                f"""
                            **문제 ID**: {problem['id']}  
                            **개념**: {problem['concept']}  
                            **난이도**: {problem['difficulty']}  
                            **풀이 시간**: {self.format_datetime(entry['timestamp'])}
                            """
                            )
                        with col2:
                            status = "✅ 정답" if entry["is_correct"] else "❌ 오답"
                            st.markdown(f"**결과**: {status}")
                            st.markdown(f"**제출한 답**: {entry['answer']}")

                        # 문제 내용 표시
                        with st.expander("문제 보기", expanded=False):
                            st.markdown(f"**문제**: {problem['question']}")
                            st.markdown(f"**보기**:")
                            for i, option in enumerate(problem["options"], 1):
                                st.markdown(f"{i}. {option}")
                            st.markdown(f"**정답**: {problem['correct_answer']}")
                            st.markdown(f"**해설**: {problem['explanation']}")

                        st.divider()
