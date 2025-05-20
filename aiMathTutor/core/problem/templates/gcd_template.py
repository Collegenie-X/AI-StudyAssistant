"""
최대공약수(GCD) 문제 생성을 위한 템플릿 모듈
"""
import random
from typing import Dict, List, Tuple
import math

class GCDProblemTemplate:
    def __init__(self):
        # 난이도별 숫자 범위 정의
        self.difficulty_ranges = {
            'easy': (10, 99),    # 2자리 수
            'medium': (50, 199), # 2-3자리 수
            'hard': (100, 999)   # 3자리 수
        }
        
    def _generate_number_pair(self, difficulty: str) -> Tuple[int, int]:
        """난이도에 따른 숫자 쌍 생성"""
        min_val, max_val = self.difficulty_ranges[difficulty]
        
        # 첫 번째 숫자 생성
        num1 = random.randint(min_val, max_val)
        
        # GCD가 1이 되지 않도록 두 번째 숫자 생성
        while True:
            num2 = random.randint(min_val, max_val)
            if math.gcd(num1, num2) > 1:
                break
                
        return num1, num2
    
    def _generate_wrong_answers(self, correct_gcd: int, num1: int, num2: int) -> List[int]:
        """오답 보기 생성"""
        wrong_answers = set()
        
        # 공약수가 아닌 수를 포함
        wrong_answers.add(correct_gcd + 1)
        wrong_answers.add(correct_gcd - 1 if correct_gcd > 1 else 2)
        
        # 두 수의 공약수 중 GCD가 아닌 수를 포함
        smaller_num = min(num1, num2)
        for i in range(1, smaller_num + 1):
            if num1 % i == 0 and num2 % i == 0 and i != correct_gcd:
                wrong_answers.add(i)
                if len(wrong_answers) >= 3:
                    break
        
        # 필요한 경우 추가 오답 생성
        while len(wrong_answers) < 3:
            wrong = random.randint(1, correct_gcd * 2)
            if wrong != correct_gcd:
                wrong_answers.add(wrong)
                
        return list(wrong_answers)[:3]
    
    def generate_problem(self, difficulty: str) -> Dict:
        """주어진 난이도에 따른 GCD 문제 생성"""
        # 숫자 쌍 생성
        num1, num2 = self._generate_number_pair(difficulty)
        correct_gcd = math.gcd(num1, num2)
        
        # 오답 생성
        wrong_answers = self._generate_wrong_answers(correct_gcd, num1, num2)
        
        # 보기 생성 및 섞기
        options = [correct_gcd] + wrong_answers
        random.shuffle(options)
        
        # 정답 인덱스 찾기
        correct_index = options.index(correct_gcd)
        answer = chr(65 + correct_index)  # A, B, C, D로 변환
        
        # 문제 생성
        problem = {
            "question": f"{num1}와 {num2}의 최대공약수(GCD)는 얼마인가요?",
            "options": {
                "A": str(options[0]),
                "B": str(options[1]),
                "C": str(options[2]),
                "D": str(options[3])
            },
            "answer": answer,
            "explanation": f"{num1}과 {num2}의 공약수를 구하고, 그 중 가장 큰 수를 찾습니다.\n"
                         f"정답은 {correct_gcd}입니다."
        }
        
        return problem

    def generate_similar_problem(self, original_problem: Dict, variation_type: str = 'numbers') -> Dict:
        """기존 문제와 유사한 새로운 문제 생성"""
        # 원본 문제에서 숫자 추출
        nums = [int(n) for n in original_problem["question"].split()
               if n.isdigit()]
        
        if variation_type == 'numbers':
            # 비슷한 크기의 숫자로 변경
            num1 = nums[0] + random.randint(-10, 10)
            num2 = nums[1] + random.randint(-10, 10)
            
            # GCD가 1이 되지 않도록 조정
            while math.gcd(num1, num2) <= 1:
                num1 = nums[0] + random.randint(-10, 10)
                num2 = nums[1] + random.randint(-10, 10)
                
        elif variation_type == 'scale':
            # 숫자 크기를 2배로 확대
            num1 = nums[0] * 2
            num2 = nums[1] * 2
            
        else:
            # 기본적으로 새로운 숫자 생성
            difficulty = 'medium'  # 기본 난이도
            num1, num2 = self._generate_number_pair(difficulty)
            
        correct_gcd = math.gcd(num1, num2)
        wrong_answers = self._generate_wrong_answers(correct_gcd, num1, num2)
        
        options = [correct_gcd] + wrong_answers
        random.shuffle(options)
        correct_index = options.index(correct_gcd)
        answer = chr(65 + correct_index)
        
        return {
            "question": f"{num1}와 {num2}의 최대공약수(GCD)는 얼마인가요?",
            "options": {
                "A": str(options[0]),
                "B": str(options[1]),
                "C": str(options[2]),
                "D": str(options[3])
            },
            "answer": answer,
            "explanation": f"{num1}과 {num2}의 공약수를 구하고, 그 중 가장 큰 수를 찾습니다.\n"
                         f"정답은 {correct_gcd}입니다."
        } 