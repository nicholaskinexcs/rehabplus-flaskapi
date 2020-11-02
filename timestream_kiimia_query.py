from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3

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
        basic_query_1 = f"""
                    SELECT * 
                    FROM {DATABASE_NAME}.{TABLE_NAME} 
                    WHERE uid = {user_id}
                    ORDER BY time DESC LIMIT 100
                    """
        page_iterator = paginator.paginate(QueryString=SELECT_ALL)
        for page in page_iterator:
            print(page)
            self._parse_query_result(page)
        return 200

    def _parse_query_result(self, query_result):
        column_info = query_result['ColumnInfo']

        print("Metadata: %s" % column_info)
        print("Data: ")
        for row in query_result['Rows']:
            print(self._parse_row(column_info, row))

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
