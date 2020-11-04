from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import boto3
from auth import*
from dynamodb_userProfileData import*
from dynamodb_questionnaire import*
from timestream_kimia_write import*
from timestream_kimia_query import*
#
app = Flask(__name__)
api = Api(app)

api.add_resource(UserProfileData, '/userProfileData/<string:uid>')
api.add_resource(SignUp, '/signup')
api.add_resource(ConfirmSignUp, '/confirmSignUp')
api.add_resource(ResendVerifictionCode, '/resendVerificationCode')
api.add_resource(ForgotPassword, '/forgotPassword')
api.add_resource(ConfirmForgotPassword, '/confirmforgotPassword')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(GetUser, '/getUser')
api.add_resource(AllPatientProfileData, '/getAllPatientProfileData/<string:clinician_uid>')
api.add_resource(AllUserProfileData, '/allUserProfileData')
api.add_resource(PatientSearch, '/patientSearch/<string:email>')
api.add_resource(RequestProfiles, '/requestProfiles')
api.add_resource(clearNotification, '/clearNotification')
api.add_resource(clearPendingPatientRequest, '/clearPendingPatientRequest')
api.add_resource(AddSurveyData, '/addSurveyData/<string:uid>')
api.add_resource(GetVASData, '/getVASData/<string:uid>')
api.add_resource(GetKOOSData, '/getKOOSData/<string:uid>')
api.add_resource(GetBarthelData, '/getBarthelData/<string:uid>')
api.add_resource(GetRankinData, '/getRankinData/<string:uid>')
api.add_resource(GetKSSPreOpData, '/getKSSPreOpData/<string:uid>')
api.add_resource(GetKSSPostOpData, '/getKSSPostOpData/<string:uid>')
api.add_resource(GetWorkoutSurveyData, '/getWorkoutSurveyData/<string:uid>')
api.add_resource(UpdateFCMTokenData, '/updateDeviceToken/<string:uid>')
api.add_resource(ClearFCMTokenData, '/clearDeviceToken/<string:uid>')
api.add_resource(GetDeviceTokens, '/getDeviceTokens/<string:uid>')
api.add_resource(GetTaggedUserDeviceTokens, '/getTaggedUserDeviceTokens')
api.add_resource(WriteRecordsWithCommonAttributes, '/storeAngleData')
api.add_resource(RunQueryBasic1, '/queryAngleData')

if __name__ == '__main__':
    app.run(host='172.20.10.4', port=5000, debug=True)
