from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json

import binascii
import datetime as dt

import srp
from warrant import aws_srp
from warrant.aws_srp import AWSSRP
import secrets
import os
import random


USER_POOL_ID = 'ap-southeast-1_pfjxa1vNH'
CLIENT_ID = 'ld4tq1kmq34qttjpp5cniqh8o'
#sign out use global_sign_out: signs out of all devices

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

def padHex(hex):
    padhashed = hex
    if(len(hex) % 2 == 1):
        padhashed = '0' + padhashed
    elif(padhashed[0] in '89ABCDEFabcdef'):
        padhashed = '00' + padhashed
    return padhashed

def generate_hash_device(device_group_key, device_key):
    # source: https://github.com/amazon-archives/amazon-cognito-identity-js/blob/6b87f1a30a998072b4d98facb49dcaf8780d15b0/src/AuthenticationHelper.js#L137

    # random device password, which will be used for DEVICE_SRP_AUTH flow
    device_password = base64.standard_b64encode(os.urandom(40)).decode('utf-8')

    combined_string = '%s%s:%s' % (device_group_key, device_key, device_password)
    combined_string_hash = aws_srp.hash_sha256(combined_string.encode('utf-8'))
    salt = aws_srp.pad_hex(aws_srp.get_random(16))

    x_value = aws_srp.hex_to_long(aws_srp.hex_hash(salt + combined_string_hash))
    g = aws_srp.hex_to_long(aws_srp.g_hex)
    big_n = aws_srp.hex_to_long(aws_srp.n_hex)
    verifier_device_not_padded = pow(g, x_value, big_n)
    verifier = aws_srp.pad_hex(verifier_device_not_padded)

    device_secret_verifier_config = {
        "PasswordVerifier": base64.standard_b64encode(bytearray.fromhex(verifier)).decode('utf-8'),
        "Salt": base64.standard_b64encode(bytearray.fromhex(salt)).decode('utf-8')
    }
    return device_password, device_secret_verifier_config

class Login(Resource):
    def post(self):
        client = boto3.client('cognito-idp')
        data = request.get_json()
        email = data['email']
        password = data['password']

        client = boto3.client('cognito-idp')

        # Step 1:
        # Use SRP lib to construct a SRP_A Value
        # # Step 2:
        # # Submit USERNAME & SRP_A to Cognito, get challenge.
        # # # Step 3:
        # # # Use challenge parameters from Cognito to construct
        # # # challenge response.
        # # # Step 4:
        # # # Submit challenge response to Cognito.
        aws = AWSSRP(username=email, password=password, pool_id=USER_POOL_ID,
                     client_id=CLIENT_ID, client=client)
        response = aws.authenticate_user()
        print(response['AuthenticationResult'].keys())

        deviceKey = response['AuthenticationResult']['NewDeviceMetadata']['DeviceKey']
        deviceGroupKey = response['AuthenticationResult']['NewDeviceMetadata']['DeviceGroupKey']
        accessToken = response['AuthenticationResult']['AccessToken']


        # randomPassword = secrets.token_urlsafe(40)
        # combinedString = deviceGroupKey + email + randomPassword
        # hashedString = hashlib.sha256(combinedString.encode('utf-8'))
        # #print(hashedString.hexdigest())
        # #salt_hexRandom = padHex(secrets.token_hex(16))
        # #salt_hexRandom = secrets.token_hex(16)
        # salt_hexRandom = hex(secrets.SystemRandom().randint(0, pow(2,128)))
        # #print(padHex(salt_hexRandom) + '\n')
        # #print(hex(salt_hexRandom) + '\n')
        # print(salt_hexRandom)
        #
        # initN = 'FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1'+ '29024E088A67CC74020BBEA63B139B22514A08798E3404DD'+ 'EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245'+ 'E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED' + 'EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D'+ 'C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F'+ '83655D23DCA3AD961C62F356208552BB9ED529077096966D'  + '670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B'+ 'E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9' + 'DE2BCBF6955817183995497CEA956AE515D2261898FA0510' +'15728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64'  + 'ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7' + 'ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6B'+ 'F12FFA06D98A0864D87602733EC86A64521F2B18177B200C'+ 'BBE117577A615D6C770988C0BAD946E208E24FA074E5AB31' + '43DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF'
        # N_as_int = int(initN, base=16)
        # g_as_int = int('2', base=16)
        # passwordVerifier = pow(g_as_int, int(hashlib.sha256((salt_hexRandom + hashedString.hexdigest()).encode('utf-8')).hexdigest(), base=16), N_as_int)
        # #print(passwordVerifier)
        # # salt_int = abs(int(salt_hexRandom, base=16))
        # # salt_int_hex = hex(salt_int)[2:]
        # #salt_base64 = base64.b64encode(bytearray.fromhex(salt_hexRandom)).decode()
        # #print(salt_hexRandom)
        # #print(salt_int_hex)
        # #print(padHex(hex(passwordVerifier)[2:]))
        # print(hex(passwordVerifier))
        device_password, device_secret_verifier_config = generate_hash_device(deviceGroupKey, deviceKey)
        response = client.confirm_device(
            AccessToken=accessToken,
            DeviceKey=deviceKey,
            DeviceSecretVerifierConfig=device_secret_verifier_config,
            DeviceName='Redmi Nicholas'
        )


        # # # Step 5:
        # # # Store device keys
        # # # Step 6:
        # # # Confirm_Device

        # #'DeviceKey': response['AuthenticationResult']['NewDeviceMetadata']['DeviceKey']
        return response
