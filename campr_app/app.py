import json
from campr import nearest_friday, generate_dates, check_availability, post_types, send_email, check_availability, check_name, get_secret, place_ids

available_sites = []


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    start_date = nearest_friday()
    end_date = "09-15-2023"
    dates = generate_dates(start_date, end_date)
    for d in dates:
        for p in place_ids:
            data = post_types(p['id'], d)
            if check_availability(data):
                name = check_name(data)
                available_sites.append({
                    "name": name,
                    "date": d
                })

    sendgrid_api_key = get_secret()
    print('len', len(sendgrid_api_key))
    print('char', sendgrid_api_key[-1])
    send_email(available_sites, start_date, end_date, place_ids, sendgrid_api_key)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": available_sites,
            # "location": ip.text.replace("\n", "")
        }),
    }
