from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime as dt
import breeze_core
import redis
import json

app = Flask('SteadyBreezeAPI')
r = redis.StrictRedis(host='host.docker.internal', port=6379, db=0)


def update_elec_data():
    """
    Function for updating the data in Redis.
    """
    print("Scheduler is alive!")

    # First process SPOT data
    spot_prices_fi = breeze_core.get_entsoe_day_ahead_prices(country_code='FI')
    spot_prices_de = breeze_core.get_entsoe_day_ahead_prices(country_code='DE_LU')
    spot_prices_dk = breeze_core.get_entsoe_day_ahead_prices(country_code='DK_1')

    # Current SPOT prices
    spot_price_fi1 = spot_prices_fi[dt.now().hour - 2]
    spot_price_de1 = spot_prices_de[dt.now().hour - 2]

    total_fi1_cap = 40 #MW
    total_de1_cap = 40 #MW

    power_list = breeze_core.mean_power_forecast(["Tahkoluoto", "Kalajoki"  ,"Kemi", "Teuva"])
    # We scale the output powers to be in MWh, the size of the PPA varies in 10-20 MW 
    power_list = power_list / 100
    next_hour_ppa_fi1 = power_list[0]
    
    # Hard-coded price for the PPA electricity
    ppa_price = 40 # EUR/MWh

    # TODO: Get DC power consumption estimate here
    fi1_current_consumption = total_fi1_cap * 0.6
    de1_current_consumption = total_de1_cap * 0.5

    spot_consumption_fi1 = fi1_current_consumption - next_hour_ppa_fi1
    
    fi1_total_price = ppa_price * next_hour_ppa_fi1 + spot_price_fi1 * spot_consumption_fi1
    de1_total_price = spot_price_de1 * de1_current_consumption
    print(f"""FI STATS: used capacity: {fi1_current_consumption}/{total_fi1_cap} MWh.
        Elec from PPA: {next_hour_ppa_fi1} MWh.
        Elec from SPOT: {spot_consumption_fi1} MWh.
        Elec price: {fi1_total_price} EUR.""")
    print(f"""DE STATS: used capacity: {de1_current_consumption}/{total_de1_cap} MWh.
        Elec from PPA: 0 MWh.
        Elec from SPOT: {de1_current_consumption} MWh.
        Elec price: {de1_total_price} EUR.""")

    fi1_price = ppa_price if fi1_current_consumption - next_hour_ppa_fi1 > 0 else spot_price_fi1
    de1_price = spot_price_de1
    
    # Save the data to redis as json:
    data = {}
    data['fi'] = {"total_price": fi1_total_price, "total_consumption": fi1_current_consumption}
    data['de'] = {"total_price": de1_total_price, "total_consumption": de1_current_consumption}
    json_data = json.dumps(data)
    r.execute_command('JSON.SET', 'data', '.', json_data)
    print("Data saved to redis.")
    r.execute_command('JSON.SET', 'spot_prices_fi', '.', spot_prices_fi.to_json(date_format='iso'))
    r.execute_command('JSON.SET', 'spot_prices_de', '.', spot_prices_de.to_json(date_format='iso'))
    print("SPOT price data saved to redis.")
    print(spot_price_fi[0])

sched = BackgroundScheduler(daemon=True)
sched.add_job(update_elec_data,'interval',minutes=1)
sched.start()

@app.route("/")
def get_ppa_price():
    """
    Simulates a PPA contract by mixing four locations in Finland and scaling the forecasted
    production to a reasonable level.

    Returns
    -------
    float 
        name of the cheapest pricezone
    """
    total_fi1_cap = 40 #MW
    total_de1_cap = 40 #MW

    power_list = breeze_core.mean_power_forecast(["Tahkoluoto", "Kalajoki"  ,"Kemi", "Teuva"])
    # We scale the output powers to be in MWh, the size of the PPA varies in 10-20 MW 
    power_list = power_list / 100
    next_hour_ppa_fi1 = power_list[0]
    
    # Hard-coded price for the PPA electricity
    ppa_price = 40 # EUR/MWh

    # TODO: Get DC power consumption estimate here
    fi1_current_consumption = total_fi1_cap * 0.6
    de1_current_consumption = total_de1_cap * 0.5

    # TODO: Get the rest of the electricity from NordPool
    spot_price_fi1 = 261.49 # EUR/MWh, this is the mean value for aug 2022
    spot_price_de1 = 200.49 # EUR/MWh, this is an imaginary value

    spot_consumption_fi1 = fi1_current_consumption - next_hour_ppa_fi1
    
    fi1_total_price = ppa_price * next_hour_ppa_fi1 + spot_price_fi1 * spot_consumption_fi1
    de1_total_price = spot_price_de1 * de1_current_consumption
    print(f"""FI STATS: used capacity: {fi1_current_consumption}/{total_fi1_cap} MWh.
        Elec from PPA: {next_hour_ppa_fi1} MWh.
        Elec from SPOT: {spot_consumption_fi1} MWh.
        Elec price: {fi1_total_price} EUR.""")
    print(f"""DE STATS: used capacity: {de1_current_consumption}/{total_de1_cap} MWh.
        Elec from PPA: 0 MWh.
        Elec from SPOT: {de1_current_consumption} MWh.
        Elec price: {de1_total_price} EUR.""")

    fi1_price = ppa_price if fi1_current_consumption - next_hour_ppa_fi1 > 0 else spot_price_fi1
    de1_price = spot_price_de1
    if fi1_price < de1_price:
        return "fi1"
    else:
        return "de1"

@app.route("/redis_backdoor")
def redis_backdoor():
    data = r.execute_command('JSON.GET', 'data')
    json_data = json.loads(data)
    print(f"scheduler is running: {sched.running}")
    print(f"scheduler state: {sched.state}")
    return json_data