from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from ..robot_agent import builder

router = APIRouter()

class Robot(BaseModel):
    name: str
    topic: str

class Robots(BaseModel):
    topics: List[Robot] = []

@router.get("/robot_agents/robots",
    response_model=Robots,
    tags=["external_tasks"],
    summary="Request the names and topics of all robots",
    description="Get the robots by name and the related topic that are connected to the configured processcube engine.",
)
async def get_robots():

    robots = Robots()

    builder_factory = builder.build()

    for external_task_record in builder_factory:
        full_topic = external_task_record.get_topic()

        # Extract robot name from topic
        # Topics are formatted as: {prefix}.{robot_path}
        # e.g., "rcc.windows.ui" or "uv.example-python-robot"
        # Extract just the robot_path part
        topic_parts = full_topic.split('.')

        # Skip the first part (prefix like 'rcc' or 'uv')
        if len(topic_parts) > 1:
            robot_path = '.'.join(topic_parts[1:])
            robot_name = robot_path.replace(".", "/")
        else:
            robot_name = full_topic

        robot = Robot(name=robot_name, topic=full_topic)

        robots.topics.append(robot)

    return robots
