from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import datetime

session = boto3.Session()
client = session.client("timestream-write", region_name='eu-west-1')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_angle_data'


class WriteRecordsWithCommonAttributes(Resource):
    def post(self):
        # arguments to pass in from client: user_id, startTime, endTime, time, fusedAngle, flexAngle, perpAngle
        data = request.get_json()
        user_id = data['user_id']
        time_start = datetime.datetime.utcfromtimestamp(data['startTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
        time_end = datetime.datetime.utcfromtimestamp(data['endTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
        angle_data_list = data['angleDataList']
        print('startTime' + time_start)
        print('endTime' + time_end)
        print('ANGLEDATALIST' + str(angle_data_list))
        print("Writing records extracting common attributes")

        # current_time = self._current_milli_time()

        for angle_data in angle_data_list:
            dimensions = [
                {'Name': 'uid', 'Value': user_id},
                {'Name': 'time_start', 'Value': time_start},
                {'Name': 'time_end', 'Value': time_end},
                {'Name': 'chart_time', 'Value': str(angle_data['time'])}
            ]

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
