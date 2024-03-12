_This is work in progress, the README will be updated soon_

# proactive-python-experiments
For trying out the Proactive Pythen SDK within the ExtremeXP project.

## Instructions
(See email from Caroline Pacheco on 31.12.2023)
```
python3 -m venv env
source ./env/bin/activate
python3 -m pip install --upgrade pip setuptools wheel python-dotenv
python3 -m pip install https://files.pythonhosted.org/packages/d7/b7/c4dd046ad83363536b64d620f07795e3bbaadb2d0519f91c5ec4b45909c3/proactive-13.1.0.2312311805.dev0.zip
```

## Configure credentials
1. Create `credentials.py` file via copying the template, e.g. by:
    ```
    mv credentials-TEMPLATE.py credentials.py
    ``` 
2. Verify that the `credentials.py` is git ignored (check `.gitignore`)
1. Add your proactive account name and password to `credentials.py`

## Test
```
python 01_Getting_Started.py
```

## Run IDEKO case
```
python ideko-case.py
```

## Notes
The `scripts` folder is copied over for convenience from the `proactive-python-client` project. 
