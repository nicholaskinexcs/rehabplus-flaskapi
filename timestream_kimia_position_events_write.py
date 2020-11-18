from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import datetime

session = boto3.Session()
client = session.client("timestream-write", region_name='eu-west-1')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_PositionEvents_Data'


class WritePositionEventsRecords(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        time_start = datetime.datetime.utcfromtimestamp(data['startTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
        position_event = data['positionEvent']
        print(user_id)
        print(time_start)
        print(position_event)

        dimensions = [
            {'Name': 'uid', 'Value': user_id},
            {'Name': 'time_start', 'Value': time_start},
            {'Name': 'chart_time', 'Value': str(position_event['time'])},
            {'Name': 'device_date_time', 'Value': datetime.datetime.utcfromtimestamp(position_event['dateTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')},
            {'Name': 'address', 'Value': position_event['address']},
            {'Name': 'realTime', 'Value': str(position_event['realTime'])},
            {'Name': 'bufferedData', 'Value': str(position_event['bufferedData'])}
        ]

        common_attributes = {
            'Dimensions': dimensions,
            'MeasureValueType': 'VARCHAR',
            'Time': str(position_event['systemDateTime']),
            'TimeUnit': 'MILLISECONDS'
        }

        position_event_record = {
            'MeasureName': 'position_event',
            'MeasureValue': str(position_event['bendType'])
        }

        records = [position_event_record]

        result = client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                      Records=records, CommonAttributes=common_attributes)
        print("WriteRecords_Position_Event Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
        return 200
