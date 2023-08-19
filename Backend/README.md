## To do list
- [ ] Handle file size (max ~= 50MB).
- [ ] Host db on server using Docker.
- [ ] Calculate time execution.


### Instruction

0. Put the private files into Backend/ folder (.env and .json file)

1. Create a new virtual environment with Python and activate it.

```
cd Backend/
python -m venv env
source env/bin/activate
```

2. Install the dependencies.

```
pip install -r requirements.txt
```

3. Run the application (make sure you have PostgreSQL running on your machine and please change the database settings in settings.py to your own database settings...)

```
python manage.py makemigrations account translation
python manage.py migrate
python manage.py runserver
```
<!-- 
4. Go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
5. Enjoy! -->