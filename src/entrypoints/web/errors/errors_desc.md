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


### Folder
#### BadRequest
    * 1002001 - folder creation error
    * 1002002 - folder update error

#### NotFound
    * 2002001 - folder not found error

### Note
#### BadRequest
    * 1003001 - note creation error
    * 1003002 - note update error

#### NotFound
    * 2003001 - note not found error
