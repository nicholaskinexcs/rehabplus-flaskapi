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


class AddSurveyData(Resource):
    def patch(self, uid):
        data = request.get_json()
        attr_name = data['attr_name']
        attr_value = json.loads(json.dumps(data['attr_value']), parse_float=Decimal)
        response = UserProfileData_table.update_item(
            Key={
                'uid': uid
            },
            UpdateExpression='SET ' + attr_name + '=list_append(if_not_exists(' + attr_name + ',:SurveyList), :value)',
            ExpressionAttributeValues={
                ':value': [attr_value],
                ':SurveyList': []
            },
            ReturnValues='NONE'
        )
        print(response)
        return response['ResponseMetadata']['HTTPStatusCode']


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class GetVASData(Resource):
    def get(self, uid):
        response = UserProfileData_table.query(
            KeyConditionExpression=Key('uid').eq(uid),
            ProjectionExpression='VAS',
        )
        print(bool(response['Items'][0]))
        print(response['Items'])
        print(response['Count'])
        if response['Count'] == 1:
            if bool(response['Items'][0]):
                # print(simplejson.dumps(response['Items']))
                print(json.loads(simplejson.dumps(response['Items'])))
                return json.loads(simplejson.dumps(response['Items']))
                # return response['Items']
            else:
                return None
        else:
            return json.loads(simplejson.dumps(response['Items']))
            # return response['Items']


class GetKOOSData(Resource):
    def get(self, uid):
        response = UserProfileData_table.query(
            KeyConditionExpression=Key('uid').eq(uid),
            ProjectionExpression='KOOS',
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

