# Weather codes

Both the realtime observations and forecasts contain a code for each entry which can be used to show an icon or descriptive text.

Weather icon sets available for free usage don't usually contain a proper icon for each of these codes. For this reason I decided to draw an extensive set of icons for the application. The icon set is not complete yet but covers most cases.

## SmartSymbol Codes

The table below shows the WeatherSymbol3 codes used by FMI open API when querying weather forecast (eg. stored query `fmi::forecast::harmonie::surface::point::timevaluepair`). The data contains both SmartSymbol and WeatherSymbol3 codes but SmartSymbol delivers more information (with the exception of fog and mist).

| Code (day) | Code (night) | Description (FMI)                                                           | Description (English)                      |
+------------+--------------+-----------------------------------------------------------------------------+--------------------------------------------+
| 1          | 101          | Selkeää                                                                     | Clear                                      |
| 2          | 102          | Enimmäkseen selkeää                                                         | Mostly clear                               |
| 4          | 104          | Puolipilvistä                                                               | Partly cloudy                              |
| 6          | 106          | Enimmäkseen pilvistä                                                        | Mostly cloudy                              |
| 7          |              | Pilvistä                                                                    | Overcast                                   |
| 9          |              | Sumua                                                                       | Fog                                        |
| 71         | 171          | Yksittäisiä ukkoskuuroja                                                    | Isolated thundershowers                    |
| 74         | 174          | Paikoin ukkoskuuroja                                                        | Scattered thundershowers                   |
| 77         |              | Ukkoskuuroja                                                                | Thundershowers                             |
| 21         | 121          | Yksittäisiä sadekuuroja                                                     | Isolated showers                           |
| 24         | 124          | Paikoin sadekuuroja                                                         | Scattered showers                          |
| 27         |              | Sadekuuroja                                                                 | Showers                                    |
| 14         |              | Jäätävää tihkua                                                             | Freezing drizzle                           |
| 17         |              | Jäätävää sadetta                                                            | Freezing rain                              |
| 11         |              | Tihkusadetta                                                                | Drizzle                                    |
| 31         | 131          | Puolipilvistä ja ajoittain heikkoa vesisadetta                              | Partly cloudy and periods of light rain    |
| 34         | 134          | Enimmäkseen pilvistä ja ajoittain heikkoa vesisadetta                       | Mostly cloudy and periods of light rain    |
| 37         |              | Heikkoa vesisadetta                                                         | Light rain                                 |
| 32         | 132          | Puolipilvistä ja ajoittain kohtalaista vesisadetta                          | Partly cloudy and periods of moderate rain |
| 35         | 135          | Enimmäkseen pilvistä ja ajoittain kohtalaista vesisadetta                   | Mostly cloudy and periods of moderate rain |
| 38         |              | Kohtalaista vesisadetta                                                     | Moderate rain                              |
| 33         | 133          | Puolipilvistä ja ajoittain voimakasta vesisadetta                           | Partly cloudy and periods of heavy rain    |
| 36         | 136          | Enimmäkseen pilvistä ja ajoittain voimakasta vesisadetta                    | Mostly cloudy and periods of heavy rain    |
| 39         |              | Voimakasta vesisadetta                                                      | Heavy rain                                 |
| 41         | 141          | Puolipilvistä ja ajoittain heikkoa räntäsadetta tai räntäkuuroja            | Isolated light sleet showers               |
| 44         | 144          | Enimmäkseen pilvistä ja ajoittain heikkoa räntäsadetta tai räntäkuuroja     | Scattered light sleet showers              |
| 47         |              | Heikkoa räntäsadetta                                                        | Light sleet                                |
| 42         | 142          | Puolipilvistä ja ajoittain kohtalaista räntäsadetta tai räntäkuuroja        | Isolated moderate sleet showers            |
| 45         | 145          | Enimmäkseen pilvistä ja ajoittain kohtalaista räntäsadetta tai räntäkuuroja | Scattered moderate sleet showers           |
| 48         |              | Kohtalaista räntäsadetta                                                    | Moderate sleet                             |
| 43         | 143          | Puolipilvistä ja ajoittain voimakasta räntäsadetta tai räntäkuuroja         | Isolated heavy sleet showers               |
| 46         |              | Enimmäkseen pilvistä ja ajoittain voimakasta räntäsadetta tai räntäkuuroja  | Scattered heavy sleet showers              |
| 49         |              | Voimakasta räntäsadetta                                                     | Heavy sleet                                |
| 51         | 151          | Puolipilvistä ja ajoittain heikkoa lumisadetta tai lumikuuroja              | Isolated light snow showers                |
| 54         | 154          | Enimmäkseen pilvistä ja ajoittain heikkoa lumisadetta tai lumikuuroja       | Scattered light snow showers               |
| 57         |              | Heikkoa lumisadetta                                                         | Light snowfall                             |
| 52         | 152          | Puolipilvistä ja ajoittain kohtalaista lumisadetta tai lumikuuroja          | Isolated moderate snow showers             |
| 55         | 155          | Enimmäkseen pilvistä ja ajoittain kohtalaista lumisadetta tai lumikuuroja   | Scattered moderate snow showers            |
| 58         |              | Kohtalaista lumisadetta                                                     | Moderate snowfall                          |
| 53         | 153          | Puolipilvistä ja ajoittain sakeaa lumisadetta tai lumikuuroja               | Isolated heavy snow showers                |
| 56         | 156          | Enimmäkseen pilvistä ja ajoittain sakeaa lumisadetta tai lumikuuroja        | Scattered heavy snow showers               |
| 59         |              | Runsasta lumisadetta                                                        | Heavy snowfall                             |
| 61         | 161          | Yksittäisiä raekuuroja                                                      | Isolated hail showers                      |
| 64         | 164          | Paikoin raekuuroja                                                          | Scattered hail showers                     |
| 67         |              | Raekuuroja                                                                  | Hail showers                               |

