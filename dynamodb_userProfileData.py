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
dynamodb_DB = boto3.resource('dynamodb')
UserProfileData_table = dynamodb_DB.Table(__TableName__)

video_put_args = reqparse.RequestParser()
video_put_args.add_argument('name', type=str, help='Name of the video is required', required=True)
video_put_args.add_argument('views', type=int, help='Views of the video is required', required=True)
video_put_args.add_argument('likes', type=int, help='Likes on the video is required', required=True)

UserProfileData_Dict = {}


# def abort_if_video_id_doesnt_exist(video_id):
#    if(video_id) not in videos:
#        abort(404, message = 'Could not find video...')

# def abort_if_video_exist(video_id):
#    if(video_id) in videos:
#        abort(409, message = 'Video already exists with that ID...')

class UserProfileData(Resource):
    def get(self, uid):
        response=UserProfileData_table.query(
            KeyConditionExpression=Key('uid').eq(uid),
            ProjectionExpression='uid, email, firstName, lastName, mobile, #userRole, signedInStatus, taggedUser, '
                                 'requests, sharedWorkouts, notifications, appointments, pastAppointments, '
                                 'billingAddress, directPayments',
            ExpressionAttributeNames={
                '#userRole': 'role'
            }
        )
        print(response)
        return response['Items'][0]

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


# class AllUserProfileData(Resource):
#     def get(self):
#         return UserProfileData_Dict


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
        print(response['Items'])
        return response['Items']


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


