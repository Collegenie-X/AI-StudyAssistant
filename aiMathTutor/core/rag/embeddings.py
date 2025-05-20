from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List


class ProblemEmbedding:
    def __init__(self):
        """
        문제 임베딩을 위한 클래스 초기화
        - model: 다국어 지원 문장 임베딩 모델
        """
        self.model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        self.vector_store = None  # VectorStore 초기화는 별도로 진행

    def create_embedding(self, problem_text: str) -> np.ndarray:
        """
        문제 텍스트를 임베딩 벡터로 변환
        Args:
            problem_text (str): 변환할 문제 텍스트
        Returns:
            np.ndarray: 정규화된 임베딩 벡터
        """
        return self.model.encode(problem_text, normalize_embeddings=True)

    def batch_embed_problems(self, problems: List[dict]) -> None:
        """
        여러 문제를 일괄적으로 임베딩하여 저장
        Args:
            problems (List[dict]): 임베딩할 문제 목록
        """
        if not self.vector_store:
            raise ValueError("벡터 저장소가 초기화되지 않았습니다.")

        embeddings = [self.create_embedding(p["text"]) for p in problems]
        self.vector_store.add_vectors(embeddings, problems)
