# Hellium Analytics

This is a set of python helper functions for generating helium statistics based on regions and individual hotspots.

## Setup

*Have not tested on windows*

1. Install [conda](https://docs.anaconda.com/anaconda/install/mac-os/#macos-graphical-install) python virtual environment manager
2. Open up `Terminal`, `iterm`, or whatever you use then type the following
3. `git clone https://github.com/grahambryan/helium-analytics.git`
4. `cd helium-analytics`
5. `conda env create -f environment.yml`
6. `conda activate env_hnt`
7. `ipython`
8. `import hellium_analytics as ha`

## Example

### get_hotspot_stats

```python
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
```

*The current hnt price is pulled directly from the coin gecko API*

```python
In [2]: ha.get_hotspot_stats("11zSUKzNbtTaG4LebcNL71VPb4PxgQVwCtRgkepbE94341bPLzG", max_time="12/01/20", min_time="11/01/20")
Out[2]:
{'address': '11zSUKzNbtTaG4LebcNL71VPb4PxgQVwCtRgkepbE94341bPLzG',
 'bucker': 'day',
 'total_hnt': 770.5057999599999,
 'avg_hnt': 25.68352666533333,
 'avg_max_hnt': 45.07513248,
 'avg_min_hnt': 3.44686095,
 'avg_std_hnt': 9.018622928616315,
 'max_of_max': 45.07513248,
 'min_of_min': 3.44686095,
 'from': '2020-11-01T00:00:00Z',
 'to': '2020-12-01T00:00:00',
 'hnt_usd_price': 1.17,
 'total_usd': 901.4917859531998}
 ```

### get_hotpost

```python
In [3]: df_hotspots = ha.get_hotspots()

In [4]: df_hotspots.info
Out[4]:
<bound method DataFrame.info of                    timestamp_added                                              owner  nonce                    name         location  ...  geocode.long_country  geocode.long_city                                 geocode.city_id         lng        lat
0      2020-12-11T20:14:23.000000Z  13NTNgUtMJm8Qht2WJVx2yNFqNoBsUARKBgh4VLCyz1ame...      0       exotic-red-baboon             None  ...                  None               None                                            None         NaN        NaN
1      2020-12-11T19:52:03.000000Z  13NTNgUtMJm8Qht2WJVx2yNFqNoBsUARKBgh4VLCyz1ame...      1        fit-carob-spider  8c196b85cd431ff  ...           Netherlands           Den Haag      ZGVuIGhhYWd6dWlkLWhvbGxhbmRuZXRoZXJsYW5kcw    4.270548  52.091945
2      2020-12-11T19:39:25.000000Z  13NTNgUtMJm8Qht2WJVx2yNFqNoBsUARKBgh4VLCyz1ame...      1   nice-umber-tardigrade  8c196b8427227ff  ...           Netherlands           Den Haag      ZGVuIGhhYWd6dWlkLWhvbGxhbmRuZXRoZXJsYW5kcw    4.276760  52.101151
3      2020-12-11T19:30:11.000000Z  13NTNgUtMJm8Qht2WJVx2yNFqNoBsUARKBgh4VLCyz1ame...      1  breezy-parchment-gecko  8c196bb8a974bff  ...           Netherlands          Maassluis     bWFhc3NsdWlzenVpZC1ob2xsYW5kbmV0aGVybGFuZHM    4.232060  51.930748
4      2020-12-11T19:21:38.000000Z  13NTNgUtMJm8Qht2WJVx2yNFqNoBsUARKBgh4VLCyz1ame...      1       lone-velvet-gecko  8c195180c2c53ff  ...        United Kingdom      Bamber Bridge  YmFtYmVyIGJyaWRnZWVuZ2xhbmR1bml0ZWQga2luZ2RvbQ   -2.656217  53.736434
...                            ...                                                ...    ...                     ...              ...  ...                   ...                ...                                             ...         ...        ...
12995  2019-11-01T03:51:25.000000Z  132CWNPXPtY5eRnAE6G7NW2GrnkStgUmYrwvNrX7RmrX3M...      4   silly-velvet-mandrill  8c44a100839d5ff  ...         United States              Miami              bWlhbWlmbG9yaWRhdW5pdGVkIHN0YXRlcw  -80.125260  25.959672
12996  2019-11-01T03:46:12.000000Z  13bUUxLLDj9cPQ7cKUdqkioY1hSb9ecsWtT9aSya1E8vUs...      4      able-chili-mammoth  8c29a1d086819ff  ...         United States           Alhambra      YWxoYW1icmFjYWxpZm9ybmlhdW5pdGVkIHN0YXRlcw -118.141511  34.080566
12997  2019-11-01T03:40:42.000000Z  13bUUxLLDj9cPQ7cKUdqkioY1hSb9ecsWtT9aSya1E8vUs...      6      sticky-foggy-perch  8c29a0a0578c1ff  ...         United States            Anaheim        YW5haGVpbWNhbGlmb3JuaWF1bml0ZWQgc3RhdGVz -117.774319  33.868570
12998  2019-11-01T02:37:48.000000Z  13mNwP5ecb3gCHWocZFXX8CJDp6XA2Q5vc4LYMrMbb8kVn...      7  clever-juniper-caribou  8c29868c62cc7ff  ...         United States          Henderson          aGVuZGVyc29ubmV2YWRhdW5pdGVkIHN0YXRlcw -114.981678  36.035109
12999  2019-11-01T02:14:40.000000Z  14JzKJVerNbhwsGX3Rh3zywWh5ECeGKXMUsF7H8xAAkwok...      1      wild-black-pelican  8c2a107054261ff  ...         United States        Jersey City  amVyc2V5IGNpdHluZXcgamVyc2V5dW5pdGVkIHN0YXRlcw  -74.071538  40.724913

[13000 rows x 22 columns]>
```

### get_hotspot_by_loc

```python
    """
    get region based hotspots organized by state and city

    Args:
        df_hotspots (pd.DataFrame): DataFrame of hotspots from get_hotspots()
        region (string): the short_country geocode listed in df_hotspots to filet on

    Return:
        get_hotspots_by_loc (dict(pd.DataFrame)): dictionary of region and state dataframes
    """
```

 ### get_hnt_stats_per_location

```python
    """
    Grab HNT stats for a location

    Args:
        state_filter (string):
        city_filter (string):
        max_time (datetime):
        bucket (string): Day, hour, Week, Month
    """
```
