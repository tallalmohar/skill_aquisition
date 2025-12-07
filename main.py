from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, select, Relationship
from datetime import datetime
from typing import Dict, Optional, List, Any
from database import create_file_db, get_session


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
	exercise_name : str
	sets : int
	reps : int
	weight : float

class WorkoutReadWithExercises(SQLModel):
	workout_name : Optional[str] = None
	date : Optional[datetime] = None
	exercises : List[ExerciseRead]

class ExerciseUpdate(SQLModel):
	sets : Optional[int] = None
	reps : Optional[int] = None
	weight : Optional[float] = None



app = FastAPI()

@app.on_event("startup")
def create_db():
	create_file_db()

@app.get("/")
def health() -> Dict[str, str | float]:
	return {"health" : "active", "version" : 1.0}

@app.get("/workouts/recents")
def get_all_workouts_DESC_dates(session : Session = Depends(get_session)):
	"""
	Just Returns all recent workouts with descending dates
	"""
	results = session.exec(select(Workout).order_by(Workout.date.desc())).all()
	if not results:
		raise HTTPException(status_code=404, detail="No Workouts have been created")

	return [r for r in results]

@app.get("/workouts",response_model=List[WorkoutReadWithExercises])
def get_all_workouts(session : Session = Depends(get_session)):
	"""
	Just Returns all of the workouts 
	"""
	from sqlalchemy.orm import selectinload

	statement = select(Workout).options(selectinload(Workout.exercises))
	results = session.exec(statement).all()
	if not results:
		raise HTTPException(status_code=404, detail="No Workouts have been created")

	return results



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


@app.post("/workouts/exercises/{workout_id}")
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

	db_exercise_to_add = Exercise(**exercise_to_add.model_dump())
	db_exercise_to_add.workout_id = workout_id
	session.add(db_exercise_to_add)
	session.commit()
	session.refresh(db_exercise_to_add)
	return db_exercise_to_add




@app.get("/workouts/id/{workout_id}")
def get_workout_with_id(workout_id : int, session : Session = Depends(get_session))-> List[Exercise]:
	"""
	Docstring for get_workout_with_id
	
	:param workout_id: Specific Workout that you want dependent of ID
	:type workout_id: int

	:return: A List of Exercises done on that day
	:rtype: List[Exercise]
	"""
	exercises_in_workout = session.exec(select(Exercise).where(Exercise.workout_id == workout_id)).all()
	if not exercises_in_workout :
		raise HTTPException(status_code=404, detail="No Exercises have been added to Workout")

	return [e for e in exercises_in_workout]

@app.patch("/workouts/id/{workout_id}")
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
	if workout_to_edit is None:
		raise HTTPException(status_code=404, detail="Workout doesn't exist!")

	workout_to_edit.workout_name = update_name
	session.commit()
	session.refresh(workout_to_edit)
	return workout_to_edit

@app.patch("/workouts/exercises/{exercise_id}")
def update_exercise(
		exercise_id : int,
		updated_data : ExerciseUpdate,
		session : Session = Depends(get_session)
)-> Exercise :
	"""
	Docstring for update_exercise
	
	:param exercise_id: Exercise you want to update 
	:type exercise_id: int
	:param updated_data: Send the updated data, it only updates the part's being sent
	:type updated_data: ExerciseUpdate

	:return: Description
	:rtype: Exercise
	"""

	exercise_to_edit = session.get(Exercise,exercise_id)
	if exercise_to_edit is None:
		raise HTTPException(status_code=404,detail="Excercise Not FOUND!!")
	
	exercise_dict = updated_data.model_dump(exclude_unset=True)
	exercise_to_edit.sqlmodel_update(exercise_dict)
	session.add(exercise_to_edit)
	session.commit()
	session.refresh(exercise_to_edit)
	return exercise_to_edit

@app.delete("/workouts/id/{workout_id}")
def delete_workouts(workout_id : int, session : Session = Depends(get_session))-> None:
	"""
	Docstring for delete_workouts
	
	:param workout_id: The Workout you want to delete. This will delete the related exercises
	:type workout_id: int
	"""
	workout_to_delete = session.get(Workout, workout_id)
	if workout_to_delete is None:
		raise HTTPException(status_code=404,detail="Workout Doesn't exist!")
	session.delete(workout_to_delete)
	session.commit()

@app.delete("/exercise/{exercise_id}")	
def delete_exercise(exercise_id : int, session: Session = Depends(get_session)) -> None:
	"""
	Docstring for delete_exercise
	
	:param exercise_id: The exercise you want to delete 
	:type exercise_id: int
	"""
	exercise_to_delete = session.get(Exercise, exercise_id)
	if exercise_to_delete is None:
		raise HTTPException(status_code=404,detail="Exercise doesn't Exist!")
	
	session.delete(exercise_to_delete)
	session.commit()

