from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..deps import get_current_user, get_current_admin
from ..schemas import TaskCreate, TaskUpdate, TaskOut
from ..models import Task, User, Role
from ..crud.tasks import (
    create_task,
    get_task,
    list_tasks_by_owner,
    list_all_tasks,
    update_task,
    delete_task,
)
from ..database import get_async_session

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskOut, status_code=201)
async def create_task_ep(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await create_task(
        session, title=payload.title, description=payload.description, owner_id=current_user.id
    )

@router.get("/", response_model=list[TaskOut])
async def list_my_tasks(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await list_tasks_by_owner(session, current_user.id)

@router.get("/all", response_model=list[TaskOut])
async def list_everything(
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_current_admin),
):
    return await list_all_tasks(session)

@router.get("/{task_id}", response_model=TaskOut)
async def get_task_ep(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task = await get_task(session, task_id)
    if not task or (task.owner_id != current_user.id and current_user.role != Role.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task_ep(
    task_id: int,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task = await get_task(session, task_id)
    if not task or (task.owner_id != current_user.id and current_user.role != Role.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await update_task(
        session,
        task,
        title=payload.title,
        description=payload.description,
        is_completed=payload.is_completed,
    )

@router.delete("/{task_id}", status_code=204)
async def delete_task_ep(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task = await get_task(session, task_id)
    if not task or (task.owner_id != current_user.id and current_user.role != Role.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await delete_task(session, task)
    return None