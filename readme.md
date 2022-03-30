# Big Brother is watching you

# Setup

- cd src/python/src
- run following command
- ```python bbs_server.py --option1 value1```
- you must define default proxy configuration in following order (from highest priority tp lowest)
    - by options
    - by env
    - by database

# Marks

- all passwords stored at database are encrypted. To encrypt your password use following command
  ```
    python encode_my_password.py %passwrod1% %password2$ %passwordN%
  ```
- restriction: username for comrades must be unique
