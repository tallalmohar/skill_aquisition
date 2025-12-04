from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, select, Relationship
from datetime import datetime
from typing import Dict, Optional, List, Any
from database import create_file_db, engine, get_session


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

class ExerciseRead(SQLModel):
	to_update : str
	update_data : Any



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
	:type workout_name: WorkoutCreate

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
	"""
	Docstring for add_exercise_to_workout
	
	:param workout_id: Choose the workout you want to add to
	:type workout_id: int

	:param exercise_to_add: ExerciseCreate Object: you add name,sets,weight and reps
	:type exercise_to_add: ExerciseCreate

	:return: Returns Exercise Objects after being pushed to Databaset
	:rtype: Exercise
	"""
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


@app.get("/workouts")
def get_all_workouts(session : Session = Depends(get_session)):
	"""
	Just Returns all of the workouts 
	"""
	results = session.exec(select(Workout)).all()
	return [r for r in results]

@app.get("/workouts/{workout_id}")
def get_workout_with_id(workout_id : int, session : Session = Depends(get_session))-> List[Exercise]:
	"""
	Docstring for get_workout_with_id
	
	:param workout_id: Specific Workout that you want dependent of ID
	:type workout_id: int

	:return: A List of Exercises done on that day
	:rtype: List[Exercise]
	"""
	exercises_in_workout = session.exec(select(Exercise).where(Exercise.workout_id == workout_id)).all()
	return [e for e in exercises_in_workout]

@app.patch("/workouts/{workout_id}")
def edit_workout_name(update_name : str, workout_id : int, session : Session = Depends(get_session))-> Workout:
	"""
	Docstring for edit_workout_name
	
	:param update_name: New Workout Name
	:type update_name: str
	:param workout_id: Workout_id to Select the one you want to change
	:type workout_id: int

	:return: New Workout Name
	:rtype: Workout
	"""
	workout_to_edit = session.get(Workout,workout_id)
	workout_to_edit.workout_name = update_name
	session.commit()
	session.refresh(workout_to_edit)
	return workout_to_edit


@app.patch("/workouts/{exercise_id}",response_model=ExerciseRead)
def update_exercise(exercise_id : int, to_update: str, update_data : Any , session : Session = Depends(get_session))->Exercise:
	exercise_to_edit = session.get(Exercise,exercise_id)
	if to_update.lower() == "reps":
		exercise_to_edit.reps = update_data
	elif to_update.lower() == "sets":
		exercise_to_edit.sets = update_data
	elif to_update.lower() == "weight":
		exercise_to_edit.weight = update_data
	session.commit()
	session.refresh(exercise_to_edit)
	return exercise_to_edit