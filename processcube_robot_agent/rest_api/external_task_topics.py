from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from ..robot_agent import builder

router = APIRouter()

class ExternalTaskTopics(BaseModel):
    topics: List[str] = []

@router.get("/external_tasks/topics", response_model=ExternalTaskTopics, tags=["external_tasks"])
async def get_external_task_topics():

    external_task_topics = ExternalTaskTopics()

    for external_task_record in builder.build():
        full_topic = external_task_record.get_topic()
        external_task_topics.topics.append(full_topic)

    return external_task_topics
