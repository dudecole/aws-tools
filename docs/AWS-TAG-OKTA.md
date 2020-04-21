# aws-tag-okta.py
## Overview
This script wraps the saml2aws and awscli into a python script, and with the current release - is used for connecting to AWS via OKTA authentication, and creating a particular AWS tag on an orginazation's AWS account with their OKTA URL.  

The [aws-tag-okta](../scripts/aws-tag-okta.py) script was written in Python3, and uses the following python modules.
## Packages
Linux or Windows packages
```
saml2aws
```
Python Packages - PIP version 3
```
awscli==1.18.40
```
Install PIP Packages
```
pip install -r requirements.txt
```
		
## Syntax
To run the [aws-tag-okta.py](../scripts/aws-tag-okta.py) script, use the following as a guideline:

    python scripts/aws-tag-okta.py [-option1] [value] [-option2] [value]
	
    [-option]: is a command line argument for specifying optional and mandatory arguments. 
		
    [value]: Specifies the value of the [-option].  Values can be quoted or non-quoted.
		
When using multiple options with values, each option is space separated.
	
## Operations
The following table includes the options, available defaults, and example values:

| Option 	| Syntax 	| Default 	| Description 	|
|------------------------------------------------	|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|---------------------------------------	|-----------------------------------------------------------------------------------------------------	|
| -u AWS_USER,<br>--aws_user AWS_USER 	| python aws-tag-okta.py -u someid@someemail.com<br><br>python aws-tag-okta.py --aws-user someid@someemail.com 	| Default=None 	| Required=True<br><br>Format=No format validation 	|
| -p AWS_PASS,<br>--aws_pass AWS_PASS 	| python aws-tag-okta.py -u someid@someemail.com -p somepassword<br><br>python aws-tag-okta.py -u someid@someemail.com --aws_pass somepassword 	| Default=None 	| Required=True<br><br>Format=With or without quotes 	|
| -r ROLE, <br>--role ROLE 	| python aws-tag-okta.py -u user -p pass -r VA-Role-SomeRoleinAWS<br><br>python aws-tag-okta.py -u user -p pass --role VA-Role-SomeRoleinAWS 	| Default=VA-Role-SecurityAudit 	| Required=False<br><br>Format=Include '-' and is case-sensitive. 	|
| -pr PARENT_ROLE, <br>--parent_role PARENT_ROLE 	| Python aws-tag-okta.py -u user -p pass -pr arn:aws:iam:::role/<br><br>Python aws-tag-okta.py -u user -p pass --parent_role arn:aws:iam:::role/ 	| Default=arn:aws:iam::<00..0123>:role/ 	| Required=False<br><br>Format=Include ':' and ends with '/'. 	|
| -o OKTA_URL, <br>--okta_url OKTA_URL 	| python aws-tag-okta.py -u user -p pass -o https://<okta-aws.com>/home/amazon_aws/00...00/291<br><br>python aws-tag-okta.py -u user -p pass --okta_url https://<okta-aws.com>/home/amazon_aws/00...00/291 	| Default=See Help File 	| This is the OKTA url to access the parent aws account. <br><br>Required=False<br><br>Format=URI address 	|
| -i IDP_ACCOUNT, <br>--idp_account IDP_ACCOUNT 	| python aws-tag-okta.py -u user -p pass -i IDPname<br><br>python aws-tag-okta.py -u user -p pass --idp_account IDPname 	| Default=parent 	| The IDP account to use. <br><br>Required=False 	|
| -id ACCOUNT_ID, <br>--account_id ACCOUNT_ID 	| python aws-tag-okta.py -u user -p pass -id 123412341234<br><br>python aws-tag-okta.py -u user -p pass --account_id 1234123408 	| Default=None 	| The account or resource ID. <br><br>Required=False	|
| -s SEARCH_STRING, <br>--search_string SEARCH_STRING 	| python aws-tag-okta.py -u user -p pass -s 123409812340812<br><br>python aws-tag-okta.py -u user -p pass --search_string 1234123412 	| Default=None | To be determined.. Currently built for ACCOUNT_ID like 12341234. <br><br>Required=False	|
| -ot OKTA_TAG_URL, <br>--okta_tag_url OKTA_TAG_URL 	| python aws-tag-okta.py -u user -p pass -ot https://okta.url<br><br>python aws-tag-okta.py -u user -p pass --okta_tag_url https://okta.url 	| Default=None 	| The okta url to tag the account. 	<br><br>Required=False|