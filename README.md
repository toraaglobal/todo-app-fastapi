## Full Stack App with FastAPI and Vercel
* We will create an app that manages a to-do list, a list of tasks that you want to complete.

#### As always, it is recommended to create a virtual environment

## Part 1: Backend with FastAPI and Postgres

#### Create the app folder

#### Inside the app folder, create the backend folder

#### You will need to have Postgres installed


```python
#brew install postgresql
#brew services start postgresql
```

#### Install the necessary packages


```python
#pip install fastapi "uvicorn[standard]" alembic psycopg2 pytest requests pydantic_settings
```

#### Save them in requirements.txt


```python
#pip freeze > requirements.txt
```

#### Create the Postgress database


```python
#createdb mydatabase
```

#### Inside the backend folder, create the .env file and enter DB credentials like this


```python
# DATABASE_HOST=localhost
# DATABASE_NAME=mydatabase
# DATABASE_USER=postgres
# DATABASE_PASSWORD=
# DATABASE_PORT=5432
# APP_NAME="Full Stack To Do App"
```

#### Create config.py file
* Pydantic settings


```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    app_name: str = "Full Stack To Do App"

    class Config:
        env_file = ".env"
        extra = "ignore"
```

#### Create main.py file
* Create app
* CORS configuration for next frontend development
* Global HTTP exception handler
* Two endpoints:
    * Root (home page)
    * items/{item_id}

#### Start server


```python
#uvicorn main:app --reload
```

#### Check the app in http://127.0.0.1:8000/
* In the terminal, check if the app name is printed

#### Alternative way to check the app from a second window of your terminal


```python
#curl http://localhost:8000
```

#### Another alternative to check the app from a second window of your terminal


```python
#pip install httpie
#http http://localhost:8000
```

#### After the initial check, now close the app and set the database migrations


```python
#ctrl-c to stop the server in the terminal
```


```python
#alembic init alembic
```

The `alembic init alembic` command is used to initialize Alembic in a project. Alembic is a database migration library for Python, commonly used with SQLAlchemy (an object-relational mapping tool for Python). This command sets up Alembic so it can be used to handle database versioning in your project.

When you run `alembic init alembic`, the following happens:

1. **Creation of Directory Structure**: The command creates a new directory named `alembic` in your project. Within this directory, Alembic stores migration scripts and some configuration files.

2. **Configuration File**: It generates an `alembic.ini` file in the root directory of your project. This file contains the necessary configuration for Alembic to connect to your database and other relevant settings.

3. **Versions Directory**: Inside the `alembic` directory, a subdirectory named `versions` is created. This directory will house the individual migration scripts you create to modify your database (for example, to add tables, change schemas, etc.).

4. **`env.py` File**: An `env.py` file is also created in the `alembic` directory. This file is the entry point for Alembic and is used to configure the migration context, database connection, and other aspects of the migration environment.

The purpose of using Alembic is to facilitate tracking and applying changes to the database schema in a controlled and consistent manner. It allows for incremental versions to be applied to the database, which is crucial in development, testing, and production environments, especially in large teams where multiple developers may be making changes to the database.

#### Edit alembic/env.py
* To have access to the .env file, add the following lines:


```python
from dotenv import load_dotenv
load_dotenv()
```

Insert next line after line 13:


```python
#import os
config.set_main_option("sqlalchemy.url", f"postgresql://{os.environ['DATABASE_USER']}:@{os.environ['DATABASE_HOST']}:{os.environ['DATABASE_PORT']}/{os.environ['DATABASE_NAME']}")
```

#### Create todos table from terminal


```python
alembic revision -m "create todos table"
```

#### Check the updates in alambic/versions

#### Edit xxx_create_todos_table.py to define the schema of the new table


```python
def upgrade():
    op.execute("""
    create table todos(
        id bigserial primary key,
        name text,
        completed boolean not null default false
    )
    """)

def downgrade():
    op.execute("drop table todos;")
```

#### Run the migration from terminal


```python
#psql -d mydatabase
```


```python
#CREATE USER user12 WITH PASSWORD 'pass12';
```


```python
#GRANT ALL PRIVILEGES ON DATABASE mydatabase TO user12;
```

NOTE: Our Honor Student **Robert Merchant** discovered that in the last PostgreSQL version (v. 15) is necessary to add also the following line:


```python
#GRANT ALL PRIVILEGES ON SCHEMA public TO user12;
```

You can find more info about this PostgreSQL update [here](https://stackoverflow.com/questions/67276391/why-am-i-getting-a-permission-denied-error-for-schema-public-on-pgadmin-4).

Thanks Robert!!! You make us all better :)


```python
#\q
```

Alternativa a lo anterior:


```python
#psql -U your_superadmin_username -h localhost -d mydatabase
```

#### Edit this line in alembic.ini


```python
sqlalchemy.url = postgresql://user12:pass12@localhost/llm 
```

#### Edit .env


```python
# DATABASE_USER=user12
# DATABASE_PASSWORD=pass12
```

#### Run the database migration from terminal


```python
#alembic upgrade head
```

#### Check the database in terminal


```python
#psql mydatabase
#\dt
select * from todos
#\q
```

#### Set up the schemas
* Create the file schemas.py in the root directory of the app
* It defines the data model: data structure, type, validation and extra configuration
* ToDoRequest is a data model with 2 data types
* ToDoResponse is a data model with 3 data types
* Config defines an extra configuration in ToDoResponse
    * orm_mode = True allows the model to work with ORMs like SQLAlchemy. Useful when we retrieve data from a database using a ORM (Object-Relational Mapping) and deliver those data in a structured format through an API.
    * because we want to serialize our database entities (convert Python objects into JSON format)


```python
from pydantic import BaseModel

class ToDoRequest(BaseModel):
    name: str
    completed: bool

class ToDoResponse(BaseModel):
    name: str
    completed: bool
    id: int

    class Config:
        orm_mode = True
```

#### Create the ORM (Object-Relational Mapping)
* Create the file database.py in the root directory of the app
* create_engine connects with the database
* sessionmaker allows to interact with the database
* declarative_base creates a base class for the models of the database, that will be all the tables


```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:@{os.environ['DATABASE_HOST']}/{os.environ['DATABASE_NAME']}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

#### Create models.py
* This is where we will define the database model using SQLAlquemy, a ORM library very popular in Python.
* Using SQLAlchemy we can interact with the table usign ToDo objects instead of writing SQL commands manually.
* The model represents the table ToDo in a database.
* Column, Integer, String and Boolean are column types.
* `__tablename__` assigns a name to the table


```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    completed = Column(Boolean, default=False)
```

#### Create crud.py
* With our CRUD (Create, Read, Update, Delete) helpers
* We import the `model` and `schema` we have defined earlier
* `Session` is used to manage the database operations
* `create_todo` creates a new todo task in the dababase
    * `db: Session` is a SQLAlchemy session to interact with the database
    * `todo: schemas.ToDoRequest` is a Pydantic object with the data of the new todo task
    *  `db_todo` creates a new ToDo task
    *  `db_add` adds the new ToDo task to the database Session
    *  `db.commit` saves the changes in the database
    *  `db.refresh` updates the database
    *  returns the `db_todo` object

* `read_todos` displays all the non-completed todo tasks
    * if all completed, displays all the todo tasks completed

* `read_todo` display the todo task identified with the id

* `uddate_todo` updates the todo task idenfitied with the id
    * if the task does not exist, it returns `None`
    * if the tasks exists, it updates it and saves it
      
* `delete_todo` deletes the todo task identified with the id
    * if the task does not exist, it returns `None`
    * if the tasks exists, it deletes it and saves the changes


```python
from sqlalchemy.orm import Session
import models, schemas

