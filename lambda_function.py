"""RDS bootstrap"""
import os
import logging
import boto3

LOGGER = logging.getLogger()
APPROVAL_DB_NAME = os.getenv('APPROVAL_DB_NAME')
INTERACTION_DB_NAME = os.getenv('INTERACTION_DB_NAME')
APPROVAL_DB_SCHEMA_NAME = os.getenv('APPROVAL_DB_SCHEMA_NAME')
INTERACTION_DB_SCHEMA_NAME = os.getenv('INTERACTION_DB_SCHEMA_NAME')
DB_CLUSTER_ARN = os.getenv('APPROVAL_DB_CLUSTER_ARN')
DB_CREDENTIALS_SECRETS_STORE_ARN = os.getenv('CREDENTIALS_SECRET')
RDS_CLIENT = boto3.client('rds-data')


def execute_statement_no_db(sql, schema_name):
    """ Executes SQL Statement w/o DB """
    return RDS_CLIENT.execute_statement(
        secretArn=DB_CREDENTIALS_SECRETS_STORE_ARN,
        resourceArn=DB_CLUSTER_ARN,
        sql=sql,
        schema=schema_name
    )


def execute_statement(sql, schema_name, db_name):
    """ Executes SQL Statement """
    return RDS_CLIENT.execute_statement(
        secretArn=DB_CREDENTIALS_SECRETS_STORE_ARN,
        database=db_name,
        resourceArn=DB_CLUSTER_ARN,
        sql=sql,
        schema=schema_name
    )


def lambda_handler(*_):
    """Default Handler"""
    LOGGER.info('Got create')
    flag_table_name = os.getenv('FLAG_TABLE')
    unclogger_prompt_table_name = os.getenv('UNCLOGGER_PROMPT_TABLE')
    user_interaction_table_name = os.getenv('USER_INTERACTION_TABLE')
    content_interaction_table_name = os.getenv('CONTENT_INTERACTION_TABLE')
    comment_table_name = os.getenv('COMMENT_TABLE')

    # create MySQL databases
    execute_statement_no_db(
        f'CREATE DATABASE IF NOT EXISTS {APPROVAL_DB_NAME}', APPROVAL_DB_SCHEMA_NAME)
    execute_statement_no_db(
        f'CREATE DATABASE IF NOT EXISTS {INTERACTION_DB_NAME}', INTERACTION_DB_SCHEMA_NAME)

    # Create Flag table
    execute_statement((
        f'CREATE TABLE IF NOT EXISTS {flag_table_name} ('
        'id varchar(200) NOT NULL,'
        'contentType varchar(32) NOT NULL,'
        'contentId varchar(128) NOT NULL,'
        'flaggerUserId varchar(128) NOT NULL,'
        'category varchar(128) NOT NULL,'
        'type varchar(128) NOT NULL,'
        'detail varchar(255) NOT NULL,'
        'status varchar(16),'
        'reviewerUserId varchar(128),'
        'reviewNote varchar(255),'
        'createTime varchar(32) NOT NULL,'
        'lastUpdateTime varchar(32),'
        'reviewTime varchar(32),'
        'PRIMARY KEY (id),'
        'UNIQUE KEY contentIdFlaggerUserIdUQ (contentId,flaggerUserId)'
        ')'
    ), APPROVAL_DB_SCHEMA_NAME, APPROVAL_DB_NAME)

    # Create Unclogger Prompt table
    execute_statement((
        f'CREATE TABLE IF NOT EXISTS {unclogger_prompt_table_name} ('
        'id varchar(200) NOT NULL,'
        'category varchar(128) NOT NULL,'
        'body varchar(255) NOT NULL,'
        'language varchar(8) NOT NULL,'
        'status varchar(16),'
        'creatorUserId varchar(128) NOT NULL,'
        'reviewerUserId varchar(128),'
        'reviewNote varchar(255),'
        'createTime varchar(32) NOT NULL,'
        'lastUpdateTime varchar(32),'
        'reviewTime varchar(32),'
        'PRIMARY KEY (id),'
        'UNIQUE KEY categoryBodyLanguageUQ (category,body,language)'
        ')'
    ), APPROVAL_DB_SCHEMA_NAME, APPROVAL_DB_NAME)
