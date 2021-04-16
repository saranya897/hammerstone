import configparser
from pymongo import MongoClient
import time
import re
import string
import random
import smtplib
from bson import ObjectId
from pprint import pprint
import random as r


class Validation:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('.env')

    def validateObjectId(self, object_id):
        print("inside object id validation")
        try:
            if ObjectId.is_valid(object_id):
                return True, "Valid object Id"
            return False, "Invalid Object Id"

        except Exception as e:
            return False, str(e)

    def phoneNoValidate(self, user_phone):
        try:
            # phone = int(user_phone)
            print("inside validation", user_phone, type(user_phone))
            if re.fullmatch(r'[0-9]{1,10}', user_phone):
                print("ok number")
                return True, "Phone Number OK"
            return False, "Invalid Phone Number"
        except Exception as e:
            print(e)
            return False, e

    def pwdValidate(self, password):
        try:
            # print(password)
            if re.fullmatch(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#\$&*~]).{8,}$', password):
                return True, "OK"
            return False, "Invalid Password"
        except Exception as e:
            print(e)
            return False, e

    def checkEmail(self, email):
        try:
            if (not re.match(r"[^@]+@[^@]+\.[^@]+", email)):
                return False, f"{email} not valid"
            return True, "Email OK"
        except Exception as e:
            return False, str(e)

# ob = Validation()
# status,data = ob.phoneNoValidate("8695795")
# print(status,data)
