from flask import Flask
import breeze_core

app = Flask('SteadyBreezeAPI')

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

@app.route("/get_cheapest_pricezone")
def get_cheapest_pricezone():
    return "no1"