def create_todo(db: Session, todo: schemas.ToDoRequest):
    db_todo = models.ToDo(name=todo.name, completed=todo.completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def read_todos(db: Session, completed: bool):
    if completed is None:
        return db.query(models.ToDo).all()
    else:
        return db.query(models.ToDo).filter(models.ToDo.completed == completed).all()

def read_todo(db: Session, id: int):
    return db.query(models.ToDo).filter(models.ToDo.id == id).first()

def update_todo(db: Session, id: int, todo: schemas.ToDoRequest):
    db_todo = db.query(models.ToDo).filter(models.ToDo.id == id).first()
    if db_todo is None:
        return None
    db.query(models.ToDo).filter(models.ToDo.id == id).update({'name': todo.name, 'completed': todo.completed})
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, id: int):
    db_todo = db.query(models.ToDo).filter(models.ToDo.id == id).first()
    if db_todo is None:
        return None
    db.query(models.ToDo).filter(models.ToDo.id == id).delete()
    db.commit()
    return True
```

#### Set up the router
* Create the new file routers/todos.py
* FastAPI API CRUD routes
* APIRouter creates the API router with the prefix /todos
* `get_db` opens and closes a SQLAlchemy session
* `Depends(get_db)` injects a db session on each route

* `@router.post`: route to create a new todo task
    * `schemas.ToDoRequest` is the model that validates the data types
    * uses the `create_todo` function defined in crud.py

* `@router.get("")` en `/todos`: route to display all tasks
    * uses the `read_todos` function defined in crud.py
    * can filter tasks based on `completed` status
 
* `@router.get("/{id}")`: route to display one task by id
    * uses the `read_todo` function defined in crud.py
    * if it is not found, it returns a 404 error message

* `@router.put("/{id}")`: route to update one task by id
    * uses the `update_todo` function defined in crud.py

* `@router.delete("/{id}")`: route to display one task by id
    * uses the `delete_todo` function defined in crud.py


```python
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import schemas
import crud
from database import SessionLocal

router = APIRouter(
    prefix="/todos"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.ToDoRequest, db: Session = Depends(get_db)):
    todo = crud.create_todo(db, todo)
    return todo

@router.get("", response_model=List[schemas.ToDoResponse])
def get_todos(completed: bool = None, db: Session = Depends(get_db)):
    todos = crud.read_todos(db, completed)
    return todos

@router.get("/{id}")
def get_todo_by_id(id: int, db: Session = Depends(get_db)):
    todo = crud.read_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="to do not found")
    return todo

@router.put("/{id}")
def update_todo(id: int, todo: schemas.ToDoRequest, db: Session = Depends(get_db)):
    todo = crud.update_todo(db, id, todo)
    if todo is None:
        raise HTTPException(status_code=404, detail="to do not found")
    return todo

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_todo(id: int, db: Session = Depends(get_db)):
    res = crud.delete_todo(db, id)
    if res is None:
        raise HTTPException(status_code=404, detail="to do not found")
```

#### Uncomment these two lines in main.py


```python
#from routers import todos
#app.include_router(todos.router)
```

#### Run the server from the terminal


```python
#uvicorn main:app --reload
```

#### In a second terminal window, make the following tests (need httpie installed)

Create one to-do task:


```python
#http POST http://localhost:8000/todos name="walk Fido" completed=false
```

Display all the to-do tasks:


```python
#http GET http://localhost:8000/todos
```

Display the to-do task with the id=1:


```python
#http GET http://localhost:8000/todos/1
```

Update it changing completed to true:


```python
#http PUT http://localhost:8000/todos/1 name="walk Fido" completed=true
```

Display all the to-do tasks:


```python
#http GET http://localhost:8000/todos
```

Create a second to-do task:


```python
#http POST http://localhost:8000/todos name="feed Fido" completed=false
```

Display all the to-do tasks:


```python
#http GET http://localhost:8000/todos
```

Delete the to-do task with the id=1:


```python
#http DELETE http://localhost:8000/todos/1
```

Display all the to-do tasks:


```python
#http GET http://localhost:8000/todos
```

The following should get a "to do not found" message


```python
#http GET http://localhost:8000/todos/1
```

## Part 2: Frontend with Next.js

#### Create the frontend app using a Next.js starter template


```python
#npx create-next-app@latest
```

#### Enter this configuration options:
* app name: todo-app
* typescript: no
* eslint: yes
* tailwind css: no
* src/ directory: no
* app router: no
* customize import alias: no

#### Go to the main folder of the frontend app and enter npm run dev to run the frontend app in the browser


```python
#cd todo-app
#npm run dev
```

#### Check how the starter template looks in your browser
* open browser in localhost:3000

#### Open the starter template in your editor
* What you will see is the UI of the default Next.js template

#### Create the .env file
* Enter the URL of the backend API
* This is a Next.js convention: any variable starting with NEXT_PUBLIC_ will be available in the client side and in the server side.


```python
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Edit pages/index.js
* remove the default content provided for this file
* the following content imports 2 next.js components we have not created yet:
    * Layout (we can re-use this component in any page).
    * ToDoList (all of our TODO functionality).

* The ToDoList component will be inside the Layout component. This is called "composition".


```python
import Head from 'next/head'
import Layout from '../components/layout';
import ToDoList from '../components/todo-list';

export default function Home() {
  return (
    <div>
      <Head>
        <title>Full Stack Book To Do</title>
        <meta name="description" content="Full Stack Book To Do" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Layout>
        <ToDoList />
      </Layout>
    </div>
  )
}
```

#### Create the components folder in the root directory

#### Create the components/layout.js file
* Imports css styles that are not created yet
* Defines a React component called Layout
    * This component accepts the parameter props
    * React components use JSX syntax, very similar to HTML
    * The {props.children} is where we use composition, this means that we can replace this with another React component when we use the Layout component anywhere.


```python
import styles from '../styles/layout.module.css'

export default function Layout(props) {
  return (
    <div className={styles.layout}>
      <h1 className={styles.title}>To Do</h1>
      {props.children}
    </div>
  )
}
```

### Create the components/todo-list.js file
* Will require to install lodash. In terminal: npm install lodash
* Imports css that is still not created.
* Imports ToDo from a file not yet created.


```python
import styles from '../styles/todo-list.module.css'
import { useState, useEffect, useCallback, useRef } from 'react'
import { debounce } from 'lodash'
import ToDo from './todo'
```


```python
export default function ToDoList() {
```

#### Global explanation of this component

This code is for a React component called `ToDoList`, which is part of a web application for managing a list of tasks or "todos". Here's a simple breakdown of what this component does:

1. **Imports and Setup**:
   - CSS styles are imported for use in the component.
   - Several hooks from React (`useState`, `useEffect`, `useCallback`, `useRef`) and a utility (`debounce` from `lodash`) are imported. These are used for managing state, side effects, and optimizing function calls.
   - The `ToDo` component is also imported, which is used to render each todo item.

2. **Component State Management**:
   - `useState` is used to create several state variables: `todos` (the list of todo items), `mainInput` (the value of a main input field for adding new todos), and `filter` (to filter the displayed todos).
   - `useRef` is used to create a ref (`didFetchRef`) for tracking if the todos have been fetched.

3. **Fetching Todos on Component Mount**:
   - `useEffect` is used to fetch the list of todos when the component first renders. It checks `didFetchRef` to ensure fetching only occurs once.

