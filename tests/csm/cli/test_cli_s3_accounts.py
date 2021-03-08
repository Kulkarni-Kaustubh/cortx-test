#!/usr/bin/python
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
"""Test suite for S3 account operations"""

import logging
import time
import pytest
from commons.ct_fail_on import CTFailOn
from commons.errorcodes import error_handler
from commons.utils import assert_utils
from config import CSM_CFG
from libs.csm.cli.cortx_cli_s3_accounts import CortxCliS3AccountOperations
from libs.csm.cli.cortx_cli_s3_buckets import CortxCliS3BucketOperations
from libs.csm.cli.cli_csm_user import CortxCliCsmUser

S3ACC_OBJ = CortxCliS3AccountOperations()
S3BKT_OBJ = CortxCliS3BucketOperations(session_obj=S3ACC_OBJ.session_obj)
CSM_USER_OBJ = CortxCliCsmUser(session_obj=S3ACC_OBJ.session_obj)
LOGGER = logging.getLogger(__name__)


class TestCliS3ACC:
    """CORTX CLI Test suite for S3 account operations"""

    @classmethod
    def setup_class(cls):
        """
        Setup all the states required for execution of this test suit.
        """
        LOGGER.info("STARTED : Setup operations at test suit level")
        cls.s3acc_prefix = "cli_s3acc"
        cls.s3acc_name = cls.s3acc_prefix
        cls.s3acc_email = "{}@seagate.com"
        cls.s3acc_password = CSM_CFG["CliConfig"]["acc_password"]
        LOGGER.info("ENDED : Setup operations at test suit level")

    def setup_method(self):
        """
        Setup all the states required for execution of each test case in this test suite
        It is performing below operations as pre-requisites
            - Initializes common variables
            - Login to CORTX CLI as admin user
        """
        LOGGER.info("STARTED : Setup operations at test function level")
        self.s3acc_name = "{}_{}".format(self.s3acc_name, int(time.time()))
        self.s3acc_email = self.s3acc_email.format(self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli()
        assert_utils.assert_equals(True, login[0], login[1])
        LOGGER.info("ENDED : Setup operations at test function level")

    def teardown_method(self):
        """
        Teardown any state that was previously setup with a setup_method
        It is performing below operations as pre-requisites
            - Initializes common variables
            - Login to CORTX CLI as admin user
        """
        LOGGER.info("STARTED : Teardown operations at test function level")
        S3ACC_OBJ.logout_cortx_cli()
        login = S3ACC_OBJ.login_cortx_cli()
        assert_utils.assert_equals(True, login[0], login[1])
        accounts = S3ACC_OBJ.show_s3account_cortx_cli(output_format="json")[1]
        accounts = S3ACC_OBJ.format_str_to_dict(
            input_str=accounts)["s3_accounts"]
        accounts = [acc["account_name"]
                    for acc in accounts if self.s3acc_prefix in acc["account_name"]]
        S3ACC_OBJ.logout_cortx_cli()
        for acc in accounts:
            S3ACC_OBJ.login_cortx_cli(
                username=acc, password=self.s3acc_password)
            S3ACC_OBJ.delete_s3account_cortx_cli(account_name=acc)
            S3ACC_OBJ.logout_cortx_cli()

        LOGGER.info("ENDED : Teardown operations at test function level")

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10872")
    @CTFailOn(error_handler)
    def test_1008_delete_s3_account(self):
        """
        Verify that S3 account should be deleted successfully on executing delete command
        """
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(
            account_name=self.s3acc_name)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Deleted s3 account %s", self.s3acc_name)

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10877")
    @CTFailOn(error_handler)
    def test_1012_delete_diff_acc(self):
        """
        Verify that appropriate error msg should be returned when s3 account tries to
        delete different s3 account
        """
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        s3acc_name2 = "cli_s3acc_{}".format(int(time.time()))
        s3acc_email2 = "{}@seagate.com".format(s3acc_name2)
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=s3acc_name2,
            account_email=s3acc_email2,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created another s3 account %s", s3acc_name2)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(account_name=s3acc_name2)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], "Access denied")
        LOGGER.info(
            "Deleting different account failed with error %s", resp[1])

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10869")
    @CTFailOn(error_handler)
    def test_1003_create_acc_invalid_passwd(self):
        """
        Test that appropriate error should be returned when CSM user/admin enters invalid password
        while creating S3 account
        """
        dummy_pwd = "seagate"
        error_msg = "Password Policy Not Met"
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=dummy_pwd)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info(
            "Creating S3 account with invalid password failed with error %s",
            resp[1])

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10870")
    @CTFailOn(error_handler)
    def test_1005_create_duplicate_acc(self):
        """
        Test that appropriate error should be thrown when CSM user/admin tries to
        create duplicate S3 user
        """
        error_msg = "attempted to create an account that already exists"
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info(
            "Creating duplicate S3 account failed with error %s", resp[1])

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10871")
    @CTFailOn(error_handler)
    def test_1007_list_acc_invalid_format(self):
        """
        Verify that error msg is returned when command to list s3 users contains
        incorrect/invalid format
        """
        output_format = "text"
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        error_msg = " invalid choice: '{}'".format(output_format)
        resp = S3ACC_OBJ.show_s3account_cortx_cli(output_format=output_format)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info(
            "Listing S3 accounts with invalid format failed with error %s",
            resp[1])

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10873")
    @CTFailOn(error_handler)
    def test_1009_no_on_deletion(self):
        """
        Verify that s3 account is not deleted when user selects "no" on confirmation
        :avocado: tags=s3_account_user_cli
        """
        delete_s3acc_cmd = "s3accounts delete {}".format(self.s3acc_name)
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info("Logging into CORTX CLI as %s", self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        LOGGER.info("Deleting s3 account %s", self.s3acc_name)
        response = S3ACC_OBJ.execute_cli_commands(cmd=delete_s3acc_cmd)[1]
        if "[Y/n]" in response:
            response = S3ACC_OBJ.execute_cli_commands(cmd="n")
        assert_utils.assert_equals(True, response[0], response[1])
        resp = S3ACC_OBJ.show_s3account_cortx_cli()
        assert_utils.assert_exact_string(resp[1], self.s3acc_name)
        LOGGER.info(
            "Verified that account is not deleted with 'no' on confirmation")

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10874")
    @CTFailOn(error_handler)
    def test_1010_delete_multiple_acc(self):
        """
        verify that appropriate error should be returned when S3 account user try to
        delete different multiple s3 accounts simultaneously
        """
        dummy_acc1 = "cli_s3acc_{}".format(int(time.time()))
        dummy_acc2 = "cli_s3acc_{}".format(int(time.time()))
        error_msg = "Access denied. Verify account name."
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info("Logging into CORTX CLI as %s", self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        LOGGER.info(
            "Performing simultaneous delete operation without mentioning currently \
            logged in s3account")
        acc_names = " ".join([dummy_acc1, dummy_acc2])
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(account_name=acc_names)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info(
            "Performing simultaneous delete operation without mentioning currently logged \
            in s3 account user failed with error %s", resp[1])
        LOGGER.info(
            "Performing simultaneous delete operation with currently logged in s3 account")
        acc_names = " ".join([self.s3acc_name, dummy_acc1])
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(
            account_name=acc_names)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Deleted s3 account %s", self.s3acc_name)

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10875")
    @CTFailOn(error_handler)
    def test_1011_delete_invalid_acc(self):
        """
        Verify that appropriate error msg should be returned when command to delete s3 user contains
        incorrect/invalid account_name
        """
        error_msg = "Access denied. Verify account name."
        dummy_acc = "cli_s3acc_{}".format(int(time.time()))
        error_msg = "Access denied. Verify account name."
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info("Logging into CORTX CLI as %s", self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(account_name=dummy_acc)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info(
            "Performing delete operation with invalid s3 account name is failed with error %s",
            resp[1])

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10881")
    @CTFailOn(error_handler)
    def test_1144_acc_login_with_param(self):
        """
        Test that S3 account is able to login to csmcli passing username as parameter
        """
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info(
            "Logging into CORTX CLI with username as parameter as %s",
            self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password,
            username_param=self.s3acc_name)
        assert_utils.assert_equals(True, login[0], login[1])
        LOGGER.info(
            "Successfully logged into CORTX CLI by passing username as parameter")

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10883")
    @CTFailOn(error_handler)
    def test_1147_s3_acc_login(self):
        """
        Test that s3 account, csm admin and csm user can login to csm interactive session
        without passing username as direct parameter in command
        """
        csm_user_name = "{0}{1}".format("auto_csm_user", str(int(time.time())))
        csm_user_email = "{0}{1}".format(csm_user_name, "@seagate.com")
        csm_user_pwd = CSM_CFG["CliConfig"]["csm_user_pwd"]
        LOGGER.info("Creating csm user with name %s", csm_user_name)
        resp = CSM_USER_OBJ.create_csm_user_cli(
            csm_user_name=csm_user_name,
            email_id=csm_user_email,
            role="manage",
            password=csm_user_pwd,
            confirm_password=csm_user_pwd)
        assert_utils.assert_equals(
            True, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], "User created")
        LOGGER.info("Created csm user with name %s", csm_user_name)
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info("Logging into CORTX CLI as s3 account %s", self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info(
            "Successfully logged in to CORTX CLI as s3 account %s",
            self.s3acc_name)
        LOGGER.info("Logging into CORTX CLI as csm user %s", csm_user_name)
        login = CSM_USER_OBJ.login_cortx_cli(
            username=csm_user_name,
            password=csm_user_pwd)
        assert_utils.assert_equals(True, login[0], login[1])
        LOGGER.info(
            "Successfully logged in to CORTX CLI as csm user %s",
            csm_user_name)

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10885")
    @CTFailOn(error_handler)
    def test_1916_update_acc_passwd(self):
        """
        Test s3 account user can update his password through csmcli
        """
        new_password = CSM_CFG["CliConfig"]["csm_user_pwd"]
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        resp = S3ACC_OBJ.reset_s3account_password(
            account_name=self.s3acc_name, new_password=new_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        LOGGER.info(
            "Logging into CORTX CLI as s3 account %s with new password",
            self.s3acc_name)
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=new_password)
        assert_utils.assert_equals(True, login[0], login[1])
        LOGGER.info(
            "Successfully logged in to CORTX CLI as s3 account %s with new password",
            self.s3acc_name)
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(
            account_name=self.s3acc_name)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Deleted s3 account %s", self.s3acc_name)

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10887")
    @CTFailOn(error_handler)
    def test_4428_delete_acc_with_buckets(self):
        """
        Test that appropriate error should be returned when s3 account user try to delete
        s3 account containing buckets
        """
        bucket_name = "{0}{1}".format("clis3bkt", int(time.time()))
        error_msg = "Account cannot be deleted as it owns some resources"
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created s3 account %s", self.s3acc_name)
        logout = S3ACC_OBJ.logout_cortx_cli()
        assert_utils.assert_equals(True, logout[0], logout[1])
        login = S3ACC_OBJ.login_cortx_cli(
            username=self.s3acc_name,
            password=self.s3acc_password)
        assert_utils.assert_equals(True, login[0], login[1])
        resp = S3BKT_OBJ.create_bucket_cortx_cli(bucket_name)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Created bucket %s", bucket_name)
        resp = S3ACC_OBJ.delete_s3account_cortx_cli(
            account_name=self.s3acc_name)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info("Deleting s3 account failed with error %s", resp[1])
        resp = S3BKT_OBJ.delete_bucket_cortx_cli(bucket_name)
        assert_utils.assert_equals(True, resp[0], resp[1])
        LOGGER.info("Deleted bucket %s", bucket_name)

    @pytest.mark.csm_cli
    @pytest.mark.tags("TEST-10888")
    @CTFailOn(error_handler)
    def test_6219_create_duplicate_acc_name(self):
        """
        Test that duplicate users should not be created between csm users
        and s3 account users in CSM CLI
        """
        error_msg = "CSM user with same username as passed S3 account name already exists"
        resp = CSM_USER_OBJ.create_csm_user_cli(
            csm_user_name=self.s3acc_name,
            email_id=self.s3acc_email,
            role="manage",
            password=self.s3acc_password,
            confirm_password=self.s3acc_password)
        assert_utils.assert_equals(
            True, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], "User created")
        LOGGER.info("Created csm user with name %s", self.s3acc_name)
        resp = S3ACC_OBJ.create_s3account_cortx_cli(
            account_name=self.s3acc_name,
            account_email=self.s3acc_email,
            password=self.s3acc_password)
        assert_utils.assert_equals(False, resp[0], resp[1])
        assert_utils.assert_exact_string(resp[1], error_msg)
        LOGGER.info("Creating s3 account failed with error %s", resp[1])