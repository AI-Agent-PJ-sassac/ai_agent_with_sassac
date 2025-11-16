# chat.py
"""
대화형 인터페이스 - 질문하고 답변 받기
"""

import warnings
from workflow import HandoverWorkflow
import sys

# 경고 메시지 숨기기
warnings.filterwarnings("ignore", category=DeprecationWarning)

def print_header():
    """헤더 출력"""
    print("\n" + "=" * 60)
    print("🏛️  공공기관 인수인계 AI Agent")
    print("=" * 60)
    print("질문을 입력하면 AI가 답변해드립니다.")
    print("종료하려면 'quit', 'exit', 'q' 를 입력하세요.")
    print("=" * 60 + "\n")

def print_answer(result):
    """답변을 예쁘게 출력"""
    print("\n" + "=" * 60)
    print("💬 답변")
    print("=" * 60)
    print(result['answer'])
    
    # 경고가 있으면 표시
    if result.get('warnings'):
        print("\n" + "-" * 60)
        print("⚠️  참고사항")
        print("-" * 60)
        for warning in result['warnings']:
            print(f"  {warning}")
    
    # 참조 문서 통계
    search_count = len(result.get('search_results', []))
    template_count = len(result.get('templates', []))
    example_count = len(result.get('examples', []))
    
    if search_count > 0 or template_count > 0 or example_count > 0:
        print("\n" + "-" * 60)
        print("📚 참조 문서")
        print("-" * 60)
        print(f"  검색 결과: {search_count}개")
        print(f"  템플릿: {template_count}개")
        print(f"  예시: {example_count}개")
    
    print("=" * 60 + "\n")

def main():
    """메인 함수"""
    print_header()
    
    # 워크플로우 초기화
    print("🔄 AI Agent 초기화 중...")
    try:
        workflow = HandoverWorkflow()
        print("✅ 준비 완료!\n")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        print("벡터 DB가 생성되어 있는지 확인해주세요.")
        print("  → python vector_store.py 실행")
        return
    
    # 대화 루프
    while True:
        try:
            # 질문 입력
            question = input("❓ 질문: ").strip()
            
            # 종료 명령어 체크
            if question.lower() in ['quit', 'exit', 'q', '종료', '끝']:
                print("\n👋 AI Agent를 종료합니다. 감사합니다!")
                break
            
            # 빈 입력 체크
            if not question:
                print("⚠️  질문을 입력해주세요.\n")
                continue
            
            # 워크플로우 실행
            print("\n🤔 답변 생성 중...")
            result = workflow.run(question, save_result=True)
            
            # 답변 출력
            print_answer(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 AI Agent를 종료합니다. 감사합니다!")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            print("다시 시도해주세요.\n")

if __name__ == "__main__":
    main()