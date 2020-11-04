from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
import json
from timestream_query_model import *

session = boto3.Session()
client = session.client("timestream-query", region_name='eu-west-1')
paginator = client.get_paginator('query')

DATABASE_NAME = 'Timestream_KIMIA'
TABLE_NAME = 'KIMIA_angle_data'

SELECT_ALL = f"SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}"


class RunQueryBasic1(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        print(user_id)
        unique_session_start_time = self.QuerySessionStartTime(user_id)
        print(unique_session_start_time)
        # TODO remove the [0] list index in the args, maybe no need
        session_record = self.QueryRecordForSession(unique_session_start_time[0], user_id)
        return json.dumps(session_record[0].to_json())

    def QuerySessionStartTime(self, user_id):
        query_session_start_time = f"""
                            SELECT time_start FROM {DATABASE_NAME}.{TABLE_NAME}
                            WHERE uid = '{user_id}'
                            ORDER BY time DESC
                            """
        page_iterator = paginator.paginate(QueryString=query_session_start_time)
        record_keys = []
        for page in page_iterator:
            time_start_keys = self._parse_query_result_session(page)
            record_keys.extend(time_start_keys)
        unique_session_start_time = list(dict.fromkeys(record_keys))
        return unique_session_start_time

    def QueryRecordForSession(self, unique_session_start_time, user_id):
        query_record_session = f"""
                    SELECT measure_name, measure_value::double, time, chart_time, time_start, time_end FROM {DATABASE_NAME}.{TABLE_NAME}
                    WHERE uid = '{user_id}' AND time_start = '{unique_session_start_time}'
                    ORDER BY time DESC
                    """
        page_iterator = paginator.paginate(QueryString=query_record_session)
        print('RECORD STARTS HERE')
        session_records = []
        for page in page_iterator:
            # print(page)
            record_model = self._parse_query_result_record(page)
            session_records.append(record_model)
            print("FLEX ANGLES")
            print(record_model.flex_angle_list)
            print("FUSED ANGLES")
            print(record_model.fused_angle_list)
            print("PERP ANGLES")
            print(record_model.perp_angle_list)
            print(len(record_model.flex_angle_list))
            print(len(record_model.fused_angle_list))
            print(len(record_model.fused_angle_list))
            print(record_model.time_start)
            print(record_model.time_end)
        print('RECORD ENDS HERE')
        return session_records

    def _parse_query_result_session(self, query_result):
        time_start_keys = []
        for row in query_result['Rows']:
            data = row['Data'][0]['ScalarValue']
            time_start_keys.append(data)
        return time_start_keys

    def _parse_query_result_record(self, query_result):
        # TODO not only can do flex_list
        column_info = query_result['ColumnInfo']
        time_start = query_result['Rows'][0]['Data'][4]
        time_end = query_result['Rows'][0]['Data'][5]
        flex_angle_list = []
        fused_angle_list = []
        perp_angle_list = []
        for row in query_result['Rows']:
            data = row['Data']
            angle_type = data[0]['ScalarValue']
            angle_value = data[1]['ScalarValue']
            time = data[2]['ScalarValue']
            chart_time = data[3]['ScalarValue']
            if angle_type == 'flex_angle':
                flex_angle_list.append([angle_value, chart_time, time])
            elif angle_type == 'fused_angle':
                fused_angle_list.append([angle_value, chart_time, time])
            elif angle_type == 'perp_angle':
                perp_angle_list.append([angle_value, chart_time, time])
        return TimestreamQueryModel(flex_angle_list=flex_angle_list, fused_angle_list=fused_angle_list, perp_angle_list=perp_angle_list, time_start=time_start, time_end=time_end)

    def _parse_row(self, column_info, row):
        data = row['Data']
        row_output = []
        for j in range(len(data)):
            info = column_info[j]
            datum = data[j]
            row_output.append(self._parse_datum(info, datum))
        print(row_output)

    def _parse_datum(self, info, datum):
        # TODO make json of col-row data pairs and add it to row_output
        return "{}"
