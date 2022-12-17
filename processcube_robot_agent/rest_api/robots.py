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

    topic_prefic = builder_factory.get_topic_prefix()

    for external_task_record in builder_factory:
        full_topic = external_task_record.get_topic()
        robot_name = full_topic.replace(".", "/")
        robot_name = robot_name.replace(f"{topic_prefic}/", "") # TODO: 

        robot = Robot(name=robot_name, topic=full_topic)

        robots.topics.append(robot)

    return robots
