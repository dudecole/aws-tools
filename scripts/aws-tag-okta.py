#!/usr/bin/python3

import json
import pprint as p #after testing we can clean this up
import subprocess
import argparse

# needs to be an integer converted to a string type
MAXIMUM_RESULTS = str(1000)


def main():
    """
    This authenticates to aws via saml2aws and uses OKTA as the IDP provider.

    Then, queries the parent organization for the account ID provided by --account_id and
    validates there are(not) entries for:

     Key of OktaUrl
     Value of 'https://'

            "Key": "VA-OktaURL",
            "Value": "https://my.okta.com/home/amazon_aws/1234123412341234"

    If the keys do not exist, then they are added to the account.

    Todo:
        1. Add account search validation?
        2. validate tagging actually works
        3. check to see if there is a way to auto-generate/auto-grab the okta URL to use
        4. Add/fix the try and except statement for each function
        5. allow the --ACCOUNT_ID parameter to be a list/array, or input file?

    :return: Success or failure message is returned
    """

    ap = argparse.ArgumentParser()

    ap.add_argument('-u', '--aws_user', required=True, dest='AWS_USER',
                    help="AWS Username in Email format, "
                         "Required=True")

    ap.add_argument('-p', '--aws_pass', required=True, dest='AWS_PASS',
                    help="AWS Password, "
                         "Required=True.")

    ap.add_argument('-r', '--role', dest='ROLE',
                    default='VA-Role-SecurityAudit',
                    help="Example: VA-Role-SomeRoleInAws , "
                         "Default=VA-Role-SecurityAudit , "
                         "Required=False")

    ap.add_argument('-pr', '--parent_role', dest='PARENT_ROLE',
                    default='arn:aws:iam::123412341234:role/',
                    help="Example: arn:aws:iam::<00..0123>:role/ , "
                         "Default=arn:aws:iam::123412341234:role/ ,  "
                         "Required=False")

    ap.add_argument('-o', '--okta_url', dest='OKTA_URL',
                    help="Example: https://<address>.<com>/home/amazon_aws/00...00/291 , "
                         "Required=False")

    ap.add_argument('-i', '--idp_account', dest='IDP_ACCOUNT',
                    default='orgparent',
                    help="Example: orgparent , Default=orgparent , "
                         "Required=False")

    ap.add_argument('-id', '--account_id', dest='ACCOUNT_ID',
                    default='123412341234',
                    help="AWS Account ID - default IS&T Sandbox account ID")

    ap.add_argument('-s', '--search_string', dest='SEARCH_STRING',
                    default='123412341234',
                    help="AWS Account ID")

    ap.add_argument('-ot', '--okta_tag_url', dest='OKTA_TAG_URL',
                    help="Okta URL to tag account with")

    args = ap.parse_args()

    # set vars for cleaner reference
    IDP_ACCOUNT = args.IDP_ACCOUNT
    OKTA_URL = args.OKTA_URL
    AWS_USER = args.AWS_USER
    AWS_PASS = args.AWS_PASS
    TOTAL_ROLE = args.PARENT_ROLE + args.ROLE
    ACCOUNT_ID = args.ACCOUNT_ID
    SEARCH_STRING = args.SEARCH_STRING
    OKTA_TAG_URL = args.OKTA_TAG_URL
    
    # Call the internal function to build the saml2aws command
    saml_command = _build_saml2aws_command(IDP_ACCOUNT,
                                           OKTA_URL,
                                           AWS_USER,
                                           AWS_PASS,
                                           TOTAL_ROLE)

    # Run compiled saml_command to authenticate
    saml_output = subprocess.run(saml_command, 
                                 check=True, 
                                 shell=True,
                                 stdout=subprocess.PIPE)

    # print the output of auth
    print("authentication status: {}".format(saml_output))

    # tag account
    tag_add_results = add_account_tags(ACCOUNT_ID, OKTA_TAG_URL)

    # validating the format of stdout
    print("tag_add_results: {}".format(tag_add_results))


def add_account_tags(account_id, okta_tag_url):
    """
    This function does the tagging.  It validates the account does(not) have
    tags already, and if true (already tagged), then do nothing.

    If false, then create Okta URL tags.

    Value: To be determined how this is created..
    todo:
        1. figure out how the URLs get generated or created
        2. Verify the VA-OktaURL is a standard/static value or if this needs to be changed
        in the future.

    :param okta_tag_url: string
    :param account_id:
    :return: tagging_status: Dictionary?
    """

    # call function to check to if account has tags first.
    tags = get_account_tags(account_id)

    if not tags:
        # add tags
        tag_account_command = _build_tag_account(account_id,
                                                 okta_tag_url)
        tag_output = subprocess.run(tag_account_command,
                                    check=True,
                                    shell=True,
                                    stdout=subprocess.PIPE)

        # Decoding the stdout of the subprocess.run()
        tag_output_decode = tag_output.stdout.decode(encoding='utf-8',
                                                     errors="ignore")

        # just for validation - can be deleted after testing.
        print("tag_output_decode: {}".format(tag_output_decode))

        # convert status into dictionary
        tagging_status = json.loads(tag_output_decode)

    else:
        # assign tags from get_account_tags and return
        tagging_status = tags

    return tagging_status


