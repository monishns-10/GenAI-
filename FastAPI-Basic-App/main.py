from fastapi import FastAPI

# Initialize the FastAPI app
app = FastAPI()

# Requirement: Create a root endpoint GET / that returns a simple JSON response
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

# Requirement: Add an endpoint that takes a value from the URL (path parameter) and returns it
@app.get("/greet/{name}")
def greet_user(name: str):
    return {"message": f"Hello there, {name}!"}