from typing import List, AsyncIterator
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import Image as AGImage
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv, find_dotenv
from PIL import Image
import yaml

from tools import Tools

class Minerva:
    """
    AI Guardian for Scam Protection using an Agentic Workflow
    """

    def __init__(self, config_path: str = "config/agents.yaml"):
        """
        Initialize Minerva with agents and tools
        """
        self.load_environment()
        self.model = self.initialize_model()
        self.config = self.load_config(config_path)
        self.tools = Tools()
        self.agents = self.create_agents()
        self.team = self.create_team()

    def load_environment(self):
        """Load environment variables"""
        load_dotenv(find_dotenv())

    def load_config(self, config_path: str) -> dict:
        """Load agent configurations from YAML file"""
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def initialize_model(self) -> OpenAIChatCompletionClient:
        """Initialize OpenAI model"""
        return OpenAIChatCompletionClient(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def create_agents(self) -> List[AssistantAgent]:
        """Create all required agents with their specialized roles and tools"""
        
        ocr_tool = FunctionTool(
            self.tools.ocr,
            description="Extracts text from an image path"
        )
        url_checker_tool = FunctionTool(
            self.tools.is_url_safe,
            description="Checks if a URL is safe"
        )

        agents = []
        
        agents.append(AssistantAgent(
            name="OCR_Specialist",
            description="Extracts text from an image",
            system_message=self.config['ocr_agent']['assignment'],
            model_client=self.model,
            #tools=[ocr_tool] # Default OCR to GPT-4o vision capabilities. Uncomment to OCR with tool calling (requires pytesseract)
        ))

        agents.append(AssistantAgent(
            name="URL_Checker",
            description="Checks if a URL is safe",
            system_message=self.config['url_checker_agent']['assignment'],
            model_client=self.model,
            tools=[url_checker_tool]
        ))

        agents.append(AssistantAgent(
            name="Content_Analyst",
            description="Analyzes the text for scam patterns",
            system_message=self.config['content_agent']['assignment'],
            model_client=self.model,
            tools=[url_checker_tool]
        ))

        agents.append(AssistantAgent(
            name="Decision_Maker",
            description="Synthesizes the analyses and make final determination",
            system_message=self.config['decision_agent']['assignment'],
            model_client=self.model
        ))

        agents.append(AssistantAgent(
            name="Summary_Agent",
            description="Generate a summary of the final determination",
            system_message=self.config['summary_agent']['assignment'],
            model_client=self.model
        ))

        agents.append(AssistantAgent(
            name="Language_Translation_Agent",
            description="Translate the summary to the user language",
            system_message=self.config['language_translation_agent']['assignment'],
            model_client=self.model
        ))

        return agents
    
    def create_team(self) -> RoundRobinGroupChat:
        """Create a team of agents that work together in Round Robin fashion"""
        return RoundRobinGroupChat(
            self.agents,
            max_turns=6
        )
    
    def reset(self):
        """Reset team state"""
        self.team.reset()

    async def analyze(self, image: Image) -> AsyncIterator:
        """
        Analyze an image for potential scams.
        """
        img = AGImage(image)
        mm_message = MultiModalMessage(content=[img], source="User")

        return self.team.run_stream(task=mm_message)