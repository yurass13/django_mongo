# django_mongo
Custom Forms. Endpoint get_form[POST] 
  - get params from request data;
  - handle the next data types:
    - Date as DT
    - Text as TX
    - Email as EM
    - Phone Number as PN
  - Returns:
    - name of best CustomForm that has fields with the same name and type.
    - prototype of CustomForm.fields from request data when no suitable form is found.

## Run
```sh
# cd /to/project/directory/ 
docker-compose up -d --build
```

## The code is covered with tests.
Run compose and type the next shell command:
```sh
# Run tests
docker exec -it django_forms_api_web_1 python manage.py test
```

## /_api/v1/get_form/ [POST]

### Input format:
`f_name1=value1&f_name2=value2`

### Output format (Form exits)
`{"name": "Form template name"}`

### Output fromat (Form doesn't exist)
`{f_name1: f_type, f_name2: f_type}`
