from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import json
from timestream_query_model import *

session = boto3.Session()
client = session.client("timestream-query", region_name='eu-west-1')
paginator = client.get_paginator('query')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_Accelerometer_Data'

SELECT_ALL = f"SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}"


class QuerySessionAccDataRecord(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        unique_session_start_time = data['sessionStartTime']
        print(user_id)
        print(unique_session_start_time)
        session_record = self.QueryRecordForSession(unique_session_start_time, user_id)
        return session_record.to_json()

    def QueryRecordForSession(self, unique_session_start_time, user_id):
        query_record_session = f"""
                    SELECT measure_name, measure_value::double, time, time_start, ble_address FROM {DATABASE_NAME}.{TABLE_NAME}
                    WHERE uid = '{user_id}' AND time_start = '{unique_session_start_time}'
                    ORDER BY time ASC
                    """
        page_iterator = paginator.paginate(QueryString=query_record_session)
        print('RECORD STARTS HERE')
        # session_records = []
        x_acc_list = []
        y_acc_list = []
        z_acc_list = []
        temperature_list = []
        position_list = []
        pitch_list = []
        time_start = ''
        count = 0
        for page in page_iterator:
            count += 1
            # print(page)
            page_result = self._parse_query_result_record(page)
            if len(page_result) != 0:
                x_acc_list.extend(page_result[0])
                y_acc_list.extend(page_result[1])
                z_acc_list.extend(page_result[2])
                temperature_list.extend(page_result[3])
                position_list.extend(page_result[4])
                pitch_list.extend(page_result[5])
                time_start = page_result[6]
        session_records = TimestreamQueryAccDataModel(x_acc_list=x_acc_list, y_acc_list=y_acc_list,
                                                      z_acc_list=z_acc_list, temperature_list=temperature_list,
                                                      position_list=position_list, pitch_list=pitch_list,
                                                      time_start=time_start)
        print('RECORD ENDS HERE')
        print('HOW MANY PAGES')
        print(count)
        return session_records

    def _parse_query_result_record(self, query_result):
        if len(query_result['Rows']) != 0:
            column_info = query_result['ColumnInfo']
            time_start = query_result['Rows'][-1]['Data'][3]['ScalarValue']
            x_acc_list = []
            y_acc_list = []
            z_acc_list = []
            temperature_list = []
            position_list = []
            pitch_list = []
            for row in query_result['Rows']:
                data = row['Data']
                measure_type = data[0]['ScalarValue']
                measure_value = data[1]['ScalarValue']
                time = data[2]['ScalarValue']
                if measure_type == 'x_acc':
                    x_acc_list.append([measure_value, time])
                elif measure_type == 'y_acc':
                    y_acc_list.append([measure_value, time])
                elif measure_type == 'z_acc':
                    z_acc_list.append([measure_value, time])
                elif measure_type == 'temperature':
                    temperature_list.append([measure_value, time])
                elif measure_type == 'position':
                    position_list.append([measure_value, time])
                elif measure_type == 'pitch':
                    pitch_list.append([measure_value, time])
            return [x_acc_list, y_acc_list, z_acc_list, temperature_list, position_list, pitch_list, time_start]
        else:
            return []

