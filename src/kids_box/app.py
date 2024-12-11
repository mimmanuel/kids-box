import uvicorn
from kids_box.api import app

def run():
    uvicorn.run(app=app)
