import decimal
import json
from decimal import Decimal

import simplejson as simplejson
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3

session = boto3.Session()
client = session.client("timestream-write", region_name='eu-west-1')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_angle_data'


class write_records_with_common_attributes(Resource):
    def post(self):
        # arguments to pass in from client: user_id, startTime, endTime, time, fusedAngle, flexAngle, perpAngle
        data = request.get_json()
        time_start = data['startTime']
        time_end = data['endTime']
        angle_data_list = data['angleDataList']
        print('startTime' + time_start)
        print('endTime' + time_end)
        print('ANGLEDATALIST' + str(angle_data_list))
        print("Writing records extracting common attributes")

        # current_time = self._current_milli_time()
        dimensions = [
            {'Name': 'uid', 'Value': 'user_id'},
            {'Name': 'time_start', 'Value': time_start},
            {'Name': 'time_end', 'Value': time_end}
        ]

        for angle_data in angle_data_list:
            common_attributes = {
                'Dimensions': dimensions,
                'MeasureValueType': 'DOUBLE',
                'Time': str(angle_data['timestamp']),
                'TimeUnit': 'MILLISECONDS'
            }

            fused_angle = {
                'MeasureName': 'fused_angle',
                'MeasureValue': str(angle_data['fusedAngle'])
            }

            flex_angle = {
                'MeasureName': 'flex_angle',
                'MeasureValue': str(angle_data['flexAngle'])
            }

            perp_angle = {
                'MeasureName': 'perp_angle',
                'MeasureValue': str(angle_data['perpAngle'])
            }

            records = [fused_angle, flex_angle, perp_angle]

            result = client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                          Records=records, CommonAttributes=common_attributes)
            print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])

        return 200