4. **Functions for Handling Todos**:
   - `fetchTodos` fetches todos from an API, possibly filtered by completion status.
   - `debouncedUpdateTodo` is a debounced version of an `updateTodo` function, used for updating todos with a delay to improve performance.
   - `handleToDoChange` handles changes to todo items (like marking them as completed).
   - `updateTodo` updates a todo item in the backend.
   - `addToDo` adds a new todo to the list.
   - `handleDeleteToDo` deletes a todo item.

5. **Handling User Input**:
   - `handleMainInputChange` updates the `mainInput` state when the user types in the input field.
   - `handleKeyDown` checks for the 'Enter' key to add a new todo.

6. **Filtering Todos**:
   - `handleFilterChange` updates the filter state and fetches todos based on the selected filter.

7. **Rendering the Component**:
   - The `return` statement contains the JSX (HTML-like syntax) for rendering the component.
   - It includes an input field for adding new todos, a loading message, a list of todos (using the `ToDo` component for each item), and buttons for filtering the todos by different criteria (all, active, completed).

In simple terms, the `ToDoList` component allows users to add, view, filter, and delete todo items. It interacts with an API for data fetching and updating, and it uses various React features for handling state, effects, and user interactions.

#### Step-by-step explanation


```python
  const [todos, setTodos] = useState(null)
  const [mainInput, setMainInput] = useState('')
  const [filter, setFilter] = useState()
  const didFetchRef = useRef(false)
```

The previous code is a typical use of React's `useState` and `useRef` hooks in a functional component. Let's break down what each line does in simple terms:

1. **`const [todos, setTodos] = useState(null)`**:
   - This line creates a state variable named `todos` with a corresponding setter function `setTodos`.
   - `useState(null)` initializes `todos` with a value of `null`.
   - You can use `setTodos` to update the value of `todos` later in the component. When you do, it triggers the component to re-render with the new value.

2. **`const [mainInput, setMainInput] = useState('')`**:
   - Similarly, this line creates another state variable `mainInput` with its setter function `setMainInput`.
   - It's initialized with an empty string `''`. This might be used, for instance, to track the value of a text input field in your UI.
   - `setMainInput` can be used to update `mainInput`, triggering a re-render with the updated value.

3. **`const [filter, setFilter] = useState()`**:
   - This line creates a state variable `filter` with a setter `setFilter`.
   - Since `useState()` is called without any argument, `filter` is initialized as `undefined`.
   - `setFilter` can be used to update the value of `filter` for various purposes, like applying a filter to the list of `todos`.

4. **`const didFetchRef = useRef(false)`**:
   - This line uses the `useRef` hook to create a mutable ref object called `didFetchRef`.
   - The ref is initialized with the value `false`. Unlike state variables, changing the value of a ref does not cause the component to re-render.
   - This ref can be used to track whether a certain action (like data fetching) has already been performed without re-triggering renders.

In summary, this code sets up two pieces of state (`todos` and `mainInput`, with `filter` being optional) to track and update component data, and uses a ref (`didFetchRef`) as a persistent variable that doesn't cause re-renders when its value changes. This pattern is common in functional components for managing both the UI state and certain actions like data fetching.


```python
  useEffect(() => {
    if (didFetchRef.current === false) {
      didFetchRef.current = true
      fetchTodos()
    }
  }, [])
```

The previous code uses the `useEffect` hook in React, which is a way to perform side effects in functional components. Let's break down what the code does in simple terms:

1. **`useEffect(() => {...}, [])`:**
   - `useEffect` is a hook that runs some code based on certain conditions.
   - The empty array `[]` as the second argument to `useEffect` means that the code inside the `useEffect` will run only once, right after the initial render of the component. This is similar to the `componentDidMount` lifecycle method in class components.

2. **`if (didFetchRef.current === false) {...}`:**
   - Inside `useEffect`, there's an `if` statement that checks the value of `didFetchRef.current`.
   - `didFetchRef` is a ref created with the `useRef` hook, and it's used here to track whether some action has already been taken. In this case, it's checking whether a function to fetch data (`fetchTodos`) has been called.

