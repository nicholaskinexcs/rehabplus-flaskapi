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


# class QueryKIMIASessions(Resource):
#     def post(self):
#         data = request.get_json()
#         user_id = data['user_id']
#         print(user_id)
#         unique_session_start_time = self.QuerySessionStartTime(user_id)
#         print(unique_session_start_time)
#         return unique_session_start_time
#
#     def QuerySessionStartTime(self, user_id):
#         query_session_start_time = f"""
#                             SELECT time_start FROM {DATABASE_NAME}.{TABLE_NAME}
#                             WHERE uid = '{user_id}'
#                             ORDER BY time DESC
#                             """
#         page_iterator = paginator.paginate(QueryString=query_session_start_time)
#         record_keys = []
#         for page in page_iterator:
#             time_start_keys = self._parse_query_result_session(page)
#             record_keys.extend(time_start_keys)
#         unique_session_start_time = list(dict.fromkeys(record_keys))
#         return unique_session_start_time
#
#     def _parse_query_result_session(self, query_result):
#         time_start_keys = []
#         for row in query_result['Rows']:
#             data = row['Data'][0]['ScalarValue']
#             time_start_keys.append(data)
#         return time_start_keys


class QuerySessionRecord(Resource):
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
                    SELECT measure_name, measure_value::double, time, chart_time, time_start, time_end FROM {DATABASE_NAME}.{TABLE_NAME}
                    WHERE uid = '{user_id}' AND time_start = '{unique_session_start_time}'
                    ORDER BY time ASC
                    """
        page_iterator = paginator.paginate(QueryString=query_record_session)
        print('RECORD STARTS HERE')
        # session_records = []
        flex_angle_list = []
        fused_angle_list = []
        perp_angle_list = []
        time_start = ''
        time_end = ''
        count = 0
        for page in page_iterator:
            # print(page)
            count += 1
            page_result = self._parse_query_result_record(page)
            if len(page_result) != 0:
                flex_angle_list.extend(page_result[0])
                fused_angle_list.extend(page_result[1])
                perp_angle_list.extend(page_result[2])
                time_start = page_result[3]
                time_end = page_result[4]
        flex_angle_list.pop()
        fused_angle_list.pop()
        perp_angle_list.pop()
        session_records = TimestreamQueryModel(flex_angle_list=flex_angle_list, fused_angle_list=fused_angle_list,
                                               perp_angle_list=perp_angle_list, time_start=time_start,
                                               time_end=time_end)
        print('RECORD ENDS HERE')
        print('HOW MANY PAGES')
        print(count)
        return session_records

    def _parse_query_result_record(self, query_result):
        if len(query_result['Rows']) != 0:
            column_info = query_result['ColumnInfo']
            time_start = query_result['Rows'][-1]['Data'][4]['ScalarValue']
            time_end = query_result['Rows'][-1]['Data'][5]['ScalarValue']
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
            return [flex_angle_list, fused_angle_list, perp_angle_list, time_start, time_end]
        else:
            return []

