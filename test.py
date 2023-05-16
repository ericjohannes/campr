from campr_app.campr import nearest_friday, generate_dates, check_availability, post_types, send_email, check_availability, check_name, get_secret, place_ids

available_sites = []

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