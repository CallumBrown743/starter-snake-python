# battlesnake-python (Crayon)

## Ethan Wipond and Wyll Brimacombe

Fork of [battlesnake-python](https://github.com/sendwithus/battlesnake).

Master branch is auto-deployed to https://era-snake.herokuapp.com/

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) to serve requests and the [gunicorn web server](http://gunicorn.org/) for running bottle on Heroku. Dependencies are listed in [requirements.txt](requirements.txt).

2019 documentation is here: [http://docs.battlesnake.io/](http://docs.battlesnake.io/)

2018:
Beat Semaphore, Giftbit, Redbrick, and Bambora.

2019: 
???

## Running the Snake Locally

1) Clone repo to your development environment:
```
git clone git@github.com:username/battlesnake-python.git
```

2) Setup a python3 virtual environment 

```
python3 -m venv env
```

3) Activate the virtual environment

```
source env/bin/activate
```

3) Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):
```
pip install -r requirements.txt
```

4) Run local server:
```
python app/main.py
```

5) Test client in your browser: [http://localhost:8080](http://localhost:8080).

6) Start the [test server](http://docs.battlesnake.io/zero-to-snake-linux.html)

```
cd battlesnake-engine
./engine dev
```

7) Navigate to [http://localhost:3010](http://localhost:3010)

## To Do 

- Add move toward snake tail as a flood priority.
- Add potential snake moves to flooding in a way that they know they can still move there.
- Something with outer edges of map

- Speed up response time?
- better logging
- Get snake running on snakedown/play.battlensake
