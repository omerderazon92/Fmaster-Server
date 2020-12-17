import pymysql
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# rds settings
rds_host = 'fart-master.cme8hfquunrm.us-east-1.rds.amazonaws.com'
name = 'admin'
password = '01Aq9w01aq9w'
db_name = 'farts_master'

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
