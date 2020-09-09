from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import srp

USER_POOL_ID = 'ap-southeast-1_pfjxa1vNH'
CLIENT_ID = '2k4evm55f7224e3bg54nhfpot'
CLIENT_SECRET ='ncggtvl6dlcak550q8cl2uo2ngu44nqs78hrl4rv7re1cf3g2mc'

def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'),
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

class SignUp(Resource):

    def post(self):
        client = boto3.client('cognito-idp')
        signupInfo = request.get_json()

        given_name = signupInfo['firstName']
        family_name = signupInfo['lastName']
        phone_number = signupInfo['mobile']
        email = signupInfo['email']
        password = signupInfo['password']


        try:
            response = client.sign_up(
                ClientId = CLIENT_ID,
                SecretHash = get_secret_hash(email),
                Username = email,
                Password = password,
                UserAttributes = [
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'given_name',
                        'Value': given_name
                    },
                    {
                        'Name': 'family_name',
                        'Value': family_name
                    },
                    {
                        'Name': 'phone_number',
                        'Value': phone_number
                    },
                ],
                ValidationData = [
                    {
                        'Name': 'email',
                        'Value': email
                    },
                ]
            )
        except client.exceptions.UsernameExistsException as e:
            return {"error": True,
                   "success": False,
                   "message": "This username already exists",
                   "data": None}
        except client.exceptions.InvalidPasswordException as e:

            return {"error": True,
                   "success": False,
                   "message": "Password should have Caps,\
                              Special chars, Numbers",
                   "data": None}
        except client.exceptions.UserLambdaValidationException as e:
            return {"error": True,
                   "success": False,
                   "message": "Email already exists",
                   "data": None}

        except Exception as e:
            return {"error": True,
                    "success": False,
                    "message": str(e),
                   "data": phone_number}

        return {"error": False,
                "success": True,
                "message": "Please confirm your signup, check Email for verification code",
                "data": response['UserSub']}

class ConfirmSignUp(Resource):
    def post(self):
        client = boto3.client('cognito-idp')
        confirmSignUpInfo = request.get_json()

        email = confirmSignUpInfo['email']
        password = confirmSignUpInfo['password']
        code = confirmSignUpInfo['code']

        try:
            response = client.confirm_sign_up(
            ClientId = CLIENT_ID,
            SecretHash = get_secret_hash(email),
            Username = email,
            ConfirmationCode = code,
            ForceAliasCreation = False,
            )
        except client.exceptions.UserNotFoundException:
            return {"error": True,
                    "success": False,
                    "message": "Username doesnt exists"}
        except client.exceptions.CodeMismatchException:
            return {"error": True,
                    "success": False,
                    "message": "Invalid Verification code"}

        except client.exceptions.NotAuthorizedException:
            return {"error": True,
                    "success": False,
                    "message": "User is already confirmed"}

        except Exception as e:
            return {"error": True,
                    "success": False,
                    "message": f"Unknown error {e.__str__()}"}

        return {"error": False,
                "success": True,
                "message": "Account Validated, Proceed to sign in",
                "data": None}

class ResendVerifictionCode(Resource):
    def post(self):
        client = boto3.client('cognito-idp')
        data = request.get_json()
        email = data['email']

        try:
            response = client.resend_confirmation_code(
            ClientId = CLIENT_ID,
            SecretHash = get_secret_hash(email),
            Username = email,
            )

        except client.exceptions.UserNotFoundException:
            return {"error": True, "success": False, "message":   "Username doesnt exists"}

        except client.exceptions.InvalidParameterException:
            return {"error": True, "success": False, "message": "User is already confirmed"}

        except Exception as e:
            return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}

        return {"error": False, "success": True, "message": "Verification vode sent, check Email for verification code"}

class ForgotPassword(Resource):
    def post(self):
        client = boto3.client('cognito-idp')
        data = request.get_json()
        email = data['email']

        try:
            response = client.forgot_password(
            ClientId = CLIENT_ID,
            SecretHash = get_secret_hash(email),
            Username = email,
            )

        except client.exceptions.UserNotFoundException:
            return {"error": True,
                    "data": None,
                    "success": False,
                    "message": "Username doesnt exists"}

        except client.exceptions.InvalidParameterException:
            return {"error": True,
                    "success": False,
                    "data": None,
                  "message": f"User <{username}> is not confirmed yet"}

        except client.exceptions.NotAuthorizedException:
            return {"error": True,
                    "success": False,
                    "data": None,
                    "message": "User is already confirmed"}

        except Exception as e:
            return {"error": True,
                    "success": False,
                    "data": None,
                    "message": f"Uknown    error {e.__str__()} "}

        return {
             "error": False,
             "success": True,
             "message": f"Please check your Registered email id for validation code",
             "data": None}

class ConfirmForgotPassword(Resource):
    def post(self):
        client = boto3.client('cognito-idp')
        data = request.get_json()
        email = data['email']
        password = data['password']
        code = data['code']

        try:
            client.confirm_forgot_password(
                ClientId = CLIENT_ID,
                SecretHash = get_secret_hash(email),
                Username = email,
                ConfirmationCode = code,
                Password = password
            )
        except client.exceptions.UserNotFoundException as e:
            return {"error": True,
                    "success": False,
                    "data":  None,
                    "message": "Username doesnt exists"}

        except client.exceptions.CodeMismatchException as e:
                return {"error": True,
                       "success": False,
                       "data": None,
                       "message": "Invalid Verification code"}

        except client.exceptions.NotAuthorizedException as e:
            return {"error": True,
                     "success": False,
                     "data": None,
                     "message": "User is already confirmed"}

        except Exception as e:
            return {"error": True,
                    "success": False,
                    "data": None,
                    "message": f"Unknown error {e.__str__()} "}

        return {"error": False,
                "success": True,
                "message": f"Password has been changed successfully",
                "data": None}

class Login(Resource):
    def post(self):
        client = boto3.client('cognito-idp')
        data = request.get_json()
        email = data['email']
        password = data['password']
        device_info = data[device]
        secret_hash = get_secret_hash(email)

        try:
            response = client.initiate_auth(
                AuthFlow = 'USER_SRP_AUTH',
                AuthParameters = {
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash
                },
                ClientId = CLIENT_ID
            )

        except Exception as e:
            return {"error": True,
                    "success": False,
                    "data": None,
                    "message": f"Unknown error {e.__str__()} "}
        print(response['ChallengeParameters'].keys())
        #'DeviceKey': response['AuthenticationResult']['NewDeviceMetadata']['DeviceKey']
        return response
