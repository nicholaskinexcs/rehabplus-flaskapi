from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3


__TableName__ = 'UserProfileData'
Primary_Column_Name = 'uid'

#client = boto3.client('dynamodb')
dynamodb_DB = boto3.resource('dynamodb')
UserProfileData_table = dynamodb_DB.Table(__TableName__)

video_put_args = reqparse.RequestParser()
video_put_args.add_argument('name', type=str, help='Name of the video is required', required=True)
video_put_args.add_argument('views', type=int, help='Views of the video is required', required=True)
video_put_args.add_argument('likes', type=int, help='Likes on the video is required', required=True)

UserProfileData_Dict = {}
#def abort_if_video_id_doesnt_exist(video_id):
#    if(video_id) not in videos:
#        abort(404, message = 'Could not find video...')

#def abort_if_video_exist(video_id):
#    if(video_id) in videos:
#        abort(409, message = 'Video already exists with that ID...')

class UserProfileData(Resource):
    def get(self, uid):
        response = UserProfileData_table.get_item(
            Key = {
                'uid': uid
            }
        )
        return response['Item']

    def put(self, uid):
        userProfileData = request.get_json()
        response = UserProfileData_table.put_item(Item = userProfileData)
        return response['ResponseMetadata']['HTTPStatusCode']

    def delete(self, uid):
        del UserProfileData_Dict[index_id]
        return '', 204

class AllUserProfileData(Resource):
    def get(self):
        return UserProfileData_Dict
