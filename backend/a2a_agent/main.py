import logging
import os
import sys
import click
import httpx
import uvicorn
from uvicorn import Config, Server
import asyncio
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv
from agent_executor import KnowledgeAgentExecutor
from agent import KnowledgeAgent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def start_server(host, port, mcp_config, select_tool_names):
    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id='knowledge_search',
        name='工具助手Agent',
        description='会使用工具的Agent',
        tags=['知识检索', '多轮问答', '智能助手'],
        examples=['今天的日期？', '计算浙江 2025 年 4 月与 2025 年 3 月的月均 LNG 价格差。'],
    )
    CARD_URL = os.environ.get('CARD_URL', f'http://{host}:{port}/')
    agent_card = AgentCard(
        name='knowledge_search',
        description='根据用户的问题合理的使用工具的解决用户的问题',
        url=CARD_URL,
        version='1.0.0',
        defaultInputModes=KnowledgeAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=KnowledgeAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )
    # 启动服务
    agent_executor = KnowledgeAgentExecutor(mcp_config, select_tool_names)
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    config = Config(app=server.build(), host=host, port=port, log_level="info")
    server_instance = Server(config)
    await server_instance.serve()

@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10066)
@click.option('--mcp', default="mcp_config.json", help='MCP 配置文件路径')
@click.option('--select_tool_names', default="", help='使用的内部工具，逗号分隔')
def main(host, port, mcp, select_tool_names):
    select_tool_names = select_tool_names.split(",")
    if select_tool_names == ['']:
        select_tool_names = []
    asyncio.run(start_server(host, port, mcp, select_tool_names))

if __name__ == '__main__':
    main()