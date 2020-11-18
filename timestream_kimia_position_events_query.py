from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import json

session = boto3.Session()
client = session.client("timestream-query", region_name='eu-west-1')
paginator = client.get_paginator('query')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_PositionEvents_Data'


class QueryKIMIASessions(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        print(user_id)
        unique_session_start_time = self.QuerySessionStartTime(user_id)
        print(unique_session_start_time)
        return unique_session_start_time

    def QuerySessionStartTime(self, user_id):
        query_session_start_time = f"""
                            SELECT time_start FROM {DATABASE_NAME}.{TABLE_NAME}
                            WHERE uid = '{user_id}'
                            ORDER BY time ASC
                            """
        page_iterator = paginator.paginate(QueryString=query_session_start_time)
        record_keys = []
        for page in page_iterator:
            time_start_keys = self._parse_query_result_session(page)
            record_keys.extend(time_start_keys)
        unique_session_start_time = list(dict.fromkeys(record_keys))
        return unique_session_start_time

    def _parse_query_result_session(self, query_result):
        time_start_keys = []
        for row in query_result['Rows']:
            data = row['Data'][0]['ScalarValue']
            time_start_keys.append(data)
        return time_start_keys


class QuerySessionPositionEventRecord(Resource):
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
                    SELECT measure_name, measure_value::varchar, time, chart_time, time_start FROM {DATABASE_NAME}.{TABLE_NAME} 
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
        # print(session_records)
        print('RECORD ENDS HERE')
        return session_records

    def _parse_query_result_record(self, query_result):
        column_info = query_result['ColumnInfo']
        time_start = query_result['Rows'][0]['Data'][4]['ScalarValue']
        position_event_list = []
        for row in query_result['Rows']:
            data = row['Data']
            measure_type = data[0]['ScalarValue']
            position_event_value = data[1]['ScalarValue']
            time = data[2]['ScalarValue']
            chart_time = data[3]['ScalarValue']
            position_event_list.append([position_event_value, chart_time, time])
        return position_event_list
