from typing import List

from autogen_agentchat.base import Response, TaskResult
from autogen_agentchat.messages import AgentMessage, MultiModalMessage


class AutoGenFormatter:
    def _message_to_str(self, message: AgentMessage) -> str:
        if isinstance(message, MultiModalMessage):
            result: List[str] = []
            for c in message.content:
                if isinstance(c, str):
                    result.append(c)
                else:
                    result.append("<image>")
            return "\n".join(result)
        else:
            return f"{message.content}"

    async def to_output(self, message: AgentMessage) -> str:
        try:
            if isinstance(message, TaskResult):
                output = (
                    f"{'-' * 10} Summary {'-' * 10}\n"
                    f"Number of messages: {len(message.messages)}\n"
                    f"Finish reason: {message.stop_reason}\n"
                )
                return output
            
            if isinstance(message, Response): 
                output = f"{'-' * 10} {message.chat_message.source} {'-' * 10}\n{self._message_to_str(message.chat_message)}\n"
                return output
            else:
                output = f"{'-' * 10} {message.source} {'-' * 10}\n{self._message_to_str(message)}\n"
                return output
        except Exception as e:
            return ""