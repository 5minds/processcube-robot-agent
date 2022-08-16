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

@router.get("/robot_agents/robots", response_model=Robots, tags=["external_tasks"])
async def get_robots():

    robots = Robots()

    for external_task_record in builder.build():
        full_topic = external_task_record.get_topic()
        robot_name = full_topic.replace(".", "/")

        robot = Robot(name=robot_name, topic=full_topic)

        robots.topics.append(robot)

    return robots
