# LEMPA
### LEan Mean Programming mAchine
LEMPA is a combination of software and hardware to allow easy..ish programming of micro controllers such as Arduino (ATMega), ESP, and others directly from the PI with as little wire mess as possible.


Click image for short video:

[![Click to watch](imgs/yt.png)](https://www.youtube.com/watch?v=8qee_lv31-o)

<!--![Image](https://i.giphy.com/media/S64nu0NFtD7TRhJ7rL/giphy.webp)-->

LEMPA is composed of 3 parts:
#### Hardware: Raspberry PI HAT
A custom PCB that contains all the relevant connections required to program:
* ATMega328 (including external oscillator)
* ATTiny
* ESP8266 
* Arduino mini pro
* Any other ATMega controller via connector

The board also includes:
* LEDs for visual status (ready, downloading, programing, success, and error)
* Jumper to define which profile to use.
* LED for testing 
* Program / download button. Short click to program the MCU, long click to download latest version of the BINs from cloud / local network / shared folder.

![Image](imgs/2D.png)
#### Software
The software reads the different profiles and orchestrates the process of downloading new BINs and programming 
###### Installation instructions
1. Download the software and extract it
2. Install **avrdude** if needed `sudo apt-get install avrdude`
3. Install required libraries `pip3 install -r requirements.tx`
4. Make sure **profiles.json** reflects your environment
5. `python3 program.py` or `python3 program.py <profile id>`

#### Configuration: profiles.json
The configuration file can contain as many profiles as required.
```javascript
  {
    "id": "blinklocal",
    "type": "bin",
    "jumper" : 1,
    "device": "m328p",
    "programmer": "linuxspi",
    "bins": [
      {
        "method": "local",
        "name": "blinklocal"
      }
    ],
    "fuses": {
      "lfuse": "0xF7",
      "hfuse": "0xD6",
      "efuse": "0xFD",
      "lock": "0xFF"
    },
    "plugins": [
      {
        "name": "serialinjector",
        "conf": {
          "serialSpeed": 38400,
          "fields": [
            {
              "id": "blinkrate",
              "value": 5,
              "title": "Blink rate in 100ms. For exampe value of 5 means 500ms off, 500ms on",
              "type": "byte"
            }
          ]
        }
      }
    ]

  },
...
]
```
* **id** Unique ID for the profile 
* **type** `bin` or `composite`. Composite allows for multiple profile programming, one after another.
* **jumper** *optional* If specified, and the relevant profile is chosen with a physical jumper, this profile will be used if none was specified as part of command line parameter.
* **device** Type of device to program. Not required for ESP. See [AVRDude](https://www.nongnu.org/avrdude/user-manual/avrdude.html) for list of devices
* **bins** List of bins to upload. For ATMega only one bin is required. For ESP multiple bins can be specified to support SPIFFS
* **plugins** System support a simple web server with the ability to send data to the ATMega via serial. This allows for parameter tweaking and QA. 

 
![Image Eco system](eco.png)

<a href="https://www.tindie.com/stores/loox/?ref=offsite_badges&utm_source=sellers_rbenamotz&utm_medium=badges&utm_campaign=badge_medium"><img src="https://d2ss6ovg47m0r5.cloudfront.net/badges/tindie-mediums.png" alt="I sell on Tindie" width="150" height="78"></a>

## Contact
Please contact me at roey@benamotz.com with any comments
