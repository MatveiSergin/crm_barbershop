# CRM for barbershop

This is a project to create a corporate part of the site for barbershop employees. It includes managing orders, employees, document management, viewing statistics, and so on. The system has several roles, which allows you to differentiate access to customer and employee data. The site is configured for JWT authentication.  The system itself is a REST API that should be used to build a website.

## Enviroments variablies
You need to create a file with the environment variables '.env'. Its contents are as follows:
```
DB_NAME='postgres'
DB_USER ='USER_NAME'
DB_PASSWORD='PASSWORD'
DB_HOST='localhost'
DB_PORT='5432'
ALLOWED_HOST='127.0.0.1'
PRODUCTION_HOST='YOUR_DOMEN'
POSTGRES_DB='DB_NAME'
POSTGRES_USER='USER_NAME'
POSTGRES_PASSWORD='DB_PASSWORD'
PGADMIN_DEFAULT_EMAIL='YOUR_EMAIL'
PGADMIN_DEFAULT_PASSWORD='PASSWORD'
```

## Deploy
To deploy the application:
1. You need to create directories.
```
mkdir -p html/project_on_django html/logs html/apache_logs html/logs apache mysql nginx/logs
```

2. Open a directory
```

cd html/project_on_django
```

3. Clone a repository
```
git clone https://github.com/MatveiSergin/crm_barbershop
```

4. Open a folder deploy and remove files.
* Dockerfile and mysite.conf move to apache
* docker-compose.yaml to the root directory

5. Move the created env file to the following path
```
html/project_on_dajngo/crm_barbershop/barbers/
```
 
6. Build images
```
docker-compose build
```

7. Run project
```
docker-compose run
```

8. Go to pg_admin
```
http:\\your_ip:8088
```
9. Create tables based on sql queries from the db.sql file on deploy folder

10. Done!
