### ERROR CODE SCHEMA
#### code: aabbbxxx

#### a - error type:
    
    * 1 - bad request,
    * 2 - not found,
    * 3 - forbidden,
    * 4- already exists,
    * 5 - unprocessable entity

#### b - entity type:

    * 111 - System
    * 001 - User
    * 002 - Folder

#### xx - number of error type. example: 01 - order not found by id

## ERRORS

### base
#### BadRequest
    * 1111001 - wrong credentials
    * 1111001 - file is missing

### User
#### BadRequest
    * 1001001 - wrong user data
    * 1001002 - password changing error
#### NotFound
    * 2001001 - user not found


### File
#### BadRequest
    * 1002001 - file creation error

#### NotFound
    * 2002001 - file not found error
