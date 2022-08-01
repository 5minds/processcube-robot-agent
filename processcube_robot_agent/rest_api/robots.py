from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from ..robot_agent import builder

router = APIRouter()

class Robots(BaseModel):
    robot_names: List[str] = []

@router.get("/robot_agents/robots", response_model=Robots, tags=["external_tasks"])
async def get_robots():

    robots = Robots()

    for external_task_record in builder.build():
        full_topic = external_task_record.get_topic()
        robot_name = full_topic.replace(".", "/")
        robots.robot_names.append(robot_name)

    return robots