## WeatherSymbol3 Codes

The table below shows the WeatherSymbol3 codes used by FMI open API when querying weather forecast (eg. stored query `fmi::forecast::harmonie::surface::point::timevaluepair`).

I have translated the descriptions to English.

| Code | Description (FMI)        | Description (English)  |
+------+--------------------------+------------------------+
| 1    | Selkeää                  | Clear                  |
| 2    | Puolipilvistä            | Partly cloudy          |
| 21   | Heikkoja sadekuuroja     | Light showers          |
| 22   | Sadekuuroja              | Moderate showers       |
| 23   | Voimakkaita sadekuuroja  | Heavy showers          |
| 3    | Pilvistä                 | Cloudy                 |
| 31   | Heikkoa vesisadetta      | Light rain             |
| 32   | Vesisadetta              | Moderate rain          |
| 33   | Voimakasta vesisadetta   | Heavy rain             |
| 41   | Heikkoja lumikuuroja     | Light snow showers     |
| 42   | Lumikuuroja              | Moderate snow showers  |
| 43   | Voimakkaita lumikuuroja  | Heavy snow showers     |
| 51   | Heikkoa lumisadetta      | Light snowfall         |
| 52   | Lumisadetta              | Moderate snowfall      |
| 53   | Voimakasta lumisadetta   | Heavy snowfall         |
| 61   | Ukkoskuuroja             | Thundershowers         |
| 62   | Voimakkaita ukkoskuuroja | Heavy thundershowers   |
| 63   | Ukkosta                  | Thunder                |
| 64   | Voimakasta ukkosta       | Heavy thunder          |
| 71   | Heikkoja räntäkuuroja    | Light sleet showers    |
| 72   | Räntäkuuroja             | Moderate sleet showers |
| 73   | Voimakkaita räntäkuuroja | Heavy sleet showers    |
| 81   | Heikkoa räntäsadetta     | Light sleed            |
| 82   | Räntäsadetta             | Moderate sleet         |
| 83   | Voimakasta räntäsadetta  | Heavy sleet            |
| 91   | Utua                     | Mist                   |
| 92   | Sumua                    | Fog                    |

## WaWa Codes

The table below shows the WaWa codes used by FMI open API when querying real time weather observations from weather stations (eg. stored query `fmi::observations::weather::timevaluepair`). Not all codes are listed by FMI.

