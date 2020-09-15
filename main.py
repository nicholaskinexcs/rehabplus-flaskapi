from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
from auth import*
from dynamodb_userProfileData import*
#
app = Flask(__name__)
api = Api(app)

api.add_resource(UserProfileData, '/userProfileData/<string:uid>')
api.add_resource(AllUserProfileData, '/userProfileData/allProfiles')
api.add_resource(SignUp, '/signup')
api.add_resource(ConfirmSignUp, '/confirmSignUp')
api.add_resource(ResendVerifictionCode, '/resendVerificationCode')
api.add_resource(ForgotPassword, '/forgotPassword')
api.add_resource(ConfirmForgotPassword, '/confirmforgotPassword')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(GetUser, '/getUser')

if __name__ == '__main__':
    app.run(host='172.20.10.2', port=5000, debug=True)
