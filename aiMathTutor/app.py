import streamlit as st
from core.rag.generator import ProblemGenerator
from core.openai.generator import OpenAIProblemGenerator
import json
from ui.components.history_viewer import HistoryViewer
import nest_asyncio
import asyncio
from utils.logger import Logger
import uuid

# 로거 초기화
logger = Logger()

# 이벤트 루프 설정
nest_asyncio.apply()

# 페이지 설정 - 반드시 다른 Streamlit 명령어보다 먼저 실행되어야 함
st.set_page_config(
    page_title="AI 수학 튜터",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 스타일 설정
st.markdown(
    """
    <style>
    .problem-area {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stRadio > label {
        background-color: #2E2E2E;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """세션 상태 초기화"""
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "openai"
        logger.info("세션 상태 초기화: current_tab = openai")
    if "current_problem" not in st.session_state:
        st.session_state.current_problem = None
        logger.info("세션 상태 초기화: current_problem = None")
    if "problem_count" not in st.session_state:
        st.session_state.problem_count = 5  # 기본값 5문제
        logger.info("세션 상태 초기화: problem_count = 5")
    if "user_id" not in st.session_state:
        st.session_state.user_id = "test_user"  # 실제 구현시 로그인 시스템과 연동
        logger.info("세션 상태 초기화: user_id = test_user")
    if "problem_history" not in st.session_state:
        st.session_state.problem_history = []  # 문제 히스토리 저장용
        logger.info("세션 상태 초기화: problem_history = []")


def display_problem_area(problem: dict, key_prefix: str, is_current: bool = False):
    """문제 영역 표시"""
    # 문제 ID가 없는 경우 UUID 생성하고 문제에 저장
    if "id" not in problem:
        problem["id"] = str(uuid.uuid4())

    with st.expander(
        f"📝 {problem['concept']} - {problem['difficulty']} 난이도", expanded=is_current
    ):
        st.markdown('<div class="problem-area">', unsafe_allow_html=True)

        # 문제 텍스트 표시
        st.markdown(f"### {problem['question']}")

        # 객관식 보기 표시
        if problem.get("options"):
            # 각 문제마다 고유한 키 생성 - key_prefix만 사용
            answer_key = f"{key_prefix}_answer"
            check_key = f"{key_prefix}_check"

            selected_answer = st.radio(
                "답을 선택하세요:",
                options=problem["options"],
                key=answer_key,
            )

            # 정답 확인 버튼
            if st.button("정답 확인", key=check_key):
                correct_idx = problem["correct_answer"] - 1
                if selected_answer == problem["options"][correct_idx]:
                    st.success("정답입니다! 🎉")
                else:
                    st.error(
                        f"틀렸습니다. 정답은 {problem['options'][correct_idx]}입니다."
                    )

                # 해설 표시
                st.markdown("### 📝 문제 해설")
                if problem.get("explanation"):
                    st.write(problem["explanation"])
                else:
                    st.write("이 문제에 대한 해설이 아직 준비되지 않았습니다.")

                # 현재 문제인 경우에만 다음 문제 네비게이션 표시
                if is_current and problem.get("next_problems"):
                    st.markdown("### 🔄 다음 문제 선택")
                    st.markdown("아래 버튼을 클릭하여 다음 문제를 선택하세요:")

                    # 다음 문제 선택 버튼들을 컬럼으로 배치
                    cols = st.columns(3)

                    with cols[0]:
                        if st.button(
                            "📚 유사 문제",
                            key=f"{key_prefix}_similar",
                            help="비슷한 난이도의 유사한 문제를 풀어보세요",
                            use_container_width=True,
                        ):
                            logger.info(
                                f"유사 문제 생성 시작 - 개념: {problem['next_problems']['similar']['concept']}"
                            )
                            generate_next_problem(
                                problem["next_problems"]["similar"], "similar"
                            )

                    with cols[1]:
                        if st.button(
                            "📈 더 어려운 문제",
                            key=f"{key_prefix}_harder",
                            help="한 단계 더 어려운 문제에 도전해보세요",
                            use_container_width=True,
                        ):
                            logger.info(
                                f"더 어려운 문제 생성 시작 - 개념: {problem['next_problems']['harder']['concept']}"
                            )
                            generate_next_problem(
                                problem["next_problems"]["harder"], "harder"
                            )

                    with cols[2]:
                        if st.button(
                            "🔄 연관 문제",
                            key=f"{key_prefix}_related",
                            help="관련된 다른 개념의 문제를 풀어보세요",
                            use_container_width=True,
                        ):
                            logger.info(
                                f"연관 문제 생성 시작 - 개념: {problem['next_problems']['related']['concept']}"
                            )
                            generate_next_problem(
                                problem["next_problems"]["related"], "related"
                            )

                    # 새로운 문제 생성 버튼 (구분선 아래에 배치)
                    st.divider()
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(
                            "📝 새로운 문제 생성",
                            key=f"{key_prefix}_new",
                            help="현재 설정된 개념의 새로운 문제를 생성합니다",
                            use_container_width=True,
                        ):
                            logger.info("새로운 문제 생성 시작")
                            try:
                                generator = OpenAIProblemGenerator()
                                if st.session_state.current_problem:
                                    # 중복 체크 후 히스토리에 추가
                                    if not any(
                                        p.get("id")
                                        == st.session_state.current_problem.get("id")
                                        for p in st.session_state.problem_history
                                    ):
                                        st.session_state.problem_history.append(
                                            st.session_state.current_problem
                                        )
                                problem = generator.generate_problem(
                                    problem["concept"], problem["difficulty"]
                                )
                                st.session_state.current_problem = problem
                                st.session_state.current_tab = "openai"
                                st.rerun()
                            except Exception as e:
                                error_msg = (
                                    f"문제 생성 중 오류가 발생했습니다: {str(e)}"
                                )
                                logger.error(error_msg)
                                st.error(error_msg)

        st.markdown("</div>", unsafe_allow_html=True)


def generate_next_problem(next_problem_info: dict, problem_type: str):
    """다음 문제 생성"""
    try:
        generator = OpenAIProblemGenerator()
        new_problem = generator.generate_problem(
            next_problem_info["concept"], next_problem_info["difficulty"]
        )

        # 현재 문제를 히스토리에 추가
        if st.session_state.current_problem:
            st.session_state.problem_history.append(st.session_state.current_problem)

        # 새 문제를 현재 문제로 설정
        st.session_state.current_problem = new_problem
        st.experimental_rerun()
    except Exception as e:
        st.error(f"문제 생성 중 오류가 발생했습니다: {str(e)}")


def main():
    # 메인 컨텐츠
    st.title("🎓 AI 수학 튜터")
    logger.info("애플리케이션 시작")

    # 세션 상태 초기화
    initialize_session_state()

    # 사이드바에 히스토리 표시
    history_viewer = HistoryViewer()
    with st.sidebar:
        history_viewer.display_history(st.session_state.user_id)
        logger.debug(f"사용자 {st.session_state.user_id}의 히스토리 표시")

        st.header("학습 경로 설정")

        # 도메인 선택
        domain = st.selectbox(
            "도메인", ["수와 연산", "도형", "측정", "규칙성", "자료와 가능성"], index=0
        )

        # 단원 선택
        unit = st.selectbox(
            "단원", ["분수와 소수", "약수와 배수", "도형의 넓이", "입체도형"], index=0
        )

        # 개념 선택
        concept = st.selectbox(
            "개념", ["최대공약수", "최소공배수", "약수 구하기", "소수 판별"], index=0
        )

        # 문제 수 선택
        st.session_state.problem_count = st.radio(
            "문제 수를 선택하세요:", [5, 15, 30, 45], index=0
        )

        st.divider()
        st.markdown("📍 **현재 학습 경로:**")
        st.write(f"도메인: {domain}")
        st.write(f"단원: {unit}")
        st.write(f"개념: {concept}")
        st.write(f"문제 수: {st.session_state.problem_count}개")
        logger.info(
            f"학습 경로 설정 - 도메인: {domain}, 단원: {unit}, 개념: {concept}, 문제 수: {st.session_state.problem_count}"
        )

    # 메인 영역 탭
    tab1, tab2 = st.tabs(["OpenAI 기반 문제 생성", "RAG 기반 문제 생성"])

    with tab1:
        st.header("OpenAI 기반 문제 생성")

        # 현재 문제 표시 (상단)
        if st.session_state.current_problem:
            st.markdown("### 현재 문제")
            display_problem_area(
                st.session_state.current_problem, "openai_current", True
            )

        # 새 문제 생성 버튼 (하단)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "📝 새로운 문제 생성", key="openai_gen", use_container_width=True
            ):
                logger.info("OpenAI 기반 새 문제 생성 시작")
                with st.spinner("OpenAI를 통해 문제를 생성중입니다..."):
                    try:
                        generator = OpenAIProblemGenerator()
                        # 현재 문제를 히스토리에 추가
                        if st.session_state.current_problem:
                            # 중복 체크 후 히스토리에 추가
                            current_id = st.session_state.current_problem.get("id")
                            if not any(
                                p.get("id") == current_id
                                for p in st.session_state.problem_history
                            ):
                                st.session_state.problem_history.append(
                                    st.session_state.current_problem
                                )
                                logger.info("이전 문제를 히스토리에 추가")
                        # 새 문제 생성
                        problem = generator.generate_problem(concept, "중")
                        st.session_state.current_problem = problem
                        st.session_state.current_tab = "openai"
                        logger.info("새 문제 생성 완료")
                        st.rerun()
                    except Exception as e:
                        error_msg = f"문제 생성 중 오류가 발생했습니다: {str(e)}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        return

        # 문제 히스토리 표시 (최신 문제가 위에 오도록)
        if st.session_state.problem_history:
            st.markdown("### 이전 문제들")
            # 중복 제거를 위해 ID 기준으로 필터링
            seen_ids = set()
            filtered_history = []
            for prob in reversed(st.session_state.problem_history):
                prob_id = prob.get("id")
                if prob_id and prob_id not in seen_ids:
                    seen_ids.add(prob_id)
                    filtered_history.append(prob)

            # 각 문제마다 고유한 키 생성 (OpenAI 탭용)
            for idx, prob in enumerate(filtered_history):
                unique_key = f"openai_history_{idx}"
                display_problem_area(prob, unique_key, False)

    with tab2:
        st.header("RAG 기반 문제 생성")

        # 현재 문제 표시 (상단)
        if st.session_state.current_problem and st.session_state.current_tab == "rag":
            st.markdown("### 현재 문제")
            display_problem_area(st.session_state.current_problem, "rag_current", True)

        # 새 문제 생성 버튼 (하단)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "📝 새로운 문제 생성", key="rag_gen", use_container_width=True
            ):
                logger.info("RAG 기반 새 문제 생성 시작")
                with st.spinner("유사 문제를 검색하여 새로운 문제를 생성중입니다..."):
                    try:
                        generator = ProblemGenerator()
                        problem = generator.generate_problem(concept, "중")
                        st.session_state.current_problem = problem
                        st.session_state.current_tab = "rag"
                        logger.info("새 문제 생성 완료")
                        st.rerun()
                    except Exception as e:
                        error_msg = f"문제 생성 중 오류가 발생했습니다: {str(e)}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        return

        # 문제 히스토리 표시
        if st.session_state.problem_history:
            st.markdown("### 이전 문제들")
            # 중복 제거를 위해 ID 기준으로 필터링
            seen_ids = set()
            filtered_history = []
            for prob in reversed(st.session_state.problem_history):
                prob_id = prob.get("id")
                if prob_id and prob_id not in seen_ids:
                    seen_ids.add(prob_id)
                    filtered_history.append(prob)

            # 각 문제마다 고유한 키 생성 (RAG 탭용)
            for idx, prob in enumerate(filtered_history):
                unique_key = f"rag_history_{idx}"
                display_problem_area(prob, unique_key, False)


if __name__ == "__main__":
    main()