| Code    | Description                                                                                 |
+---------+---------------------------------------------------------------------------------------------+
| 00      | No significant weather observed                                                             |
| 01      | Clouds generally dissolving or becoming less developed during the past hour                 |
| 02      | State of sky on the whole unchanged during the past hour                                    |
| 03      | Clouds generally forming or developing during the past hour                                 |
| 04      | Haze or smoke, or dust in suspension in the air, visibility equal to, or greater than, 1 km |
| 05      | Haze or smoke, or dust in suspension in the air, visibility less than 1 km                  |
| 06 - 09 | Reserved                                                                                    |
| 10      | Mist                                                                                        |
| 11      | Diamond dust                                                                                |
| 12      | Distant lightning                                                                           |
| 13 - 17 | Reserved                                                                                    |
| 18      | Squalls                                                                                     |
| 19      | Reserved                                                                                    |
| 20      | Fog                                                                                         |
| 21      | PRECIPITATION                                                                               |
| 22      | Drizzle (not freezing) or snow grains                                                       |
| 23      | Rain (not freezing)                                                                         |
| 24      | Snow                                                                                        |
| 25      | Freezing drizzle or freezing rain                                                           |
| 26      | Thunderstorm (with or without precipitation)                                                |
| 27      | BLOWING OR DRIFTING SNOW OR SAND                                                            |
| 28      | Blowing or drifting snow or sand, visibility equal to, or greater than, 1 km                |
| 29      | Blowing or drifting snow or sand, visibility less than 1 km                                 |
| 30      | FOG                                                                                         |
| 31      | Fog or ice fog in patches                                                                   |
| 32      | Fog or ice fog, has become thinner during the past hour                                     |
| 33      | Fog or ice fog, no appreciable change during the past hour                                  |
| 34      | Fog or ice fog, has begun or become thicker during the past hour                            |
| 35      | Fog, depositing rime                                                                        |
| 36 - 39 | Reserved                                                                                    |
| 40      | PRECIPITATION                                                                               |
| 41      | Precipitation, slight or moderate                                                           |
| 42      | Precipitation, heavy                                                                        |
| 43      | Liquid precipitation, slight or moderate                                                    |
| 44      | Liquid precipitation, heavy                                                                 |
| 45      | Solid precipitation, slight or moderate                                                     |
| 46      | Solid precipitation, heavy                                                                  |
| 47      | Freezing precipitation, slight or moderate                                                  |
| 48      | Freezing precipitation, heavy                                                               |
| 49      | Reserved                                                                                    |
| 50      | DRIZZLE                                                                                     |
| 51      | Drizzle, not freezing, slight                                                               |
| 52      | Drizzle, not freezing, moderate                                                             |
| 53      | Drizzle, not freezing, heavy                                                                |
| 54      | Drizzle, freezing, slight                                                                   |
| 55      | Drizzle, freezing, moderate                                                                 |
| 56      | Drizzle, freezing, heavy                                                                    |
| 57      | Drizzle and rain, slight                                                                    |
| 58      | Drizzle and rain, moderate or heavy                                                         |
| 59      | Reserved                                                                                    |
| 60      | RAIN                                                                                        |
| 61      | Rain, not freezing, slight                                                                  |
| 62      | Rain, not freezing, moderate                                                                |
| 63      | Rain, not freezing, heavy                                                                   |
| 64      | Rain, freezing, slight                                                                      |
| 65      | Rain, freezing, moderate                                                                    |
| 66      | Rain, freezing, heavy                                                                       |
| 67      | Rain (or drizzle) and snow, slight                                                          |
| 68      | Rain (or drizzle) and snow, moderate or heavy                                               |
| 69      | Reserved                                                                                    |
| 70      | SNOW                                                                                        |
| 71      | Snow, slight                                                                                |
| 72      | Snow, moderate                                                                              |
| 73      | Snow, heavy                                                                                 |
| 74      | Ice pellets, slight                                                                         |
| 75      | Ice pellets, moderate                                                                       |
| 76      | Ice pellets, heavy                                                                          |
| 77      | Snow grains                                                                                 |
| 78      | Ice crystals                                                                                |
| 79      | Reserved                                                                                    |
| 80      | SHOWER(S) or INTERMITTENT PRECIPITATION                                                     |
| 81      | Rain shower(s) or intermittent rain, slight                                                 |
| 82      | Rain shower(s) or intermittent rain, moderate                                               |
| 83      | Rain shower(s) or intermittent rain, heavy                                                  |
| 84      | Rain shower(s) or intermittent rain, violent                                                |
| 85      | Snow shower(s) or intermittent snow, slight                                                 |
| 86      | Snow shower(s) or intermittent snow, moderate                                               |
| 87      | Snow shower(s) or intermittent snow, heavy                                                  |
| 88      | Reserved                                                                                    |
| 89      | Hail                                                                                        |
| 90      | THUNDERSTORM                                                                                |
| 91      | Thunderstorm, slight or moderate, with no precipitation                                     |
| 92      | Thunderstorm, slight or moderate, with rain showers and/or snow showers                     |
| 93      | Thunderstorm, slight or moderate, with hail                                                 |
| 94      | Thunderstorm, heavy, with no precipitation                                                  |
| 95      | Thunderstorm, heavy, with rain showers and/or snow showers                                  |
| 96      | Thunderstorm, heavy, with hail                                                              |
| 97 - 98 | Reserved                                                                                    |
| 99      | Tornado                                                                                     |

Note: Code figures 20–26 are used to report precipitation, fog (or ice fog) or thunderstorm at the station during the preceding hour but not at the time of observation.

## Sources

Codes listed and used by FMI: [Latauspalvelun pikaohje](https://www.ilmatieteenlaitos.fi/latauspalvelun-pikaohje)

List of all WaWa codes: [WMO Manual on Codes, International Codes, Volume I.1, Annex II to the WMO Technical Regulations, Part A – Alphanumeric Codes](https://library.wmo.int/doc_num.php?explnum_id=10235)