def get_account_tags(account_id):
    """
    Function that looks for a tag on a particular account_id/resource_id and returns
    a dictionary or null value (to be determined what value to return if None).

    Sample dictionary return looks like:
    {
    "Tags": [
        {
            "Key": "VA-OktaURL",
            "Value": "https://my.okta.com/home/amazon_aws/123412341234"
        }
    ]
    }

    :param account_id: number converted to string format
    :return: tagging status
    """

    # call function to compile the command
    get_account_tags_cli = _build_get_account_tags(account_id)

    # verify the commands look ok.
    print("account_tags: {}".format(get_account_tags_cli))

    # run the compiled command
    account_tags = subprocess.run(get_account_tags_cli,
                                  check=True,
                                  shell=True,
                                  stdout=subprocess.PIPE)

    # validating - just for testing
    print("here is the aws_cli_output: {}".format(account_tags.stdout.decode
                                                  (encoding='utf-8',
                                                   errors="ignore")))

    # decoding results and assigning to decode var
    aws_account_decode = account_tags.stdout.decode(encoding='utf-8',
                                                    errors="ignore")

    # convert the string to a dictionary
    account_output_dict = json.loads(aws_account_decode)

    # print to make sure things look like a dictionary - just for testing
    p.pprint(account_output_dict, indent=2)

    try:
        # check to see if the key 'Key' and a Value with 'https' exists
        if 'OktaURL' in account_output_dict['Tags'][0]['Key'] and \
             'https' in account_output_dict['Tags'][0]['Value']:

            print("value exists! - Don't need to add anything")
            # assign the dictionary to tags and return it
            tags = account_output_dict['Tags']
        else:
            # set tags to none and return it
            tags = None

    except Exception as e:
        print("ERROR: {}".format(e))

    return tags


def _build_tag_account(resource_id, okta_tag_url):
    """
    Internal function to compile the command to add the OKTA tags to the AWS account.
    todo:
        1. do we want to parameterize this to allow for different kinds of tags?
        2. This function needs to be tested.  PID account doesn't have access to add tags

    The command puts the tags in a list and looks like this:

        aws --profile saml organizations add-tags-to-resource --resource-id 123412341234 \
                --tags "[{\"Key\": \"VA-OktaURL\",\"Value\": \"https://my.okta.com..<stuff>\"}]

        example of tag payload is:
        "Tags": [
            {
                "Key": "VA-OktaURL",
                "Value": "https://my.okta.com/home/amazon_aws/1234123412341234"
            }
        ]
        }

    :param resource_id: Integer converted to string type
    :param okta_tag_url: String
    :return: aws_cli_tag_account: command to run as string format
    """

    aws_cli_tag_account = subprocess.list2cmdline(['aws',
                                                   '--profile',
                                                   'saml',
                                                   'organizations',
                                                   'add-tags-to-resource',
                                                   '--resource-id=' + resource_id,
                                                   '--tags "[{\"Key\": \"VA-OktaURL\", '
                                                   '\"Value\": ' + okta_tag_url])

    return aws_cli_tag_account


def _build_get_account_tags(resource_id):
    """
    Internal function to compile the command to get the tags for the account.

    The command looks like this:

        aws --profile saml organizations list-tags-for-resource --resource-id 123412341234

    :param resource_id: This is the account ID passed in as arg.parse=account_id
    :return: aws_cli_account_tags: command to run as string format
    """

    aws_cli_account_tags = subprocess.list2cmdline(['aws',
                                                    '--profile',
                                                    'saml',
                                                    'organizations',
                                                    'list-tags-for-resource',
                                                    '--resource-id='+ resource_id])

    return aws_cli_account_tags


def _build_initial_list_accounts(maximum_results):
    """
    Internal function to compile the initial awscli command to get the list of
    accounts.

    The command looks like this:

        aws --profile saml organizations list-accounts --max-items MAXIMUM_RESULTS

    :param MAXIMUM_RESULTS: This is a global variable - defined in the beginning of this file
    :return: aws_cli_command
    """

    aws_cli_command = subprocess.list2cmdline(['aws',
                                               '--profile',
                                               'saml',
                                               'organizations',
                                               'list-accounts',
                                               '--max-items',
                                               maximum_results])

    return aws_cli_command


def _build_paged_list_accounts(maximum_results, starting_token):
    """
    Internal function to compile the awscli command that gets a list of accounts
    and includes the 'starting_token' for pagination.

    The 'starting_token parameter is the value of 'NextToken' which may or may not
    be displayed when querying for a list of accounts.

    If there are more pages to show in the 'list-accounts', then the NextToken
    will be displayed.  If this is true, then the value of NextToken is saved
    to the 'starting_token' to continue to the next page of the account results.

    The compiled command should look like:

        aws --profile saml organizations list-accounts --max-items 100 --starting-token 1098238..287-blah-blah

    :param maximum_results: Value of the global variable MAXIMUM_RESULTS defined in start of program
    :param starting_token: This is assigned the 'NextToken' value to continue
    to the next page.
    :return: aws_command_pagination command is returned.
    """
    aws_command_pagination = subprocess.list2cmdline(['aws',
                                                      '--profile',
                                                      'saml',
                                                      'organizations',
                                                      'list-accounts',
                                                      '--max-items',
                                                      maximum_results,
                                                      '--starting-token',
                                                      starting_token])

    return aws_command_pagination


