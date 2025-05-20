import logging
import streamlit as st
from datetime import datetime
import os


class Logger:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            # 로그 디렉토리 생성
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # 로그 파일 설정
            log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"

            # 로거 설정
            self.logger = logging.getLogger("AI_Math_Tutor")
            self.logger.setLevel(logging.INFO)

            # 파일 핸들러 설정
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.INFO)

            # 포맷터 설정
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)

            # 핸들러 추가
            self.logger.addHandler(file_handler)

            self._is_initialized = True

    def info(self, message: str) -> None:
        # 정보 로그를 기록합니다.
        self.logger.info(message)
        st.write(f"ℹ️ {message}")

    def error(self, message: str) -> None:
        # 에러 로그를 기록합니다.
        self.logger.error(message)
        st.error(message)

    def debug(self, message: str) -> None:
        # 디버그 로그를 기록합니다.
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        # 경고 로그를 기록합니다.
        self.logger.warning(message)
        st.warning(message)
