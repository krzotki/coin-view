import json
import sys
import pymysql
import rds_config
import requests
import os
import boto3
from botocore.exceptions import ClientError

rds_host = rds_config.db_endpoint
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name
port = 3306
try:
    conn = pymysql.connect(host=rds_host, user=name,
                           passwd=password, db=db_name,
                           connect_timeout=5,
                           cursorclass=pymysql.cursors.DictCursor)
except:
    sys.exit()


api_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.environ["api_key"]
}


def send_email(recipient, text):
    SENDER = "aws.krzotki@gmail.com"
    AWS_REGION = "eu-central-1"
    SUBJECT = "Crypto alert"

    BODY_TEXT = text

    BODY_HTML = """<html>
    <head>
        <style>
            .green {
                color: green;
            }
            .red {
                color: red;
            }
        </style>
    </head>
    <body>
      <h1>Hi %s! Here is the alert for crypto price threshold you have set up.</h1>
      <ul>%s</ul>
    </body>
    </html>
                """ % (recipient["Ua_login"], BODY_TEXT)

    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)

    client.send_email(
        Destination={
            'ToAddresses': [
                recipient["Ua_Email"],
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
    )


def lambda_handler(event, context):
    with conn.cursor() as cur:
        qry = "SELECT * FROM CryptoNotification"
        cur.execute(qry)
        alerts = cur.fetchall()
        print('ALERTS', alerts)
        cryptoids = list(map(lambda x: str(x['Cn_CryptoId']), alerts))
        userids = list(map(lambda x: str(x['Cn_UaId']), alerts))

        qry = "SELECT Ua_Email, Ua_login, Ua_Id  FROM `UsrAccount` where Ua_Id in (%s)" % (
            ",".join(userids))
        cur.execute(qry)
        users = cur.fetchall()
        users = dict(map(lambda user: (user["Ua_Id"], user), users))

        cryptos = requests.get(
            api_url, params={'id': ",".join(cryptoids)}, headers=headers).json()
        cryptos = cryptos["data"]

        alerts_to_send_per_user = {}

        for i in range(0, len(alerts)):
            alert = alerts[i]
            userid = alert["Cn_UaId"]
            cryptoid = alert["Cn_CryptoId"]
            threshold = alert["Cn_Treshold"]

            crypto_change = cryptos[str(
                cryptoid)]["quote"]["USD"]["percent_change_24h"]

            crypto_price = cryptos[str(
                cryptoid)]["quote"]["USD"]["price"]

            crypto_name = cryptos[str(cryptoid)]["name"]

            print(userid, cryptoid, crypto_change, crypto_name)
            if (abs(crypto_change) >= threshold):
                color_class = 'green' if crypto_change > 0 else 'red'
                item = ("%s : <b class='%s'>%f%%</b> - current price: <b>%f$</b>") % (
                    crypto_name, color_class, crypto_change, crypto_price)

                if (userid in alerts_to_send_per_user):
                    alerts_to_send_per_user[userid].append(item)
                else:
                    alerts_to_send_per_user[userid] = [item]

        for key in alerts_to_send_per_user:
            text = '\n'.join(list(map(lambda item: "<li>%s</li>" %
                             (item), alerts_to_send_per_user[key])))
            user = users[key]
            send_email(user, text)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({"status": 'OK'})
    }
