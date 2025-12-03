from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, select, Relationship
from datetime import datetime
from typing import Dict, Optional, List
from database import create_file_db, engine, get_session
from datetime import datetime


# Child Model: many exercises can reference a single workout
# EX: incline smith and bench press can point to that same id push day
class Exercise(SQLModel, table=True):
	exercise_id : Optional[int] = Field(default=None,primary_key=True)
	exercise_name : str
	weight : float
	reps : int
	sets : int
	date : datetime  = Field(default_factory=datetime.utcnow) 
	# This the the FK that points to the parent class
	workout_id : Optional[int] = Field(default=None, foreign_key="workout.id")
	workout : Optional["Workout"] = Relationship(back_populates="exercises") 

# Parent class: can have many exercises 
class Workout(SQLModel,table=True):
	id : Optional[int] = Field(default=None, primary_key=True)
	workout_name : str
	date : datetime =  Field(default_factory=datetime.utcnow) 
	# Relationship between exercises and workout
	exercises : List["Exercise"] = Relationship(back_populates="workout", sa_relationship_kwargs={"cascade":"all,delete"})



class WorkoutCreate(SQLModel):
	workout_name : str 

class ExerciseCreate(SQLModel):
	exercise_name : str
	sets : int
	reps : int
	weight : float


app = FastAPI()

@app.on_event("startup")
def create_db():
	create_file_db()

@app.get("/")
def health() -> Dict[str, str | float]:
	return {"health" : "active", "version" : 1.0}



@app.post("/workouts")
def create_workout(workout_name : WorkoutCreate, session: Session = Depends(get_session)) -> Workout:
	"""
	Docstring for create_workout
	
	:param workout_name: name of the Workout to add (Ex. Push Day)
	:type workout_name: str
	:return: returns a Workout Object after adding it to the database
	:rtype: Workout
	"""
	db_workout_model = Workout(**workout_name.model_dump())
	session.add(db_workout_model)
	session.commit()
	session.refresh(db_workout_model)
	return db_workout_model


@app.post("/workouts/{workout_id}/exercises")
def add_exercise_to_workout(
	workout_id : int,
	exercise_to_add : ExerciseCreate,
	session : Session = Depends(get_session)
	) -> Exercise:
	workout_to_add_to = session.get(Workout, workout_id)
	if workout_to_add_to is None:
		raise HTTPException(status_code=404, detail="Workout Session doesn't exist!")
	else:
		db_exercise_to_add = Exercise(**exercise_to_add.model_dump())
		db_exercise_to_add.workout_id = workout_id
		session.add(db_exercise_to_add)
		session.commit()
		session.refresh(db_exercise_to_add)
	return db_exercise_to_add