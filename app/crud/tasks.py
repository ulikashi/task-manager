from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Task

async def create_task(session: AsyncSession, *, title: str, description: str | None, owner_id: int) -> Task:
    task = Task(title=title, description=description, owner_id=owner_id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def get_task(session: AsyncSession, task_id: int) -> Task | None:
    res = await session.execute(select(Task).where(Task.id == task_id))
    return res.scalar_one_or_none()

async def list_tasks_by_owner(session: AsyncSession, owner_id: int) -> list[Task]:
    res = await session.execute(select(Task).where(Task.owner_id == owner_id).order_by(Task.id))
    return list(res.scalars().all())

async def list_all_tasks(session: AsyncSession) -> list[Task]:
    res = await session.execute(select(Task).order_by(Task.id))
    return list(res.scalars().all())

async def update_task(session: AsyncSession, task: Task, *, title: str | None = None, description: str | None = None, is_completed: bool | None = None) -> Task:
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if is_completed is not None:
        task.is_completed = is_completed
    await session.commit()
    await session.refresh(task)
    return task

async def delete_task(session: AsyncSession, task: Task) -> None:
    await session.delete(task)
    await session.commit()