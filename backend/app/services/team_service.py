from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.department import Department
from app.models.user import User

from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
)


# ----------------------------------------
# Get All Teams
# ----------------------------------------
def get_all_teams(db: Session):
    return db.query(Team).all()


# ----------------------------------------
# Get Team By ID
# ----------------------------------------
def get_team_by_id(
    db: Session,
    team_id: int,
):
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        raise ValueError("Team not found")

    return team


# ----------------------------------------
# Create Team
# ----------------------------------------
def create_team(
    db: Session,
    team: TeamCreate,
):

    # ------------------------------------
    # Validate Department
    # ------------------------------------
    department = (
        db.query(Department)
        .filter(
            Department.id == team.department_id
        )
        .first()
    )

    if not department:
        raise ValueError("Department not found")

    # ------------------------------------
    # Validate Team Lead
    # ------------------------------------
    if team.team_lead_id is not None:

        team_lead = (
            db.query(User)
            .filter(
                User.id == team.team_lead_id
            )
            .first()
        )

        if not team_lead:
            raise ValueError("Team lead not found")

        if not team_lead.is_active:
            raise ValueError(
                "Team lead is not active"
            )

    # ------------------------------------
    # Prevent Duplicate Team
    # Same team name inside department
    # ------------------------------------
    existing = (
        db.query(Team)
        .filter(
            Team.name == team.name,
            Team.department_id
            == team.department_id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Team already exists in this department"
        )

    # ------------------------------------
    # Create Team
    # ------------------------------------
    new_team = Team(
        name=team.name,
        description=team.description,
        department_id=team.department_id,
        team_lead_id=team.team_lead_id,
        is_active=team.is_active,
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team


# ----------------------------------------
# Update Team
# ----------------------------------------
def update_team(
    db: Session,
    team_id: int,
    team_data: TeamUpdate,
):

    team = get_team_by_id(
        db,
        team_id,
    )

    # ------------------------------------
    # Determine final Department ID
    # ------------------------------------
    final_department_id = (
        team_data.department_id
        if team_data.department_id is not None
        else team.department_id
    )

    # ------------------------------------
    # Validate Department
    # ------------------------------------
    if team_data.department_id is not None:

        department = (
            db.query(Department)
            .filter(
                Department.id
                == team_data.department_id
            )
            .first()
        )

        if not department:
            raise ValueError(
                "Department not found"
            )

    # ------------------------------------
    # Validate Team Lead
    # ------------------------------------
    if team_data.team_lead_id is not None:

        team_lead = (
            db.query(User)
            .filter(
                User.id
                == team_data.team_lead_id
            )
            .first()
        )

        if not team_lead:
            raise ValueError(
                "Team lead not found"
            )

        if not team_lead.is_active:
            raise ValueError(
                "Team lead is not active"
            )

    # ------------------------------------
    # Prevent Duplicate Team
    # ------------------------------------
    final_name = (
        team_data.name
        if team_data.name is not None
        else team.name
    )

    existing = (
        db.query(Team)
        .filter(
            Team.name == final_name,
            Team.department_id
            == final_department_id,
            Team.id != team_id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Team already exists in this department"
        )

    # ------------------------------------
    # Update Fields
    # ------------------------------------
    if team_data.name is not None:
        team.name = team_data.name

    if team_data.description is not None:
        team.description = (
            team_data.description
        )

    if team_data.department_id is not None:
        team.department_id = (
            team_data.department_id
        )

    if team_data.team_lead_id is not None:
        team.team_lead_id = (
            team_data.team_lead_id
        )

    if team_data.is_active is not None:
        team.is_active = (
            team_data.is_active
        )

    db.commit()
    db.refresh(team)

    return team


# ----------------------------------------
# Delete Team
# ----------------------------------------
def delete_team(
    db: Session,
    team_id: int,
):

    team = get_team_by_id(
        db,
        team_id,
    )

    db.delete(team)
    db.commit()

    return {
        "message": "Team deleted successfully"
    }