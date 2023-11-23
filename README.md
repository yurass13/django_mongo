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

## Bugs
### custom_forms.tests.test_names_exists_but_wrong_types
In query or DB response:
1. Type of DT1 is TX
```py
# custom_forms.views.get_form:
fields = [
    {'f_name': 'TX1', 'f_type': 'TX'},
    {'f_name': 'DT1', 'f_type': 'TX'},
    {'f_name': 'DT2', 'f_type': 'DT'}
]
```
2. In query prototype we see that f_type of DT1 is TX:
```py
# custom_forms.views.get_form:
candidates.query = '''
SELECT
    "custom_forms_customform"."name",
    "custom_forms_customform"."fields"
FROM "custom_forms_customform"
WHERE (
    "custom_forms_customform"."fields" = {'f_name': 'TX1', 'f_type': 'TX'} AND
    "custom_forms_customform"."fields" = {'f_name': 'DT1', 'f_type': 'TX'} AND
    "custom_forms_customform"."fields" = {'f_name': 'DT2', 'f_type': 'DT'}
)'''
```
3. But QuerySet is not empty:
```py
  len(candidates)=1
  best_form = <QuerySet [<CustomForm: CustomForm object (Text with date1 and date2)>]>
```

May mongo ignore f_type after find f_name?
