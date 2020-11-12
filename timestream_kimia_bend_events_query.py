from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import json
import datetime

session = boto3.Session()
client = session.client("timestream-query", region_name='eu-west-1')
paginator = client.get_paginator('query')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_BendEvents_Data'

class QuerySessionBendEventRecord(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        unique_session_start_time = data['sessionStartTime']
        print(user_id)
        print(unique_session_start_time)
        session_record = self.QueryRecordForSession(unique_session_start_time, user_id)
        return session_record

    def QueryRecordForSession(self, unique_session_start_time, user_id):
        query_record_session = f"""
                    SELECT measure_name, measure_value::varchar, time, device_timestamp, time_start, real_time, buffered_data, count, rom_min_abs, rom_max_abs, ble_address  FROM {DATABASE_NAME}.{TABLE_NAME} 
                    WHERE uid = '{user_id}' AND time_start = '{unique_session_start_time}'
                    ORDER BY time ASC
                    """
        page_iterator = paginator.paginate(QueryString=query_record_session)
        print('RECORD STARTS HERE')
        session_records = []
        for page in page_iterator:
            # print(page)
            position_event_model = self._parse_query_result_record(page)
            session_records.extend(position_event_model)
        print(session_records)
        print('RECORD ENDS HERE')
        return session_records

    def _parse_query_result_record(self, query_result):
        column_info = query_result['ColumnInfo']
        time_start = query_result['Rows'][0]['Data'][4]['ScalarValue']
        start_time_date_time = datetime.datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S.%f')
        position_event_list = []
        for row in query_result['Rows']:
            data = row['Data']
            measure_name = data[0]['ScalarValue']
            measure_value = data[1]['ScalarValue']
            time = data[2]['ScalarValue']
            device_timestamp = data[3]['ScalarValue']
            time_start = data[4]['ScalarValue']
            real_time = data[5]['ScalarValue']
            buffered_data = data[6]['ScalarValue']
            count = data[7]['ScalarValue']
            rom_min_abs = data[8]['ScalarValue']
            rom_max_abs = data[9]['ScalarValue']
            ble_address = data[10]['ScalarValue']
            # chart_time = systemDateTime(aka time) - time_start (in milliseconds)
            system_date_time = datetime.datetime.strptime(time[:-3], '%Y-%m-%d %H:%M:%S.%f')
            chart_time = (system_date_time - start_time_date_time).total_seconds()
            # print(chart_time.total_seconds())
            position_event_list.append([measure_value, chart_time, time])
        return position_event_list
