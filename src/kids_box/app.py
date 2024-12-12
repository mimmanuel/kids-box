import uvicorn
from kids_box.api import app

def run():
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
