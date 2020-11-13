from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import datetime

session = boto3.Session()
client = session.client("timestream-write", region_name='eu-west-1')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_Accelerometer_Data'


class WriteAccDataRecords(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        time_start = datetime.datetime.utcfromtimestamp(data['startTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
        acc_data = data['accData']
        # print(user_id)
        # print(time_start)
        # print(acc_data)

        dimensions = [
            {'Name': 'uid', 'Value': user_id},
            {'Name': 'time_start', 'Value': time_start},
            {'Name': 'ble_address', 'Value': str(acc_data['BLEAddress'])},
        ]

        common_attributes = {
            'Dimensions': dimensions,
            'MeasureValueType': 'DOUBLE',
            'Time': str(acc_data['systemDateTime']),
            'TimeUnit': 'MILLISECONDS'
        }

        x_acc_record = {
            'MeasureName': 'x_acc',
            'MeasureValue': str(acc_data['xAcc'])
        }

        y_acc_record = {
            'MeasureName': 'y_acc',
            'MeasureValue': str(acc_data['yAcc'])
        }

        z_acc_record = {
            'MeasureName': 'z_acc',
            'MeasureValue': str(acc_data['zAcc'])
        }
        temperature_record = {
            'MeasureName': 'temperature',
            'MeasureValue': str(acc_data['temperature'])
        }
        position_record = {
            'MeasureName': 'position',
            'MeasureValue': str(acc_data['position'])
        }
        pitch_record = {
            'MeasureName': 'pitch',
            'MeasureValue': str(acc_data['pitch'])
        }

        records = [x_acc_record, y_acc_record, z_acc_record, temperature_record, position_record, pitch_record]

        result = client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                      Records=records, CommonAttributes=common_attributes)
        print("WriteRecords_Acc_Data Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
        return 200
