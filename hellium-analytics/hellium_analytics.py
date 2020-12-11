#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sample script.

This is a template for a top-level/entry point script.

Example:

    Call this module as a script from the command line:
    $ python script.py
"""

import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime


API = "https://api.helium.io/v1/hotspots"


def get_hotspots(max_cursor_cnt=50):
    """
    Make requests to helium.io API to grab pages of hotspot data up to max_cursor_cnt

    arg:
        max_cursor_cnt (int): Max number of pages to request (default: 100)

    return:
        hotspots (pd.DataFrame): dataframe of all hotspots listed at helium.io
    """
    responses = list()
    resp = requests.get(API).json()
    responses.append(resp["data"])
    cursor = resp["cursor"]
    cursor_cnt = 1
    while True:
        response = requests.get(API, params={"cursor": cursor})
        if response.ok:
            resp = response.json()
            if "cursor" not in resp or cursor_cnt >= max_cursor_cnt:
                break
            cursor = resp["cursor"]
            responses.append(resp["data"])
            cursor_cnt += 1
        else:
            break
    hotspots = list()
    for page in responses:
        for hotspot in page:
            hotspots.append(hotspot)
    return pd.json_normalize(hotspots)


def get_hotspots_by_loc(df_hotspots, region="US"):
    """
    get region based hotspots organized by state and city

    Args:
        df_hotspots (pd.DataFrame): DataFrame of hotspots from get_hotspots()
        region (string): the short_country geocode listed in df_hotspots to filet on

    Return:
        get_hotspots_by_loc (dict(pd.DataFrame)): dictionary of region and state dataframes
    """
    # For now only grab ones in the US
    df_us_hotspots = df_hotspots[df_hotspots["geocode.short_country"] == region]
    # Grab states
    states_list = list(set(df_us_hotspots["geocode.long_state"].to_list()))
    # Build data tree for each state
    get_hotspots_by_loc = dict()
    for state in states_list:
        state_df = df_us_hotspots[df_us_hotspots["geocode.long_state"] == state]
        get_hotspots_by_loc[f"{state}"] = dict()
        get_hotspots_by_loc[f"{state}"]["state_data"] = state_df
        cities_list = list(
            set(
                df_us_hotspots[df_us_hotspots["geocode.long_state"] == state][
                    "geocode.long_city"
                ].to_list()
            )
        )
        for city in cities_list:
            get_hotspots_by_loc[f"{state}"][f"{city}"] = get_hotspots_by_loc[
                f"{state}"
            ]["state_data"][
                get_hotspots_by_loc[f"{state}"]["state_data"]["geocode.long_city"]
                == city
            ]
    return get_hotspots_by_loc


def get_hnt_per_location(hotspots_by_loc):
    """
    Takes in region hotspot dictionary and produces total mined HNT from the date a hotspot was
    a dataframe for every city that has hotspots
    """
    today = datetime.now()
    max_time = today.isoformat()
    hnt_per_location_list = list()
    for state in hotspots_by_loc.keys():
        for city in hotspots_by_loc[f"{state}"].keys():
            if city == "state_data":
                continue
            df = hotspots_by_loc[f"{state}"][f"{city}"]
            address_list = df.address.to_list()
            min_time = df.timestamp_added.min()
            total_hnt = 0
            avg_hnt_per_hotspot = list()
            max_hnt_per_hotspot = list()
            min_hnt_per_hotspot = list()
            std_hnt_per_hotspot = list()
            print(f"Processing {state}, {city} with {len(address_list)} Hotspots")
            for address in address_list:
                response = requests.get(
                    f"{API}/{address}/rewards/stats",
                    params={
                        "max_time": max_time,
                        "min_time": min_time,
                        "bucket": "hour",
                    },
                )
                if response.ok:
                    resp = response.json()
                    rewards = pd.DataFrame.from_dict(resp["data"])
                    total_hnt += rewards.total.sum()
                    max_hnt_per_hotspot.append(rewards.total.max())
                    min_hnt_per_hotspot.append(rewards.total.min())
                    std_hnt_per_hotspot.append(rewards.total.std())
                    avg_hnt_per_hotspot.append(rewards.total.mean())

            hnt_per_location_list.append(
                {
                    "state": state,
                    "city": city,
                    "num_hotspots": len(address_list),
                    "total_hnt": total_hnt,
                    "avg_hnt": np.mean(avg_hnt_per_hotspot),
                    "avg_max_hnt": np.mean(max_hnt_per_hotspot),
                    "avg_min_hnt": np.mean(min_hnt_per_hotspot),
                    "avg_std_hnt": np.mean(std_hnt_per_hotspot),
                    "max_of_max": np.max(max_hnt_per_hotspot),
                    "min_of_min": np.min(min_hnt_per_hotspot),
                    "from": min_time,
                    "to": max_time,
                }
            )
    return hnt_per_location_list


def get_hnt_stats_per_location(
    state_filter=None, city_filter=None, max_time=datetime.now(), bucket="day"
):
    """
    Grab HNT stats for a location

    Args:
        state_filter (string):
        city_filter (string):
        max_time (datetime):
        bucket (string): Day, hour, Week, Month
    """
    if not state_filter and not city_filter:
        return {
            "state": "N/A",
            "city": "N/A",
            "num_hotspots": 0,
            "total_hnt": 0,
            "avg_hnt": 0,
            "avg_max_hnt": 0,
            "avg_min_hnt": 0,
            "avg_std_hnt": 0,
            "max_of_max": 0,
            "min_of_min": 0,
            "from": "",
            "to": "",
        }
    hotspots_by_loc = get_hotspots_by_loc(get_hotspots(max_cursor_cnt=50))
    if state_filter:
        df = hotspots_by_loc[f"{state_filter}"]["state_data"]
        city_filter = None
    if city_filter:
        for state in hotspots_by_loc.keys():
            for city in hotspots_by_loc[f"{state}"].keys():
                if city.lower() == city_filter.lower():
                    print(f"City, {city_filter} found")
                    df = hotspots_by_loc[f"{state}"][f"{city}"]
                    break
            if city.lower() == city_filter.lower():
                break
    address_list = df.address.to_list()
    print(f"----- Processing {len(address_list)} hotspots")
    min_time = df.timestamp_added.min()
    total_hnt = 0
    avg_hnt_per_hotspot = list()
    max_hnt_per_hotspot = list()
    min_hnt_per_hotspot = list()
    std_hnt_per_hotspot = list()
    for address in address_list:
        response = requests.get(
            f"{API}/{address}/rewards/stats",
            params={
                "max_time": max_time.isoformat(),
                "min_time": min_time,
                "bucket": bucket.lower(),
            },
        )
        if response.ok:
            resp = response.json()
            rewards = pd.DataFrame.from_dict(resp["data"])
            total_hnt += rewards.total.sum()
            max_hnt_per_hotspot.append(rewards.total.max())
            min_hnt_per_hotspot.append(rewards.total.min())
            std_hnt_per_hotspot.append(rewards.total.std())
            avg_hnt_per_hotspot.append(rewards.total.mean())
    data = {
        "state": state,
        "bucket": bucket.lower(),
        "city": city if city_filter else "N/A",
        "num_hotspots": len(address_list),
        "total_hnt": total_hnt,
        "avg_hnt": np.mean(avg_hnt_per_hotspot),
        "avg_max_hnt": np.mean(max_hnt_per_hotspot),
        "avg_min_hnt": np.mean(min_hnt_per_hotspot),
        "avg_std_hnt": np.mean(std_hnt_per_hotspot),
        "max_of_max": np.max(max_hnt_per_hotspot),
        "min_of_min": np.min(min_hnt_per_hotspot),
        "from": min_time,
        "to": max_time.isoformat(),
    }
    return data


def get_hotspot_stats(
    address, max_time=datetime.now().strftime("%D"), min_time="12/01/16", bucket="day"
):
    """
    Get stats for a single hotspot based on bucket size

    Args:
        address (string): address of hotspot
        max_time (string): query up to this date of format mm/dd/yy (default: datetime.now().strftime("%D"))
        min_time (string): start query at this date for format mm/dd/yy (defualt: 12/01/16)
        bucket (string): Sample size ("hour", "day", "month", "year")

    Return:
        data (dict): dictionary of hotspot stats
    """
    min_time = datetime.strptime(min_time, "%m/%d/%y").isoformat()
    max_time = datetime.strptime(max_time, "%m/%d/%y").isoformat()
    response = requests.get(
        f"{API}/{address}/rewards/stats",
        params={
            "max_time": max_time,
            "min_time": min_time,
            "bucket": bucket.lower(),
        },
    )
    total_hnt = 0
    avg_hnt_per_hotspot = list()
    max_hnt_per_hotspot = list()
    min_hnt_per_hotspot = list()
    std_hnt_per_hotspot = list()
    if response.ok:
        resp = response.json()
        rewards = pd.DataFrame.from_dict(resp["data"])
        total_hnt += rewards.total.sum()
        max_hnt_per_hotspot.append(rewards.total.max())
        min_hnt_per_hotspot.append(rewards.total.min())
        std_hnt_per_hotspot.append(rewards.total.std())
        avg_hnt_per_hotspot.append(rewards.total.mean())
        data = {
            "address": address,
            "bucker": bucket.lower(),
            "total_hnt": total_hnt,
            "avg_hnt": np.mean(avg_hnt_per_hotspot),
            "avg_max_hnt": np.mean(max_hnt_per_hotspot),
            "avg_min_hnt": np.mean(min_hnt_per_hotspot),
            "avg_std_hnt": np.mean(std_hnt_per_hotspot),
            "max_of_max": np.max(max_hnt_per_hotspot),
            "min_of_min": np.min(min_hnt_per_hotspot),
            "from": resp["meta"]["min_time"],
            "to": max_time,
        }
    gecko_resp = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "helium", "vs_currencies": "usd"},
    )
    if gecko_resp.ok:
        resp = gecko_resp.json()
        current_usd_price = resp["helium"]["usd"]
        data["hnt_usd_price"] = current_usd_price
        data["total_usd"] = current_usd_price * data["total_hnt"]
    else:
        return None
    return data


def write_to_json(data, outfile="data.json"):
    data_obj = {"data": data}
    with open(outfile, "w") as outfile:
        json.dump(data_obj, outfile)
