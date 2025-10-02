#!/usr/bin/env python3
"""
워크플로우 매니저
연속 작업을 관리하고 실행하는 모듈
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import autogen
from main import setup_agents, is_termination_msg, load_config


class WorkflowManager:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.results_dir = Path(self.config["results_dir"])
        self.workflow_dir = self.results_dir / "workflows"
        self.workflow_dir.mkdir(exist_ok=True)
        self.current_workflow_id = None
        self.workflow_results = []
        
    def _load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        with open(config_path, "r") as f:
            return json.load(f)
    
    def load_workflow(self, workflow_file: str) -> List[Dict[str, Any]]:
        """워크플로우 파일 로드"""
        with open(workflow_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # 단순 작업 리스트
            return [{"name": f"Task {i+1}", "task": task} for i, task in enumerate(data)]
        elif "tasks" in data:
            # 구조화된 워크플로우
            return data["tasks"]
        else:
            raise ValueError("Invalid workflow format")
    
    def create_workflow_id(self) -> str:
        """워크플로우 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"workflow_{timestamp}"
    
    def save_workflow_state(self, current_task_idx: int, total_tasks: int, status: str):
        """워크플로우 상태 저장"""
        state_file = self.workflow_dir / f"{self.current_workflow_id}_state.json"
        state = {
            "workflow_id": self.current_workflow_id,
            "current_task": current_task_idx,
            "total_tasks": total_tasks,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "results": self.workflow_results
        }
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def run_single_task(self, task: Dict[str, Any], task_idx: int, previous_results: List[Dict] = None):
        """단일 작업 실행"""
        from main import is_termination_msg
        builder, evaluator, user_proxy = setup_agents(self.config)

        # 이전 작업 결과를 컨텍스트로 포함
        context = ""
        if previous_results:
            context = "\n\n=== Previous Task Results ===\n"
            for prev in previous_results[-2:]:  # 최근 2개만
                context += f"\n[{prev['name']}]\n{prev['summary']}\n"

        task_message = f"{context}\n\nCurrent Task: {task['task']}"

        print(f"\n{'='*60}")
        print(f"📌 작업 {task_idx + 1}: {task.get('name', 'Unnamed Task')}")
        print(f"📋 내용: {task['task']}")
        print(f"{'='*60}\n")

        # GroupChat 설정 (UserProxy 추가)
        groupchat = autogen.GroupChat(
            agents=[user_proxy, builder, evaluator],
            messages=[],
            max_round=self.config["max_iterations"],
        )

        # ChatManager 설정
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=builder.llm_config
        )

        # 대화 시작
        user_proxy.initiate_chat(
            manager,
            message=task_message,
        )
        
        # 결과 추출
        chat_history = groupchat.messages
        result_summary = self._extract_summary(chat_history)
        
        result = {
            "task_idx": task_idx,
            "name": task.get("name", f"Task {task_idx + 1}"),
            "task": task["task"],
            "chat_history": chat_history,
            "iterations": len(chat_history),
            "summary": result_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        self.workflow_results.append(result)
        return result
    
    def _extract_summary(self, chat_history: List[Dict]) -> str:
        """대화 기록에서 요약 추출"""
        # 마지막 몇 개 메시지에서 핵심 내용 추출
        summary_parts = []
        for msg in chat_history[-3:]:
            if msg.get("name") == "Evaluator" and "APPROVE" in msg.get("content", ""):
                # Evaluator의 승인 메시지에서 요약 추출
                content = msg["content"]
                if "```" in content:
                    # 코드 블록 추출
                    code_start = content.find("```")
                    code_end = content.rfind("```")
                    if code_start != code_end:
                        summary_parts.append(content[code_start:code_end+3])
                else:
                    summary_parts.append(content[:200] + "...")
        
        return "\n".join(summary_parts) if summary_parts else "작업 완료"
    
    def run_workflow(self, workflow_file: str):
        """전체 워크플로우 실행"""
        self.current_workflow_id = self.create_workflow_id()
        self.workflow_results = []
        
        print(f"🚀 워크플로우 시작: {self.current_workflow_id}")
        
        try:
            tasks = self.load_workflow(workflow_file)
            total_tasks = len(tasks)
            
            print(f"📋 총 {total_tasks}개의 작업이 있습니다.\n")
            
            for idx, task in enumerate(tasks):
                self.save_workflow_state(idx, total_tasks, "in_progress")
                
                # 이전 결과를 컨텍스트로 전달
                result = self.run_single_task(task, idx, self.workflow_results)
                
                print(f"\n✅ 작업 {idx + 1}/{total_tasks} 완료")
                print(f"   반복 횟수: {result['iterations']}")
                
                # 잠시 대기 (API 제한 고려)
                if idx < total_tasks - 1:
                    import time
                    print("\n⏳ 다음 작업 준비 중... (5초 대기)")
                    time.sleep(5)
            
            self.save_workflow_state(total_tasks, total_tasks, "completed")
            self.save_final_results()
            
            print(f"\n🎉 워크플로우 완료!")
            print(f"📊 총 {total_tasks}개 작업 완료")
            print(f"💾 결과 저장: {self.workflow_dir}/{self.current_workflow_id}_final.json")
            
        except Exception as e:
            print(f"\n❌ 워크플로우 실행 중 오류 발생: {e}")
            self.save_workflow_state(-1, -1, "failed")
            raise
    
    def save_final_results(self):
        """최종 결과 저장"""
        final_file = self.workflow_dir / f"{self.current_workflow_id}_final.json"
        final_data = {
            "workflow_id": self.current_workflow_id,
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(self.workflow_results),
            "results": self.workflow_results,
            "summary": self._create_workflow_summary()
        }
        
        with open(final_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        # latest 링크 업데이트
        latest_file = self.workflow_dir / "latest_workflow.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    def _create_workflow_summary(self) -> str:
        """워크플로우 전체 요약 생성"""
        summary_lines = ["워크플로우 요약:"]
        for result in self.workflow_results:
            summary_lines.append(f"\n[{result['name']}]")
            summary_lines.append(f"- 작업: {result['task']}")
            summary_lines.append(f"- 결과: {result['summary'][:100]}...")
            summary_lines.append(f"- 반복: {result['iterations']}회")
        
        return "\n".join(summary_lines)


def main():
    """CLI 진입점"""
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python workflow_manager.py <workflow_file>")
        print("예시: python workflow_manager.py tasks/korean_corrector_workflow.json")
        sys.exit(1)
    
    workflow_file = sys.argv[1]
    
    if not os.path.exists(workflow_file):
        print(f"❌ 파일을 찾을 수 없습니다: {workflow_file}")
        sys.exit(1)
    
    manager = WorkflowManager()
    
    try:
        manager.run_workflow(workflow_file)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()