3. **`didFetchRef.current = true`:**
   - If `didFetchRef.current` is `false` (meaning `fetchTodos` hasn't been called yet), the code sets `didFetchRef.current` to `true`.
   - This is done to ensure that the data-fetching function only runs once.

4. **`fetchTodos()`:**
   - This is a call to a function named `fetchTodos`, which likely fetches data from an API or some external source.
   - The function is called inside the `if` statement to make sure it only runs the first time the component is rendered.

In simple terms, this `useEffect` hook is used to run the `fetchTodos` function only once after the component is first rendered, and `didFetchRef` is used to ensure that this function doesn't run more than once. This pattern is useful for fetching data that you only need to load once when the component initially appears on the screen.


```python
  async function fetchTodos(completed) {
    let path = '/todos'
    if (completed !== undefined) {
      path = `/todos?completed=${completed}`
    }
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + path)
    const json = await res.json()
    setTodos(json)
  }
```

The code snippet defines an asynchronous function named `fetchTodos` that is used for fetching a list of todo items (tasks) from an external source (like a server or an API). Here's a breakdown of what each part of the function does:

1. **`async function fetchTodos(completed) {...}`:**
   - `async` indicates that this function is asynchronous, meaning it can perform tasks that take some time to complete (like fetching data from an API) without blocking other code from running.
   - `fetchTodos` is the name of the function.
   - `completed` is a parameter that the function can accept. It's used to determine which todos to fetch based on their completion status.

2. **Determine the API Path:**
   - Initially, `path` is set to `'/todos'`, which seems to be the endpoint for fetching todos.
   - If `completed` is not `undefined`, the function modifies the `path` to include a query parameter `completed`. This is likely used to filter the todos based on whether they are completed or not on the server-side.

3. **Fetch the Data:**
   - The function uses the `fetch` API to make a network request to the provided URL, which is constructed using `process.env.NEXT_PUBLIC_API_URL` (the base URL of the API) and the `path`.
   - `await` is used to wait for the response from `fetch`. This is possible because the function is asynchronous.

4. **Process the Response:**
   - Once the response is received, `res.json()` is called to convert the response into a JSON format. Again, `await` is used to wait for this process to complete.
   - The JSON data, presumably a list of todo items, is then stored in a variable named `json`.

5. **Update State with Fetched Data:**
   - Finally, the function updates the component's state by calling `setTodos(json)`. This updates the `todos` state with the fetched data, likely causing the component to re-render and display the new list of todos.

In simple terms, `fetchTodos` is a function that fetches a list of todo items from a server and updates the component's state with these items. The function can also filter the todos based on their completion status if the `completed` parameter is provided.


```python
const debouncedUpdateTodo = useCallback(debounce(updateTodo, 500), [])
```

The previous line of code uses two React hooks, `useCallback` and `debounce` from the `lodash` library, to create a debounced version of an `updateTodo` function. Let's break it down:

1. **`updateTodo` Function**: This is presumably a function that performs some update operation, like updating a todo item. Such operations are often tied to user input or other rapid interactions.

2. **`debounce(updateTodo, 500)`**:
   - `debounce` is a function from the `lodash` library that limits the rate at which a function can fire.
   - When you wrap `updateTodo` with `debounce`, you create a new function that will only execute `updateTodo` after it hasn't been called for 500 milliseconds.
   - This is useful for reducing the number of times `updateTodo` is called, which can be beneficial for performance, especially if `updateTodo` involves network requests or other heavy computations.

3. **`useCallback` Hook**:
   - `useCallback` is a React hook that returns a memoized version of the callback function that only changes if one of the dependencies has changed.
   - In this case, `useCallback` is used to memoize the debounced version of `updateTodo`. The empty dependency array `[]` means that the memoized function will only be created once and will not change on subsequent renders of the component.

4. **`const debouncedUpdateTodo`**:
   - The debounced function is stored in a constant named `debouncedUpdateTodo`. 
   - You can now use `debouncedUpdateTodo` in your component in place of `updateTodo` for operations that you want to debounce, like handling real-time input changes.

In simple terms, this code creates a version of the `updateTodo` function that will only be triggered if there's a pause of 500 milliseconds between invocations, preventing it from running too frequently. This can improve performance and user experience, especially in cases of rapidly firing events like typing in a search bar or resizing a window.


```python
  function handleToDoChange(e, id) {
    const target = e.target
    const value = target.type === 'checkbox' ? target.checked : target.value
    const name = target.name
    const copy = [...todos]
    const idx = todos.findIndex((todo) => todo.id === id)
    const changedToDo = {
      ...todos[idx],
      [name]: value
    }
    copy[idx] = changedToDo
    debouncedUpdateTodo(changedToDo)
    setTodos(copy)
  }
```

The previous code defines a function named `handleToDoChange` in a React component. The function is designed to handle changes to todo items (like updating a task's status or content). Let's break it down into simpler terms:

1. **Function Definition**:
   - `handleToDoChange` is a function that takes two parameters: `e` (an event object from a user interaction, like typing in a text field or checking a checkbox) and `id` (the unique identifier of a todo item).

2. **Extracting Information from the Event**:
   - `const target = e.target`: Gets the target element that triggered the event.
   - `const value = target.type === 'checkbox' ? target.checked : target.value`: Determines the value to be updated. If the target element is a checkbox, it uses the `checked` property; otherwise, it uses the `value` property.
   - `const name = target.name`: Gets the name of the target element, which likely corresponds to a property of the todo item (like 'completed' or 'title').

3. **Finding and Updating the Todo Item**:
   - `const copy = [...todos]`: Creates a copy of the current list of todos. This is important for immutability, a key concept in React.
   - `const idx = todos.findIndex((todo) => todo.id === id)`: Finds the index of the todo item that needs to be updated based on its `id`.
   - Constructs a new todo object (`changedToDo`) by copying the existing todo item and updating the property corresponding to the target element's name with the new value.

4. **Updating the State**:
   - `copy[idx] = changedToDo`: Places the updated todo item back into the correct position in the copy of the todo list.
   - `debouncedUpdateTodo(changedToDo)`: Calls a debounced function to update the todo item, likely making changes persistent in a database or backend (this function is defined elsewhere).
   - `setTodos(copy)`: Updates the state of the todo list with the new, modified list. This triggers a re-render of the component with the updated data.

In simple terms, `handleToDoChange` is a function that updates the state of a todo item when a user interacts with it (like checking it off or editing its text). It ensures that changes are reflected both in the UI and, through `debouncedUpdateTodo`, potentially in a backend or database. The use of debouncing helps in optimizing performance, especially for frequent and rapid changes.


```python
  async function updateTodo(todo) {
    const data = {
      name: todo.name,
      completed: todo.completed
    }
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/todos/${todo.id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }
```

The previous code defines an asynchronous function named `updateTodo` that is used for updating a todo item in a web application. Here's a simple explanation of what it does:

1. **Asynchronous Function (`async`)**:
   - The `async` keyword indicates that the function is asynchronous, meaning it can perform operations that might take some time to complete, like sending a request to a server, without blocking other code from running.

2. **Function Purpose**:
   - The function `updateTodo` takes an argument `todo`, which is an object representing a todo item.

3. **Preparing the Data for Update**:
   - Inside the function, a new object `data` is created, containing the `name` and `completed` properties of the `todo`. This data will be sent to the server to update the corresponding todo item.

4. **Making an HTTP Request**:
   - The function then makes an HTTP request using the `fetch` function.
   - `process.env.NEXT_PUBLIC_API_URL + `/todos/${todo.id}``: This constructs the URL for the request, combining a base API URL stored in an environment variable with the specific endpoint for updating a todo (identified by `todo.id`).
   - The request is made using the `PUT` method, which is commonly used for updating resources in RESTful APIs.

5. **Sending the Data**:
   - `body: JSON.stringify(data)`: The data object is converted to a JSON string and included in the request body.
   - `headers: { 'Content-Type': 'application/json' }`: The request headers indicate that the body of the request is in JSON format.

6. **Awaiting the Response**:
   - `const res = await fetch(...)`: The `await` keyword is used to wait for the server's response. The response is stored in the variable `res`, although this code doesn't do anything with `res` after receiving it.

In simple terms, `updateTodo` is a function that sends an updated todo item to a server. It uses an asynchronous HTTP request to send the updated data (like the name of the todo and whether it's completed) to a specific API endpoint. The server can then process this request and update the todo item in the database or backend system.


```python
  async function addToDo(name) {
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/todos/`, {
      method: 'POST',
      body: JSON.stringify({
        name: name,
        completed: false
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    if (res.ok) {
      const json = await res.json();
      const copy = [...todos, json]
      setTodos(copy)
    }
  }
```

The previous code defines an asynchronous function named `addToDo` in a web application, typically one built with React. The function is designed to add a new todo item to a list. Here's a simple explanation of each part:

1. **Asynchronous Function**:
   - `async function addToDo(name) {...}`: This is an asynchronous function named `addToDo`. It takes one argument, `name`, which represents the name of the todo item to be added.
   - Being asynchronous means it can perform tasks like network requests without blocking other operations.

2. **Making a Network Request**:
   - The function sends a network request to a server using the `fetch` API.
   - The URL for the request is constructed from an environment variable (`process.env.NEXT_PUBLIC_API_URL`) and the endpoint path `/todos/`. This is where the todo item will be sent.
   - It uses the `POST` method, which is commonly used for sending data to create a new resource (in this case, a new todo item).

3. **Sending Data**:
   - The `body` of the request is a JSON string containing the new todo item data. It includes the `name` of the todo and a `completed` status, which is initially set to `false`.
   - The `headers` specify that the content being sent is in JSON format.

4. **Handling the Server Response**:
   - `await` is used to wait for the response from the server. The response is stored in the variable `res`.
   - If the response is successful (`res.ok`), the function proceeds to process the response.
   - `await res.json()` converts the response body to a JavaScript object, stored in `json`. This object likely represents the newly created todo item.

5. **Updating the Todo List**:
   - The function creates a new array `copy` by spreading the current `todos` array and adding the new todo item (`json`) to the end.
   - `setTodos(copy)` is called to update the state of the todo list with this new array. This will cause the component to re-render and display the updated list, including the newly added todo.

In simple terms, the `addToDo` function adds a new todo item to a list by sending it to a server and then updating the local state to reflect this addition. This is a common pattern in React applications for handling user input and synchronizing with a backend server.


```python
  async function handleDeleteToDo(id) {
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/todos/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    if (res.ok) {
      const idx = todos.findIndex((todo) => todo.id === id)
      const copy = [...todos]
      copy.splice(idx, 1)
      setTodos(copy)
    }
  }
```

This code defines an asynchronous function named `handleDeleteToDo` in a React application. The function is used to delete a todo item from a list. Let's break down what it does in simpler terms:

1. **Asynchronous Function**:
   - `async function handleDeleteToDo(id) {...}`: This is an asynchronous function, meaning it can perform tasks that take some time to complete (like sending a request to a server) without blocking other code from running.
   - The function takes one parameter, `id`, which is likely the unique identifier of the todo item that needs to be deleted.

2. **Sending a Network Request**:
   - The function sends a network request to a server using the `fetch` API.
   - The URL for the request is constructed from an environment variable (`process.env.NEXT_PUBLIC_API_URL`) and the specific endpoint for the todo item (`/todos/${id}`). This endpoint is used to specify which todo item should be deleted.
   - It uses the `DELETE` method, which is commonly used in web APIs to remove a resource (in this case, a todo item).

3. **Setting Request Headers**:
   - The headers indicate that the content type of the request is JSON. This is part of the HTTP protocol and helps the server understand the format of the request.

4. **Handling the Server Response**:
   - `await` is used to wait for the server's response. The response is stored in the variable `res`.
   - If the response is successful (`res.ok`), the function proceeds to update the local state.

5. **Updating the Local State**:
   - The function finds the index (`idx`) of the todo item to be deleted from the current list of todos (`todos`).
   - It then creates a copy of the todos array and removes the item at the found index using `splice(idx, 1)`.
   - Finally, `setTodos(copy)` is called to update the state with the new array of todos, which no longer includes the deleted item. This triggers a re-render of the component with the updated todo list.

In simple terms, the `handleDeleteToDo` function deletes a specific todo item by sending a request to a server, and if successful, it updates the local list of todos to reflect this deletion. This pattern is common in React applications for handling data synchronization with a backend server while keeping the UI up-to-date.


```python
  function handleMainInputChange(e) {
    setMainInput(e.target.value)
  }
```

The previous code defines a function named `handleMainInputChange` in a React component. The function is designed to handle changes in a text input field. Here's a simple explanation:

1. **Function Definition**:
   - `function handleMainInputChange(e) {...}`: This is a function that gets called whenever there is a change in a specific input field in your component.
   - It takes one parameter, `e`, which represents the event object that contains information about the change event.

2. **Updating Component State**:
   - `setMainInput(e.target.value)`: This line updates the state of the component.
   - `e.target` refers to the DOM element that triggered the event (in this case, the input field).
   - `e.target.value` is the current value of that input field after the change.
   - `setMainInput` is a function that updates the state variable `mainInput` with the new value of the input field.
   - This state update will cause the component to re-render if `mainInput` is used in the render output.

In simple terms, `handleMainInputChange` is a function that updates the `mainInput` state of the component with the new value from a text input field every time the user types or changes the content in that field. This is a common pattern in React for handling user input and keeping the component's state in sync with the UI.


```python
  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      if (mainInput.length > 0) {
        addToDo(mainInput)
        setMainInput('')
      }
    }
  }
```

The previous code defines a function named `handleKeyDown` in a React component. The function is designed to respond to keyboard events, specifically when a key is pressed. Let's break it down:

1. **Function Definition**:
   - `function handleKeyDown(e) {...}`: This is a function that gets called whenever a key is pressed in an element that this function is attached to (like an input field).
   - The parameter `e` represents the event object that contains information about the key press event.

2. **Checking the Pressed Key**:
   - `if (e.key === 'Enter') {...}`: This line checks if the key pressed is the 'Enter' key. The `key` property of the event object holds the value of the key that was pressed.

3. **Conditionally Adding a Todo Item**:
   - `if (mainInput.length > 0) {...}`: This condition checks if the `mainInput` (presumably a state variable tracking the current value of an input field) is not empty.
   - If `mainInput` is not empty and the 'Enter' key was pressed, the function then proceeds to execute two actions:
     - `addToDo(mainInput)`: This calls a function `addToDo` and passes `mainInput` as an argument. It's likely that `addToDo` is a function for adding a new todo item with the text from `mainInput`.
     - `setMainInput('')`: This resets the `mainInput` state to an empty string, clearing the input field. This is typically done after the input value has been used (like after adding the todo item).

In simple terms, the `handleKeyDown` function is designed to listen for a key press event, and when the 'Enter' key is pressed, it checks if there is any text in the `mainInput`. If there is, it adds a new todo item with this text and then clears the input field. This kind of functionality is common in todo list applications, allowing users to add items to their list by typing text into an input field and pressing 'Enter'.


```python
  function handleFilterChange(value) {
    setFilter(value)
    fetchTodos(value)
  }
```

The previous code defines a function named `handleFilterChange` in a React component. The function is designed to handle changes in the way todo items are filtered. Let's simplify each part:

1. **Function Definition**:
   - `function handleFilterChange(value) {...}`: This is a function that likely gets called when a user interacts with some sort of filter control, like buttons or a dropdown menu.
   - The parameter `value` represents the new filter option selected by the user.

2. **Updating the Filter State**:
   - `setFilter(value)`: This line updates the component's state for the filter criteria.
   - `setFilter` is a function that changes the state variable `filter` to the new value provided. This probably controls what todos are currently being shown based on the filter (like 'all', 'completed', 'active').

3. **Fetching Filtered Todos**:
   - `fetchTodos(value)`: After updating the filter state, the function calls `fetchTodos`, passing the new filter value.
   - `fetchTodos` is likely a function that fetches the todo items based on the selected filter criteria. For example, it could make a network request to a server to get all todos, only completed todos, or only active todos, depending on the filter value.

In simple terms, `handleFilterChange` is a function that updates which todo items are displayed based on a selected filter. It does this by updating the filter state and then fetching the todo items that match this new filter criteria. This is a common pattern in applications where you need to display different subsets of data based on user selection or interaction.


```python
  return (
    <div className={styles.container}>
      <div className={styles.mainInputContainer}>
        <input className={styles.mainInput} placeholder="What needs to be done?" value={mainInput} onChange={(e) => handleMainInputChange(e)} onKeyDown={handleKeyDown}></input>
      </div>
      {!todos && (
        <div>Loading...</div>
      )}
      {todos && (
        <div>
          {todos.map((todo) => {
            return (
              <ToDo key={todo.id} todo={todo} onDelete={handleDeleteToDo} onChange={handleToDoChange} />
            )
          })}
        </div>
      )}
      <div className={styles.filters}>
        <button className={`${styles.filterBtn} ${filter === undefined && styles.filterActive}`} onClick={() => handleFilterChange()}>All</button>
        <button className={`${styles.filterBtn} ${filter === false && styles.filterActive}`} onClick={() => handleFilterChange(false)}>Active</button>
        <button className={`${styles.filterBtn} ${filter === true && styles.filterActive}`} onClick={() => handleFilterChange(true)}>Completed</button>
      </div>
    </div>
  )
```

The previous code is the part of a React component (`ToDoList`) that describes what the component should render on the screen, also known as the JSX return block. Here's a simple explanation of each part:

1. **Container Div**:
   - The entire component is wrapped in a `<div>` element with a `className` of `styles.container`, applying CSS styles to the overall layout.

2. **Input for Adding Todos**:
   - Inside the container, there is a `<div>` for the main input field, styled with `styles.mainInputContainer`.
   - An `<input>` element is used for entering new todo items. It has:
     - A `placeholder` text "What needs to be done?" to guide the user.
     - Its value is tied to the `mainInput` state variable, so it displays what's currently in `mainInput`.
     - Event handlers `onChange` and `onKeyDown` are attached to it. These call `handleMainInputChange` when the input changes and `handleKeyDown` when a key is pressed, respectively.

3. **Loading Message**:
   - `{!todos && <div>Loading...</div>}`: This line checks if `todos` is not yet available (like it's `null` or `undefined`). If so, it displays a "Loading..." message. This is likely a placeholder while the todos are being fetched from an API.

4. **Displaying Todos**:
   - `{todos && <div>...</div>}`: This checks if `todos` is available. If it is, it goes through each todo item and renders it.
   - `todos.map(...)` is a JavaScript function that iterates over each item in the `todos` array.
   - For each `todo` item, it renders a `ToDo` component, passing the todo item, and functions `handleDeleteToDo` and `handleToDoChange` as props. This means each todo item will have its own display and functionality, like being able to be deleted or changed.

5. **Filter Buttons**:
   - There are three buttons for filtering the displayed todos: All, Active, and Completed.
   - Each button has an `onClick` handler that calls `handleFilterChange` with different values (`undefined`, `false`, `true`) to change the current filter.
   - The buttons are styled, and their style changes based on the current filter value to visually indicate which filter is active.

In simple terms, this part of the `ToDoList` component creates the user interface for the todo list application. It includes an input field for adding new todos, displays a loading message if the todos are still being fetched, shows the list of todos once they are available, and provides buttons to filter the displayed todos.

## Create the /components/todo.js file


```python
import Image from 'next/image'
import styles from '../styles/todo.module.css'

export default function ToDo(props) {
  const { todo, onChange, onDelete } = props;
  return (
    <div className={styles.toDoRow} key={todo.id}>
      <input className={styles.toDoCheckbox} name="completed" type="checkbox" checked={todo.completed} value={todo.completed} onChange={(e) => onChange(e, todo.id)}></input>
      <input className={styles.todoInput} autoComplete='off' name="name" type="text" value={todo.name} onChange={(e) => onChange(e, todo.id)}></input>
      <button className={styles.deleteBtn} onClick={() => onDelete(todo.id)}><Image src="/delete-outline.svg" width="24" height="24" /></button>
    </div>
  )
}
```

The previous code is for a React component called `ToDo`, typically used in a todo list application built with Next.js. The component is designed to display and interact with a single todo item. Here's a breakdown of the code in simple terms:

1. **Imports**:
   - `Image` from 'next/image': This is a Next.js optimized image component that allows for efficient image loading.
   - `styles` from a CSS module: This imports specific CSS styles for the component.

2. **Component Function `ToDo`**:
   - `export default function ToDo(props) {...}`: This defines the `ToDo` component. It is a functional component that takes `props` as its argument.
   - `const { todo, onChange, onDelete } = props;`: This line extracts the `todo`, `onChange`, and `onDelete` properties from `props`. These are likely passed from the parent component and contain the todo item data and functions for handling changes and deletion.

3. **Rendering the Todo Item**:
   - The component returns JSX (a syntax extension for JavaScript used with React) that describes the structure of the UI for the todo item.
   - `<div className={styles.toDoRow} key={todo.id}>`: This `div` acts as a container for the todo item. It uses styles from the imported CSS module and a unique `key` based on the todo's `id`.

4. **Todo Checkbox**:
   - `<input className={styles.toDoCheckbox} ...>`: This is a checkbox input that allows marking the todo item as completed or not. 
   - `checked={todo.completed}`: The checkbox is checked or unchecked based on the `completed` property of the `todo` object.
   - `onChange={(e) => onChange(e, todo.id)}`: This sets up a handler so that when the checkbox changes, the `onChange` function is called with the event `e` and the `id` of the todo.

5. **Todo Text Input**:
   - `<input className={styles.todoInput} ...>`: This is a text input field for the todo item's name.
   - `value={todo.name}`: The input displays the name of the todo.
   - The `onChange` handler here works similarly to the checkbox, allowing the name of the todo to be edited.

6. **Delete Button**:
   - `<button className={styles.deleteBtn} ...>`: This is a button for deleting the todo item.
   - `onClick={() => onDelete(todo.id)}`: When the button is clicked, the `onDelete` function is called with the `id` of the todo.
   - The button includes an `<Image>` component, which displays an icon from a provided source (`/material-symbols_delete-outline-sharp.svg`). The `width` and `height` are set for the image.

In simple terms, the `ToDo` component is a part of a user interface for a todo list application. It displays each todo item with a checkbox to mark it as complete, an editable text field for the todo name, and a delete button with an image icon. The component allows for interaction with the todo item, including changing its completion status, editing its name, and removing it from the list.

## Create the style files

#### Delete the content in the default css files:
* globals.css
* Home.module.css

#### styles/layout.module.css


```python
.layout {
    width: 300px;
    margin: 20px;
}

.title {
    text-align: center;
    font-size: 24px;
    margin: 10px;
}
```

#### styles/todo-list.module.css


```python
.container {
  width: 300px;
  border: 1px solid black;
}

.mainInputContainer {
  width: 100%;
  margin: 20px 0;
}

.mainInput {
  padding: 5px;
  border: 1px solid black;
  margin: auto;
  display: block;
  width: 260px;
  height: 40px;
}

.filters {
  display: flex;
  justify-content: space-between;
  padding: 20px;
  margin-top: 20px;
  border-top: 1px solid black;
}

.filterBtn {
  background: none;
  border: none;
  cursor: pointer;
}

.filterActive {
  text-decoration: underline;
}
```

#### styles/todo.module.css


```python
.todoInput {
    padding: 5px;
    border: 1px solid black;
    width: 194px;
    height: 40px;
    margin: 5px;
}

.toDoRow {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 5px 20px;
}

.deleteBtn {
    background: none;
    border: 0;
    cursor: pointer;
}
```

## Load the delete icon in the public folder
* You can download it here: [https://iconduck.com/icons/28730/delete-outline](https://iconduck.com/icons/28730/delete-outline)

## Part 3: Run the full-stack app

#### You will need to have the backend app open from another terminal window


```python
#uvicorn main:app --reload
```

#### Open an additional terminal window an run the frontend app


```python
#npm run dev
```

#### If you are using the Chrome browser, you can open DevTools and see the operations that are happening in the background when you make changes in the todo app tasks.

## Part 4: Upload backend to Github

Uploading your backend application to a GitHub account is a relatively straightforward process. Here's a step-by-step guide to do it:

### Step 1: Create a Repository on GitHub

1. **Log in to GitHub**: Go to [GitHub](https://github.com/) and make sure you're registered or log in.

2. **Create a New Repository**:
   - Click on the "+" icon in the top right corner and select "New repository".
   - Name your repository, add a description (optional), and choose whether it should be public or private.
   - You can also initialize the repository with a README file, a license, or a `.gitignore`, although this is optional and can be done later.

### Step 2: Prepare Your Local Project

1. **Organize Your Code Locally**:
   - If you haven't already, organize your code in a folder on your computer. Ensure everything you need is included and that confidential files (like `.env` with credentials) are excluded or listed in `.gitignore`.

2. **Initialize Git in Your Project** (if not already done):
   - Open a terminal or command line.
   - Navigate (`cd`) to your project folder.
   - Run `git init` to initialize a new Git repository.

3. **Add a `.gitignore` File** (if you don't have one):
   - Create a `.gitignore` file at the root of your project.
   - Add names of files or folders you don't want to upload to GitHub (for example, `node_modules`, sensitive configuration files, etc.).

### Step 3: Upload Your Code to GitHub

1. **Add Files to the Local Git Repository**:
   - From the terminal, in your project folder, run `git add .` to add all files to the repository (respecting `.gitignore`).
   - Or use `git add [file]` to add specific files.

2. **Make Your First Commit**:
   - Run `git commit -m "First commit"` to make the first commit with a descriptive message.

3. **Link Your Local Repository with GitHub**:
   - On GitHub, on your repository page, you'll find a URL for the repository. It will be something like `https://github.com/your-user/your-repository.git`.
   - In your terminal, run `git remote add origin [repository URL]` to link your local repository with GitHub.

4. **Push Your Code to GitHub**:
   - Run `git push -u origin master` (or `main` if your main branch is called `main`) to push your code to the GitHub repository.

### Step 4: Verify and Continue Development

- **Verify on GitHub**: After uploading your code, go to your repository page on GitHub to make sure everything is there.
- **Future Development**: For future commits, you only need to do `git add`, `git commit`, and `git push`.

And with that, your backend application should be on GitHub. Always remember to keep sensitive data secure and use good Git practices for managing your code.

## Part 5: Deploy backend to Render.com

Deploying your FastAPI backend with a PostgreSQL database on Render.com involves several steps. Render offers a fairly straightforward solution for deploying web applications and databases. Here is a basic guide to do it:

### Step 1: Prepare Your FastAPI Application

Before deploying, make sure your FastAPI application is production-ready. This includes:

1. **Check Dependencies**: Ensure all necessary dependencies are listed in a `requirements.txt` file.

2. **Application Configuration**: Verify that your application is configured to use environment variables for important configurations, such as database credentials.

3. **Dockerfile (Optional)**: If you prefer to deploy using Docker, make sure you have a suitable `Dockerfile` for your application. Render supports deployments both with and without Docker.

### Step 2: Set Up Your PostgreSQL Database

1. **Create a Database on Render**:
   - Go to the Render dashboard and create a new PostgreSQL database service.
   - Render will provide the database credentials, including the hostname, port, username, password, and database name.

2. **Configure Environment Variables**:
   - Note down the database credentials, as you will need them to configure your FastAPI application.

### Step 3: Deploy Your FastAPI Application

1. **Create a New Web Service on Render**:
   - In the Render dashboard, choose the option to create a new web service.
   - Select the repository where your FastAPI code is.
   - Configure the deployment options, such as the runtime environment (if you are not using Docker).

2. **Set Environment Variables for FastAPI**:
   - In your web service settings on Render, set the necessary environment variables for your application, including the PostgreSQL database credentials.

3. **Deployment**:
   - Render will start the deployment process once you have configured your service and saved the changes.
   - If you have set up everything correctly, Render will build and deploy your application.

4. **Review and Testing**:
   - After deploying, be sure to review the available logs in Render to verify that everything is working as expected.
   - Perform tests to ensure that your FastAPI application is communicating correctly with the PostgreSQL database.

### Step 4: Updates and Maintenance

- **Updates**: To update your application, simply push your changes to the repository connected to Render. Render will automatically initiate a new deployment.
- **Monitor Your Application**: Use Render's tools to monitor the performance and health of your application and database.

### Final Considerations

- **Security**: Ensure that your application and database are configured securely.
- **Database Backups**: Set up regular backups for your database on Render to prevent data loss.

Render.com greatly facilitates the process of deploying applications and databases, integrating well with code repositories and providing a manageable platform for deployment and application management.

## How to add environment variables in Render.com

To set up environment variables for your FastAPI application on Render.com, follow these steps:

### Access Your Web Service Settings on Render

1. **Log in to Render**: Go to [Render.com](https://render.com/) and log in to your account.

2. **Navigate to Your Web Service**: In the Render dashboard, locate the web service you created for your FastAPI application.

3. **Enter the Service Configuration**: Click on the web service to open its configuration panel.

### Set Up the Environment Variables

1. **Find the Environment Variables Section**: Within the service configuration, look for a section called "Environment Variables" or something similar.

2. **Add New Environment Variables**:
   - Click the button to add a new environment variable.
   - Enter the name and value for each required variable.
   - For example, if your FastAPI application uses environment variables for database connection, you will need to add variables such as `DATABASE_URL`, `DATABASE_USER`, `DATABASE_PASSWORD`, etc., with the corresponding values you obtained when setting up your PostgreSQL database in Render.

### Common Examples of Environment Variables

- **`DATABASE_URL`**: The full URL to connect to your PostgreSQL database.
- **`DATABASE_USER` and `DATABASE_PASSWORD`**: Username and password for the database.
- **Application Configuration Variables**: Any other variables your application needs for its configuration, such as secret keys, operation modes, etc.

### Save and Apply Changes

- After adding all your environment variables, make sure to save the changes.
- Render might automatically restart your service to apply these changes. If not, you can manually restart the service to ensure the new environment variables are in use.

### Verify Everything Works

- Once your service restarts with the new variables, verify that your application is running correctly and can connect to the database using the configured environment variables.

Properly configuring environment variables is crucial for the security and correct functioning of your application in production. These variables allow your application to access important resources such as databases and external APIs, maintaining the sensitivity and configurability of these details.

## Create the todos table in the postgres database

Edit the remote postgress database hosted in Render.com from your terminal:


```python
#psql postgresql://user:password@host:port/databasename
```


```python
# CREATE TABLE todos (
#     id BIGSERIAL PRIMARY KEY,
#     name TEXT,
#     completed BOOLEAN NOT NULL DEFAULT false
# );
```


```python
#\dt
```


```python
#\q
```

## How to verify the backend is running correctly on Render.com

To verify that your application is running correctly and can connect to the database using the configured environment variables, you can follow these steps:

### 1. Check the Application Logs

After deploying your application and setting up the environment variables, the first thing to do is check the application's logs:

- On Render.com, go to the dashboard of your web service.
- Look for a logs or records section. This will show you the output of your application, including startup messages and errors.
- Check these logs for errors or messages related to the database connection. If your application cannot connect to the database, you will likely see errors here.

### 2. Perform Connectivity Tests

If your FastAPI application exposes endpoints that perform read/write operations on the database, you can test these endpoints to ensure that the database connection is working properly:

- Use a tool like Postman or simply a browser to make requests to your API endpoints that require access to the database.
- Observe if the operations are completed successfully (for example, reading data, creating new records, updating or deleting existing records).

### 3. Verify Application Behavior

If your application has a user interface (frontend):

- Interact with the application as a normal user would.
- Perform actions that you know depend on the database and observe if they behave as expected.

### 4. Check Security Configurations

- Make sure that your database's security configurations allow connections from your application deployed on Render. This may include setting up allowed IPs or adjusting firewall rules.

### 5. Use Diagnostic Tools

- If you have access to database diagnostic or monitoring tools (like those provided by Render's database service or external tools), use them to verify if there are active connections and if queries are being executed.

### 6. Consult Documentation and Support

- If you encounter problems, consult the documentation of Render and FastAPI to see if there are specific configuration or troubleshooting steps you might have overlooked.
- If problems persist, consider seeking help in community forums or Render's technical support.

### 7. Verify Environment Variables

- Make sure the environment variables are correctly configured in Render and that your application is using them as expected.

By following these steps, you should get a good idea of whether your application is running correctly and if it's connecting to the database as expected.

## Part 6: Load the frontend to Github
* Follow the process explained in Part 4.

## Part 7: Deploy the frontend to Vercel

Uploading your frontend to Vercel after uploading it to GitHub is a fairly straightforward process. Vercel integrates seamlessly with GitHub, making the deployment process easy. Here's how to do it step by step:

### Step 1: Prepare Your GitHub Repository

Before you start, make sure your frontend project is up to date on GitHub. This includes all necessary files to run your application, such as `package.json`, source code files, etc.

### Step 2: Create a Vercel Account (if you don't have one yet)

If you don't have a Vercel account yet, go to [Vercel.com](https://vercel.com/) and sign up. You can do this using your GitHub account, which facilitates integration.

### Step 3: Connect Your GitHub Repository with Vercel

1. **Log in to Vercel**: Log into your Vercel account.

2. **Import Your Project**:
   - In your Vercel dashboard, look for an option to "Import Project" or "New Project".
   - Select "Import from GitHub". Vercel will ask for permission to access your GitHub repositories if it's your first time doing this.
   - Choose the GitHub repository that contains your frontend project.

### Step 4: Configure Your Project in Vercel

Once you have selected your repository:

1. **Configure Project Options**:
   - Vercel will automatically detect that it's a frontend project (such as a React, Vue, Next.js project, etc.) and will suggest configurations.
   - Configure the build and deployment options as necessary. This may include build commands, output directory, and environment variables.

2. **Set Up Environment Variables** (if necessary):
   - If your application requires environment variables (like API keys or URLs), add them in the project configuration on Vercel.

### Step 5: Deploy Your Project

- After configuring your project, click on "Deploy". Vercel will start the deployment process automatically.
- You can follow the progress of the deployment in the Vercel dashboard. Once the deployment is complete, you will receive a URL where your application will be available.

### Step 6: Future Updates

- For future updates, simply push your changes to the GitHub repository. If you have continuous integrations enabled in Vercel, each push to the selected branch (such as `main` or `master`) will automatically initiate a new deployment.

### Step 7: Verify Your Application

- Once your application is deployed, visit the URL provided by Vercel to ensure everything is working as expected.

And with that, your frontend should be live on Vercel, accessible via a public URL, and automatically updating with each change you push to your GitHub repository.

## Enter the environment variables in Vercel: NEXT_PUBLIC_API_URL

To ensure that your frontend deployed on Vercel connects with your backend hosted on Render.com, you need to update the `NEXT_PUBLIC_API_URL` environment variable to point to the URL of your backend service on Render.com. Here's how you can do it:

### Find Your Backend URL on Render

1. **Log in to Render**: Go to [Render.com](https://render.com/) and log into your account.
2. **Locate Your Backend Service**: Look for the service you have set up for your FastAPI backend.
3. **Copy the Service URL**: Render assigns a URL to each deployed service. Find this URL in the dashboard of your service on Render. Typically, it will be something like `https://your-backend.onrender.com`.

### Update the Environment Variable in Vercel

1. **Log in to Vercel**: Go to [Vercel.com](https://vercel.com/) and log into your account.
2. **Navigate to Your Frontend Project**: Search for and select the frontend project where you need to update the environment variable.
3. **Access Project Settings**: Look for a configuration or settings section of the project.
4. **Edit the Environment Variables**:
   - Find the `NEXT_PUBLIC_API_URL` variable and change its value to the URL of your backend service on Render, for example, `https://your-backend.onrender.com`.
   - If the variable does not exist, add it with the name `NEXT_PUBLIC_API_URL` and the corresponding value for the URL of the Render service.

### Considerations

- **Recompilation**: When changing environment variables in Next.js projects, you may need to recompile your application for the changes to take effect.
- **Public Variables in Next.js**: In Next.js, environment variables exposed to the browser must start with `NEXT_PUBLIC_`. Ensure this convention is maintained so your frontend application can access them.

### Frontend Deployment

- Once you have updated the environment variable in Vercel, your frontend application will automatically recompile and deploy with the new configuration.
- Verify that your frontend is correctly connecting to the backend after deployment.

By following these steps, your frontend on Vercel will be configured to communicate with your backend hosted on Render.com, allowing you to effectively handle requests between the frontend and backend.

## Update the CORS configuration in the backend
In main.py, line 20:


```python
# origins = [
#     "http://localhost:3000",
#     "https://yourvercelname.vercel.app/",
# ]
```

Or you can instead do (this is not recommended for a real-world project):


```python
# origins = ["*"]
```

So the CORS configuration (line 25) will be:


```python
# CORS configuration, needed for frontend development
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
```

## If the data does not load, try Purge Cache in Vercel
* In Project Settings > Data Cache > Purge Everything


```python

```


***
***
## LangChain + ToDo Full Stack App

### Add OpenAI key in backend/.env

### Add imports in backend/routers/todos.py


```python
# from langchain import OpenAI, PromptTemplate
# from langchain.chains import LLMChain
```

### Add basic LangChain code in backend/routers/todos.py


```python
# LANGCHAIN
langchain_llm = OpenAI(temperature=0)

summarize_template_string = """
        Provide a summary for the following text:
        {text}
"""

summarize_prompt = PromptTemplate(
    template=summarize_template_string,
    input_variables=['text'],
)

summarize_chain = LLMChain(
    llm=langchain_llm,
    prompt=summarize_prompt,
)

@router.post('/summarize-text')
async def summarize_text(text: str):
    summary = summarize_chain.run(text=text)
    return {'summary': summary}
```

### Check backend


```python
#uvicorn main:app --reload
```

http://127.0.0.1:8000/docs
* Check how POST /todos/summarize-test works

### Add advanced LangChain code in backend/routers/todos.py


```python
write_poem_template_string = """
        Write a short poem with the following text:
        {text}
"""

write_poem_prompt = PromptTemplate(
    template=write_poem_template_string,
    input_variables=['text'],
)

write_poem_chain = LLMChain(
    llm=langchain_llm,
    prompt=write_poem_prompt,
)

@router.post("/write-poem/{id}")
async def get_todo_by_id(id: int, db: Session = Depends(get_db)):
    todo = crud.read_todo(db, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="to do not found")
    poem = write_poem_chain.run(text=todo.name)
    return {'poem': poem}
```

## Update frontend

### components/todo.js
* The generatePoem(id) function is the key
* We are displaying the generated poem in a pop-up box
* The associated styles are in styles/todo.module.css


```python
import Image from 'next/image'
import styles from '../styles/todo.module.css'
import { useState } from 'react'

export default function ToDo(props) {
  const { todo, onChange, onDelete } = props;
  const [poem, setPoem] = useState(null); // Add this line to define the poem state
  const [isPoemVisible, setIsPoemVisible] = useState(false); // Track the visibility of the poem box

  // The following function is added for our LangChain test:
  async function generatePoem(id) {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/todos/write-poem/${id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
    if (res.ok) {
        const data = await res.json();
        setPoem(data.poem);
        setIsPoemVisible(true); // Show the poem box when a poem is generated
    }
  }

  // Function to close the poem box
  function closePoemBox() {
    setIsPoemVisible(false);
  }

  return (
    <div className={styles.toDoRow} key={todo.id}>
      <input
        className={styles.toDoCheckbox}
        name="completed"
        type="checkbox"
        checked={todo.completed}
        value={todo.completed}
        onChange={(e) => onChange(e, todo.id)}
      ></input>
      <input
        className={styles.todoInput}
        autoComplete='off'
        name="name"
        type="text"
        value={todo.name}
        onChange={(e) => onChange(e, todo.id)}
      ></input>
      <button
        className={styles.generatePoemBtn} // Style the poem button as needed
        onClick={() => generatePoem(todo.id)} // Call the generatePoem function
      >
        Generate Poem
      </button>
      <button className={styles.deleteBtn} onClick={() => onDelete(todo.id)}>
        <Image src="/delete-outline.svg" width="24" height="24" />
      </button>
      {isPoemVisible && (
        <div className={styles.poemBox}>
          <button className={styles.closeButton} onClick={closePoemBox}>
            &times; {/* Add a close icon (×) */}
          </button>
          <div className={styles.poem}>
            <p>{poem}</p>
          </div>
        </div>
      )}
    </div>
  );  

}
```
