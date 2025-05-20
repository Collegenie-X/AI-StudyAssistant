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
            total = stats["total"]
            correct = stats["correct"]
            accuracy = (correct / total * 100) if total > 0 else 0

            # 통계 카드들을 나란히 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 문제 수", f"{total}문제")
            with col2:
                st.metric("정답 수", f"{correct}문제")
            with col3:
                st.metric("정답률", f"{accuracy:.1f}%")

            # 히스토리 데이터 로드
            with open(self.problem_repo.history_file, "r", encoding="utf-8") as f:
                import json

                data = json.load(f)
                history = data["problem_history"]

                # 현재 사용자의 히스토리만 필터링
                user_history = [h for h in history if h["user_id"] == user_id]

                if not user_history:
                    st.info("아직 풀이한 문제가 없습니다.")
                    return

                # 히스토리 테이블 표시
                for entry in reversed(user_history):  # 최신 기록부터 표시
                    with st.container():
                        problem = self.problem_repo.get_problem(entry["problem_id"])
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
                            st.divider()
