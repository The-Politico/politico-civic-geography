![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# django-politico-civic-geography

Manage political geographic and spatial data, the POLITICO way.

### Quickstart

1. Install the app.

  ```
  $ pip install django-politico-civic-geography
  ```

2. Add the app to your Django project and configure settings.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'geography',
  ]

  #########################
  # geography settings

  CENSUS_API_KEY = ''
  GEOGRAPHY_AWS_ACCESS_KEY_ID = ''
  GEOGRAPHY_AWS_SECRET_ACCESS_KEY = ''
  GEOGRAPHY_AWS_REGION = 'us-east-1' # default
  GEOGRAPHY_AWS_S3_BUCKET = ''
  GEOGRAPHY_S3_UPLOAD_ROOT = 'elections' # default
  GEOGRAPHY_AWS_ACL = 'public-read' # default
  GEOGRAPHY_AWS_CACHE_HEADER = 'max-age=31536000' # default
  GEOGRAPHY_API_AUTHENTICATION_CLASS = 'rest_framework.authentication.BasicAuthentication' # default
  GEOGRAPHY_API_PERMISSION_CLASS = 'rest_framework.permissions.IsAdminUser' # default
  GEOGRAPHY_API_PAGINATION_CLASS = 'geography.pagination.ResultsPagination' # default

  ```

3. Migrate the database.

  ```
  $ python manage.py migrate geography
  ```


### Bootstrapping your database

civic-geography can bootstrap a database of US national, state and county data for you from U.S. Census cartographic boundary files, creating simplified topojson geography. Just run it!

```
$ python manage.py bootstrap_geography
```


Use the `--help` flag to see additional options.

*Note:* In order to create simplified geography, you must have [topojson](https://github.com/topojson/topojson) installed and available via command line on your machine. You can install it via npm.

```
$ npm install -g topojson
```

### Publishing geography to S3

You can publish your geometries as topojson to an S3 bucket with this command.

```
$ python manage.py bake_geography
```


### Developing

##### Running a development server

Move into the example directory, install dependencies and run the development server with pipenv.

  ```
  $ cd example
  $ pipenv install
  $ pipenv run python manage.py runserver
  ```

##### Setting up a PostgreSQL database

1. Run the make command to setup a fresh database.

  ```
  $ make database
  ```

2. Add a connection URL to `example/.env`.

  ```
  DATABASE_URL="postgres://localhost:5432/geography"
  ```

3. Run migrations from the example app.

  ```
  $ cd example
  $ pipenv run python manage.py migrate
  ```