def _build_saml2aws_command(idp_account, okta_url, aws_user,
                            aws_pass, total_role):
    """
    This compiles the command to authenticate via saml2aws.

    The command looks like this:

    saml2aws --idp-account=<idp_account> idp-provider=Okta --mfa=OKTA \
            --url=<okta_url> --username=<aws_user> --password=<aws_pass> \
            --mfa-token= <null> --role=<total_role> --aws-urn=urn:amazon:webservices \
            --skip-prompt --session-duration=3600 login

    :param idp_account: argparse of idp_account
    :param okta_url: argparse of okta_url
    :param aws_user: argparse of aws_user
    :param aws_pass: argparse of aws_pass
    :param total_role: argparse of role + parent_role
    :return: saml_command
    """
    saml_command = subprocess.list2cmdline(['saml2aws',
                                            '--idp-account=' + idp_account,
                                            '--idp-provider=Okta',
                                            '--mfa=OKTA',
                                            '--url=' + okta_url,
                                            '--username=' + aws_user,
                                            '--password=' + aws_pass,
                                            '--mfa-token=',
                                            '--role=' + total_role,
                                            '--aws-urn=urn:amazon:webservices',
                                            '--skip-prompt',
                                            '--session-duration=3600',
                                            'login'])

    return saml_command


def get_aws_account(maximum_results, search_string):
    """
    This searches all the results for a particular value in the json/dictionary
    payload.  The search string isn't implemented yet, as it is still unclear
    if this function will even be used..

    The return value would be the json/dictionary payload of the account(s) found

    Todo:
        1. determine what the search string would be.
        2. determine if this function would be useful.
        3. pass the search_string parameter in to the function calls of:
            - _build_initial_list_accounts(maximum_results, search_string)
            - _build_paged_list_accounts(MAXIMUM_RESULTS, starting_token,
                                         search_string)
        4. add search_string functionality to the above functions and create
        a return value of the json/dictionary payload information found.
        5. assign the above payload to the return variable of found_account
        6. return the value of found_account back

    :param maximum_results: the global variable MAXIMUM_RESULTS
    :param search_string: string
    :return: found_account: dictionary
    """

    # Call the internal function to build the 'list-accounts' awscli command
    aws_cli_command = _build_initial_list_accounts(maximum_results)

    # verify the commands look ok.
    # print("aws_cli_command: {}".format(aws_cli_command))

    # get the list of accounts
    aws_cli_output = subprocess.run(aws_cli_command,
                                    check=True,
                                    shell=True,
                                    stdout=subprocess.PIPE)

    # convert the aws_cli_output to a string
    cli_output_decode = aws_cli_output.stdout.decode(encoding='utf-8',
                                                     errors="ignore")
    # convert the string to a dictionary
    cli_output_dict = json.loads(cli_output_decode)

    # setting conditional before the loop
    found_account = None
    if 'NextToken' in cli_output_dict:
        while cli_output_dict['NextToken'] and found_account is None:

            # looping through each page searching for 'search_string'
            i = 0
            for i in range(len(cli_output_dict['Accounts'])):
                account = cli_output_dict['Accounts'][i]
                # print("for loop - ID of account: {}".format(account['Id']))

                # if search string is found assign value to found_account
                if search_string in account['Id']:
                    # print("yep we found the account")
                    # p.pprint(account)
                    found_account = account
                    break
                i += 1

            # assigning value of 'NextToke' to starting_token for next page
            starting_token = cli_output_dict['NextToken']

            # calling internal function for pagination and assigning NextToken
            aws_command_pagination = _build_paged_list_accounts(MAXIMUM_RESULTS,
                                                                starting_token)

            # running the compiled command with the new starting_token
            aws_cli_output = subprocess.run(aws_command_pagination,
                                            check=True,
                                            shell=True,
                                            stdout=subprocess.PIPE)
            # decoding the results
            cli_output_decode = aws_cli_output.stdout.decode(encoding='utf-8',
                                                             errors="ignore")

            # converting to a dictionary to parse/search for the NextToken
            cli_output_dict = json.loads(cli_output_decode)

    else:
        i = 0

        # looping through each page searching for 'search_string'
        for i in range(len(cli_output_dict['Accounts'])):
            account = cli_output_dict['Accounts'][i]
            # print("else statement - ID of account: {}".format(account['Id']))

            # if search string is found assign value to found_account
            if search_string in account['Id']:
                # print("else statement - yep we found the account")
                p.pprint(account)
                found_account = account
                break
            i += 1

    return found_account


if __name__ == '__main__':
    main()

