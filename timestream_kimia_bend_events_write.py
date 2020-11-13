from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import datetime

session = boto3.Session()
client = session.client("timestream-write", region_name='eu-west-1')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_BendEvents_Data'


class WriteBendEventsRecords(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        time_start = datetime.datetime.utcfromtimestamp(data['startTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
        bend_event = data['bendEvent']
        print(user_id)
        print(time_start)
        print(bend_event)

        dimensions = [
            {'Name': 'uid', 'Value': user_id},
            {'Name': 'time_start', 'Value': time_start},
            {'Name': 'ble_address', 'Value': str(bend_event['BLEAddress'])},
            {'Name': 'real_time', 'Value': str(bend_event['realTime'])},
            {'Name': 'buffered_data', 'Value': str(bend_event['bufferedData'])},
            {'Name': 'rom_min_abs', 'Value': str(bend_event['rom_min_abs'])},
            {'Name': 'rom_max_abs', 'Value': str(bend_event['rom_max_abs'])},
            {'Name': 'count', 'Value': str(bend_event['count'])},
            {'Name': 'device_timestamp', 'Value': datetime.datetime.utcfromtimestamp(bend_event['deviceDateTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')}
        ]

        common_attributes = {
            'Dimensions': dimensions,
            'MeasureValueType': 'VARCHAR',
            'Time': str(bend_event['systemDateTime']),
            'TimeUnit': 'MILLISECONDS'
        }

        position_event_record = {
            'MeasureName': 'bend_event',
            'MeasureValue': str(bend_event['bendType'])
        }

        records = [position_event_record]

        result = client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                      Records=records, CommonAttributes=common_attributes)
        print("WriteRecords_Bend_Event Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
        return 200
