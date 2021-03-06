import decimal
import json
from decimal import Decimal

import simplejson as simplejson
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3

__TableName__ = 'UserProfileData'
Primary_Column_Name = 'uid'

# client = boto3.client('dynamodb')
dynamodb_DB = boto3.resource('dynamodb', region_name="ap-southeast-1")
UserProfileData_table = dynamodb_DB.Table(__TableName__)


class UserProfileData(Resource):
    def get(self, uid):
        response = UserProfileData_table.query(
            KeyConditionExpression=Key('uid').eq(uid),
            ProjectionExpression='uid, email, firstName, lastName, mobile, #userRole, signedInStatus, taggedUser, '
                                 'requests, sharedWorkouts, notifications, appointments, pastAppointments, '
                                 'billingAddress, directPayments',
            ExpressionAttributeNames={
                '#userRole': 'role'
            }
        )
        print(response)
        return json.loads(simplejson.dumps(response['Items'][0]))

    def put(self, uid):
        userProfileData = request.get_json()
        response = UserProfileData_table.put_item(Item=userProfileData)
        return response['ResponseMetadata']['HTTPStatusCode']

    def patch(self, uid):
        data = request.get_json()
        key = data['key']
        attr_name = data['attr_name']
        attr_value = data['attr_value']
        response = UserProfileData_table.update_item(
            Key={
                'uid': uid
            },
            UpdateExpression='SET ' + attr_name + '=list_append(' + attr_name + ',:value)',
            ExpressionAttributeValues={
                ':value': [attr_value]
            },
            ReturnValues='NONE'
        )
        return response


class AllPatientProfileData(Resource):
    def get(self, clinician_uid):
        response = UserProfileData_table.scan(
            FilterExpression=Attr('taggedUser').contains(clinician_uid),
            ProjectionExpression='uid, email, firstName, lastName, mobile, #userRole, signedInStatus, taggedUser, '
                                 'requests, sharedWorkouts, notifications, appointments, pastAppointments, '
                                 'billingAddress, directPayments',
            ExpressionAttributeNames={
                '#userRole': 'role'
            }
        )
        print(json.loads(simplejson.dumps(response['Items'])))
        return json.loads(simplejson.dumps(response['Items']))


class AllUserProfileData(Resource):
    def get(self):
        response = UserProfileData_table.scan(
            ProjectionExpression='uid, email, firstName, lastName, mobile, #userRole, signedInStatus, taggedUser, '
                                 'requests, sharedWorkouts, notifications, appointments, pastAppointments, '
                                 'billingAddress, directPayments',
            ExpressionAttributeNames={
                '#userRole': 'role'
            }
        )
        print(response['Items'])
        return response['Items']


class PatientSearch(Resource):
    def get(self, email):
        response = UserProfileData_table.scan(
            FilterExpression=Attr('email').eq(email),
            ProjectionExpression='uid, email, firstName, lastName, mobile, #userRole, signedInStatus, taggedUser, '
                                 'requests, sharedWorkouts, notifications, appointments, pastAppointments, '
                                 'billingAddress, directPayments',
            ExpressionAttributeNames={
                '#userRole': 'role'
            }
        )
        print(response['Items'])
        return response['Items']


class RequestProfiles(Resource):
    def post(self):
        data = request.get_json()
        request_list = data['requestList']
        print(request_list)

        response = UserProfileData_table.scan(
            FilterExpression=Attr('uid').is_in(request_list),
            ProjectionExpression='uid, email, firstName, lastName, mobile, #userRole, signedInStatus, taggedUser, '
                                 'requests, sharedWorkouts, notifications, appointments, pastAppointments, '
                                 'billingAddress, directPayments',
            ExpressionAttributeNames={
                '#userRole': 'role'
            }
        )
        print(response['Items'])
        return response['Items']


class clearNotification(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['userId']
        notification_obj = data['notificationModel']
        # print(notification_obj)
        # need to get the list
        patient_item = UserProfileData_table.get_item(
            Key={
                'uid': user_id
            }
        )
        notification_list = patient_item['Item']['notifications']
        # print(notification_list)

        # then find the index of the element
        index = notification_list.index(notification_obj)
        # print(index)

        # then use REMOVE using the index of the item to remove it

        response = UserProfileData_table.update_item(
            Key={
                'uid': user_id
            },
            UpdateExpression='REMOVE notifications[' + str(index) + ']',
            ReturnValues='NONE'
        )
        print(response)
        return response


class clearPendingPatientRequest(Resource):
    def post(self):
        data = request.get_json()
        patient_id = data['patientId']
        clinician_id = data['clinicianId']
        # print(notification_obj)
        # need to get the list
        patient_item = UserProfileData_table.get_item(
            Key={
                'uid': clinician_id
            }
        )
        notification_list = patient_item['Item']['requests']
        # print(notification_list)

        # then find the index of the element
        index = notification_list.index(patient_id)
        # print(index)

        # then use REMOVE using the index of the item to remove it

        response = UserProfileData_table.update_item(
            Key={
                'uid': clinician_id
            },
            UpdateExpression='REMOVE requests[' + str(index) + ']',
            ReturnValues='NONE'
        )
        print(response)
        return response


class UpdateFCMTokenData(Resource):
    def patch(self, uid):
        data = request.get_json()
        attr_name = data['attr_name']
        attr_value = data['attr_value']
        response = UserProfileData_table.update_item(
            Key={
                'uid': uid
            },
            UpdateExpression='SET ' + attr_name + '=list_append(if_not_exists(' + attr_name + ',:FCMList), :value)',
            ExpressionAttributeValues={
                ':value': [attr_value],
                ':FCMList': []
            },
            ReturnValues='NONE'
        )
        print(response)
        return response['ResponseMetadata']['HTTPStatusCode']


class ClearFCMTokenData(Resource):
    def patch(self, uid):
        data = request.get_json()
        attr_name = data['attr_name']
        attr_value = data['attr_value']
        response = UserProfileData_table.update_item(
            Key={
                'uid': uid
            },
            UpdateExpression='SET ' + attr_name + '=:FCMList',
            ExpressionAttributeValues={
                ':FCMList': []
            },
            ReturnValues='NONE'
        )
        print(response)
        return response['ResponseMetadata']['HTTPStatusCode']


class GetDeviceTokens(Resource):
    def get(self, uid):
        response = UserProfileData_table.query(
            KeyConditionExpression=Key('uid').eq(uid),
            ProjectionExpression='DeviceToken',
        )
        print(bool(response['Items'][0]))
        print(response['Items'])
        print(response['Count'])
        if response['Count'] == 1:
            if bool(response['Items'][0]):
                print(simplejson.dumps(response['Items']))
                print(json.loads(simplejson.dumps(response['Items'])))
                return json.loads(simplejson.dumps(response['Items']))
            else:
                return None
        else:
            return json.loads(simplejson.dumps(response['Items']))


class GetTaggedUserDeviceTokens(Resource):
    def post(self):
        data = request.get_json()
        tagged_user_list = data['taggedUserList']
        print(tagged_user_list)

        response = UserProfileData_table.scan(
            FilterExpression=Attr('uid').is_in(tagged_user_list),
            ProjectionExpression='DeviceToken',
        )
        print(response['Items'])
        return response['Items']
