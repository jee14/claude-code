#!/usr/bin/env python3
"""
자율 에이전트 시스템
Builder와 Evaluator가 자동으로 대화하며 프로젝트를 완성
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import autogen
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def load_config():
    """설정 파일 로드"""
    with open("config.json", "r") as f:
        return json.load(f)


def setup_agents(config):
    """에이전트 설정"""
    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        raise ValueError(
            f"{config['api_key_env']} 환경 변수가 설정되지 않았습니다"
        )

    # 모델 이름 가져오기 (.env에서 또는 config에서)
    model = os.getenv(config.get("model_env", ""),
                      config.get("model", "anthropic/claude-sonnet-4.5"))

    print(f"🤖 사용 모델: {model}")

    # OpenRouter 설정 (OpenAI 호환)
    llm_config = {
        "model": model,
        "api_key": api_key,
        "base_url": config.get("base_url", "https://openrouter.ai/api/v1"),
        "api_type": "openai",
    }

    # Builder 에이전트
    builder = autogen.AssistantAgent(
        name=config["builder"]["name"],
        system_message=config["builder"]["system_message"],
        llm_config=llm_config,
    )

    # Evaluator 에이전트
    evaluator = autogen.AssistantAgent(
        name=config["evaluator"]["name"],
        system_message=config["evaluator"]["system_message"],
        llm_config=llm_config,
    )

    # UserProxy 에이전트 (코드 실행 및 파일 저장)
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",  # 자동 실행
        max_consecutive_auto_reply=10,  # 자동 응답 허용
        is_termination_msg=is_termination_msg,  # APPROVE 시 종료
        code_execution_config={
            "work_dir": config.get("output_dir", "generated_code"),
            "use_docker": False,
        },
    )

    return builder, evaluator, user_proxy


def is_termination_msg(msg):
    """종료 조건 체크"""
    content = msg.get("content", "")
    return "APPROVE" in content.upper()


def save_results(chat_history, task, config):
    """결과 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(config["results_dir"])
    results_dir.mkdir(exist_ok=True)

    result_file = results_dir / f"result_{timestamp}.json"

    result_data = {
        "timestamp": timestamp,
        "task": task,
        "chat_history": chat_history,
        "iterations": len(chat_history),
    }

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    # 최신 결과를 latest.json으로도 저장
    latest_file = results_dir / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 결과 저장됨: {result_file}")
    return result_file


def run_autonomous_agents(task: str):
    """자율 에이전트 실행"""
    config = load_config()
    builder, evaluator, user_proxy = setup_agents(config)

    print(f"🚀 자율 에이전트 시작")
    print(f"📋 작업: {task}")
    print(f"🔄 최대 반복: {config['max_iterations']}")
    print("-" * 60)

    # GroupChat 설정 (UserProxy 추가)
    groupchat = autogen.GroupChat(
        agents=[user_proxy, builder, evaluator],
        messages=[],
        max_round=config["max_iterations"],
    )

    # ChatManager 설정
    manager = autogen.GroupChatManager(
        groupchat=groupchat, llm_config=builder.llm_config
    )

    # 대화 시작
    user_proxy.initiate_chat(
        manager,
        message=task,
    )

    # 결과 저장
    chat_history = groupchat.messages
    result_file = save_results(chat_history, task, config)

    print(f"\n🎉 작업 완료!")
    print(f"📊 총 {len(chat_history)}번의 대화")

    return result_file


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python main.py '작업 설명'")
        print(
            "예시: python main.py 'FastAPI로 간단한 TODO API를 만들어주세요'"
        )
        sys.exit(1)

    task = sys.argv[1]

    try:
        run_autonomous_agents(task)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
