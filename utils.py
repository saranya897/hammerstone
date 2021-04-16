import configparser
from pymongo import MongoClient
import time
import syslog
import sys
import requests
import random
import string
import datetime
import syslog
import sys
import requests
import random as r
import smtplib
import hashlib
import random
import string
from validation import Validation
from bson.objectid import ObjectId


class Utils:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(".env")
        self.validate = Validation()

        connectionString = self.config['mongo_db_test']['string']
        try:
            conn = MongoClient(connectionString)
            print("connected to db......")

        except Exception as e:
            print("Not connected to db....", e)

        self.interim = conn.Hammerstone['Interim_users']
        self.user = conn.Hammerstone['Users']
        self.company = conn.Hammerstone['Company_profile']
        self.package = conn.Hammerstone['Packages']

    def createPackage(self, name, no_of_captains, no_of_salesmen):
        try:
            result = self.package.insert_one({
                "package_name": name,
                "no_of_captains": no_of_captains,
                "no_of_salesmen": no_of_salesmen,
                "created_time": int(time.time())
            })
        except Exception as e:
            print(e)

    def getUserOTP(self, email):
        '''
        Get the OTP from user_profile
        '''
        print("getuserOTP")
        try:
            otp = list(self.user.find({"user_email": email}, {'otp': 1}))
            otp = otp[0]['otp']
            print("OTP from user_profile: ", email, otp)
            return int(otp), True
        except Exception as e:
            # syslog.syslog(syslog.LOG_ERR, f"Exception in OTPAuthenticate:getuserOTP(utils.py) for {email}")
            return None, False

    def checkUserExists(self, email):
        '''
        To check whether a user exists in user_profile
        '''
        try:
            account = list(self.user.find({"user_email": email}, {'_id': 1}))
            print(account)
            if len(account) >= 1:
                status = True
            else:
                status = False

            return status

        except Exception as e:
            # syslog.syslog(syslog.LOG_ERR,"Exception Caught: ", str(e))
            return e

    def getOTP(self, email):
        '''
        Get the OTP from interim_profile or userprofile
        '''
        print("getOTP")
        otp, status = self.getInterOTP(email)
        print(otp, status)
        if not status:
            otp, status = self.getUserOTP(email)

        return otp, status

    def getInterOTP(self, email):
        '''
        Get the OTP from interim_profile
        '''
        print("getInterOTP")
        try:
            otp = list(self.interim.find({"user_email": email}, {'otp': 1}))
            otp = otp[0]['otp']
            print("OTP from interim: ", email, otp)
            return int(otp), True
        except Exception as e:
            # syslog.syslog(syslog.LOG_ERR, f"Exception in OTPAuthenticate:getInterOTP(utils.py) for {email}")
            return None, False

    def interimToUserProfile(self, email):
        '''
        Moving data from interim to user_profile after otp authentication
        '''
        print("Inside interimToUserProfile")
        user_list = list(self.interim.find({"user_email": email}))
        user = user_list[0]  # Getting dictionary from the list
        user['signup'] = datetime.datetime.utcnow()

        """ doing 3 things
         - Inserting to mongoDB[user_profile]
         - Deleting from mongoDB[interim]
         - Adding user_creds to Django Auth Server
        """
        try:
            # token_status = False
            # token_data ={}
            result_user = self.user.insert_one(user)
            if result_user.inserted_id != None:
                try:
                    # Delete authenticated user_profile from interim
                    result_interim = self.interim.delete_many(
                        {"user_email": email})
                    # print(result_interim)
                    # token_status,token_data = self.auth.register(user['email'],user['otp'])

                    # syslog.syslog(syslog.LOG_INFO,"Token status and Token data:" + str(token_status) +"," +str(token_data))
                    # print("Token status and Token data:" + str(token_status) +"," +str(token_data))
                    # if not token_status and "509" in token_data:
                    #    token_status, token_data = False, None
                    return user
                except Exception as e:
                    # token_status, token_data = False, "Error Code: 514, Error Occured! Please contact Customer Care!"

                    # syslog.syslog(syslog.LOG_ERR,"Exception Caught while trying to register User" + str(e) +" for user " + email)
                    return user
            # else:
            #    token_status, token_data = False, "Error Code: 514, Error Occured! Please contact Customer Care!"
            #    syslog.syslog(syslog.LOG_ERR,"Error Code: 514, Error Occured! Please contact Customer Care!")
            #    return token_status, token_data, user
        except errors.PyMongoError as e:
            # token_status, token_data = False, "Error Code: 514, Error Occured! Please contact Customer Care!"
            # syslog.syslog(
            # syslog.LOG_ERR, "Couldn't move data from Interim to User_Profile) Exception caught with message " + str(e) + " for " + email)
            return user

    def generateOTP(self):
        '''
        Generate an OTP with given range
        '''
        print("Genaerate OTP")
        otp = ""
        for i in range(6):
            if i == 0:
                otp += str(r.randint(1, 9))
            else:
                otp += str(r.randint(0, 9))
        otp = int(otp)
        # syslog.syslog(syslog.LOG_INFO,"OTP for "+ username +" is:" + str(otp))

        return otp

    # def checkcaptainExists(self, companyid):
    #     '''
    #     To check whether a user exists in user_profile
    #     '''
    #     try:
    #         company = list(self.company.find(
    #             {'_id': ObjectId(companyid)}))
    #         # number = company[0]['no_of_salesman']
    #         captain_email = company[0]['company_email']
    #         user_status = self.utils.checkcaptainExists(captain_email)

    #         print(account)
    #         if len(user_status) >= 1:
    #             status = True
    #         else:
    #             status = False

    #         return status

    #     except Exception as e:
    #         # syslog.syslog(syslog.LOG_ERR,"Exception Caught: ", str(e))
    #         return e

    def AddCustomerExecutive(self, companyid, role, user_name, user_email, user_phone):
        print(user_phone)

        status, response = self.validate.phoneNoValidate(user_phone)
        print(status, response)
        if status == False:
            return False, "Invalid phonenumber"
        status, response = self.validate.checkEmail(user_email)
        if status == False:
            return False, "Invalid Email ID"

        company = list(self.company.find(
            {'_id': ObjectId(companyid)}, {'no_of_salesman': 1}))
        salesman_number = company[0]['no_of_salesman']
        print(salesman_number)
        search = list(self.user.find(
            {'company_id': companyid}, {'role': role}))
        print("search length", len(search))
        if len(search) > salesman_number:
            return False, " customer Executive  addition not possible"
        status, password = self.generateRandomPassword()
        print("random password is", status, password)

        status, password_hashed = self.encodePassword(password)
        print("password is", status, password_hashed)

        if status == False:
            return False, password_hashed
        try:

            result_user = self.user.insert_one({'user_name': user_name,
                                                'user_email': user_email,
                                                'user_phone': user_phone,
                                                'user_password': password_hashed,
                                                'company_id': companyid,
                                                'role': role,
                                                'created_time': datetime.datetime.now()})
        except Exception as e:
            return False, "insertion Failed"
        print(result_user)

        message = f"Your password is {password}.Please login !!!"
        subject = "CUSTOMER EXECUTIVE PASSWORD"

        status, response, code = self.sendEmail(user_email, message, subject)

        if status == False:
            return False, "password sending unsuccessfull"

        return True, "sucessfully  customer executive inserted"

    def encodePassword(self, password):
        try:
            salt = self.config['hashing']['secret_key']
            salted_pwd = password + salt
            hashed_string = hashlib.sha256(salted_pwd.encode())
            hashed_password = hashed_string.hexdigest()

            return True, hashed_password
        except Exception as e:
            return False, str(e)

    def generateRandomPassword(self):
        try:
            password_new = ''.join(random.choice(string.ascii_lowercase +
                                                 string.digits) for i in range(8))
            return True, password_new
        except Exception as e:
            return False, str(e)

    def sendEmail(self, email_id, message, subject):
        from_address = self.config['email']['email_id']
        login = from_address
        to_address = email_id
        password = self.config['email']['password']
        mail_subject = subject
        priority = '2'
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\nPriority: %s\r\n\r\n"
               % (from_address, to_address, mail_subject, priority))
        msg = msg + message

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            server.login(login, password)
            server.sendmail(from_address, to_address, msg)
            server.quit()
            return True, "Mail sent", "200"
        except Exception as e:
            return False, e, "500"

# ob = Utils()
# ob.find("607794284923958524657b31", "customer",
        # "sabarisa", "sranya@gmail.com", "7900", "ssss")
# ob.createPackage("Package_2",2,10)
