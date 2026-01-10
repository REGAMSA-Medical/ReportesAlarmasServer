import uvicorn
import sys
import subprocess

def main():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True
    )

def makemigrations():
    args = sys.argv[1:]
    command = ['alembic', 'revision', '--autogenerate'] + args
    subprocess.run(command)
    
def migrate():
    subprocess.run(['alembic', 'upgrade', 'head'])

if __name__ == "__main__":
    main()