from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
)

from app.services.team_service import (
    get_all_teams,
    get_team_by_id,
    create_team,
    update_team,
    delete_team,
)


router = APIRouter()


# ----------------------------------------
# Get All Teams
# ----------------------------------------
@router.get(
    "/",
    response_model=list[TeamResponse],
)
def get_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_teams(db)


# ----------------------------------------
# Get Team By ID
# ----------------------------------------
@router.get(
    "/{team_id}",
    response_model=TeamResponse,
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_team_by_id(
            db,
            team_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


# ----------------------------------------
# Create Team
# ----------------------------------------
@router.post(
    "/",
    response_model=TeamResponse,
    status_code=201,
)
def create_new_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_team(
            db,
            team,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ----------------------------------------
# Update Team
# ----------------------------------------
@router.put(
    "/{team_id}",
    response_model=TeamResponse,
)
def update_existing_team(
    team_id: int,
    team: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_team(
            db,
            team_id,
            team,
        )

    except ValueError as e:
        error_message = str(e)

        if error_message == "Team not found":
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=error_message,
        )


# ----------------------------------------
# Delete Team
# ----------------------------------------
@router.delete("/{team_id}")
def delete_existing_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_team(
            db,
            team_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )