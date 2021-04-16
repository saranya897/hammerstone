import grpc
from concurrent import futures
import random as r
from pymongo import MongoClient
import hammerstone_pb2
import hammerstone_pb2_grpc
import configparser
from utils import Utils
import datetime
import requests
import syslog


class ProfileService(hammerstone_pb2_grpc.ProfileServiceServicer):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('.env')
        self.utils = Utils()

    # def registerComapny(self):

        # @TODO get inputs

        # @TODO validate inputs

        # @TODO insert data into comapny profile

        # @TODO insert email,pasword,phone etc to interim

        # @TODO Generate random OTP and send it to the email id provided as input

        # @TODO Return necessary response

    def otpAuthenticate(self, request, context):

        # syslog(LOG_INFO,f"Getting params from client: OtpAuthenticate {request.email}")
        # print("\n\nGetting params from client: OtpAuthenticate")
        otp_got = request.otp
        email = request.email

        ResponseStatus = {}
        user_name, user_phone, user_email = None, None, None
        user_status = self.utils.checkUserExists(email)
        print("user_status", user_status)
        otp, status = self.utils.getOTP(email)
        print("otp, status", otp, status)
        if otp_got != otp:
            ResponseStatus['status_code'] = False
            ResponseStatus['status_message'] = "400: Enter valid OTP"
            return hammerstone_pb2.OtpAuthResponse(resp=ResponseStatus,
                                                   user_name=user_name,
                                                   user_phone=user_phone,
                                                   user_email=user_email
                                                   )

        if user_status:
            ResponseStatus['status_code'] = False
            ResponseStatus['status_message'] = "User already exists!"
            return hammerstone_pb2.OtpAuthResponse(resp=ResponseStatus,
                                                   user_name=user_name,
                                                   user_phone=user_phone,
                                                   user_email=user_email
                                                   )
        else:
            user = self.utils.interimToUserProfile(email)
            # token_status, token_data, user = self.utils.interimToUserProfile(email)

        # if not token_status:
        #     syslog(LOG_INFO,f"Token creation from Auth Server for user {str(email)} failed")
        #     ResponseStatus['status_code'] = False
        #     ResponseStatus['status_message'] = "500: Something went wrong"
        #     return hammerstone_pb2.OtpAuthResponse( resp          = {ResponseStatus},
        #                                         first_name    = f_name,
        #                                         last_name     = l_name,
        #                                         email         = email
            #   )
        if not user:
            # syslog(LOG_INFO,f"insertion  failled")
            ResponseStatus['status_code'] = False
            ResponseStatus['status_message'] = "500: Something went wrong"
            return hammerstone_pb2.OtpAuthResponse(resp=ResponseStatus,
                                                   user_name=user_name,
                                                   user_phone=user_phone,
                                                   user_email=user_email
                                                   )

        ResponseStatus['status_code'] = True
        ResponseStatus['status_message'] = "200: Success"
        # print(ResponseStatus, user, token_data)
        return hammerstone_pb2.OtpAuthResponse(resp=ResponseStatus,
                                               user_name=user['user_name'],
                                               user_phone=user['user_phone'],
                                               user_email=user['user_email']
                                               )
    # def loginUser(self):

    #     # @TODO Get the email and password

    #     # @TODO Perform required validations

    #     # @TODO If all the validation steps are passed check whether a user exists with the entered email

    #     # @TODO If yes check the password of user matches the entered password

    #     # @TODO     5. Give proper responses

    # def forgotPassword(self):

        # @TODO Get email id of user

        # @TODO Perform email validation

        # @TODO Check whether a user exists in userprofile collection

        # @TODO If not give error message

        # @TODO Else create a random password.

        # @TODO Update the new password in DB (SHA-2 hashed).

        # @TODO     7. Then send the new password to user via email
    def addsalesman(self, request, context):

        user_name = request.user_name
        user_phone = request.user_phone
        user_email = request.user_email

        company_id = request.company_id
        role = request.role

        # user_status = self.utils.checkcaptainExists(company_id)
        # if user_status == False:
        #         return hammerstone_pb2.Response(status_code      = status,
        #                                         status_message   = message)
        status, message = self.utils.AddCustomerExecutive(
            company_id, role, user_name, user_email, user_phone)
        if status == False:
            return hammerstone_pb2.Response(status_code=status,
                                            status_message=message)
        return hammerstone_pb2.Response(status_code=status,
                                        status_message=message)
