# homebridge-switcherV2

#### Homebridge plugin to control Switcher V2 (Python version).

## Installation

1. Install [homebridge](https://github.com/nfarina/homebridge#installation-details).

2. Extract the requiered parameters. Follow instructions below at "Getting the Parameters"

3. Install the Plugin
 ```
sudo npm install -g git+https://github.com/royby12/homebridge-switcherV2.git
 ```

## Configuration Examples

#### Config.json :

 ```json 
{
  "accessory": "SwitcherV2",
  "name": "TestSwitcher",
  "switcherIP": "[SWITCHER IP]",
  "phone_id": "[PHONE ID]",
  "device_id": "[Device ID]",
  "device_pass": "[DEVICE PASSWORD]",
  "pythonPath": "[YOUR PATH TO switcherJSON.py (instructions below)]",
  "icon": 0,
  "DefaultDuration": "3600"
}
 ``` 
 ### Parameter Details:
 
| Key | Description | Default |
| --- | --- | --- |
| `accessory` | Must be `SwitcherV2` | N/A |
| `name` | Name to appear in the Home app | N/A |
| `switcherIP` | IP of the Switcher V2 | N/A |
| `phone_id` | Phone ID that was extracted from the script | N/A |
| `device_id` | Device ID that was extracted from the script | N/A |
| `device_pass` | Device Pass that was extracted from the script | N/A |
| `pythonPath` | Your path to switcherJSON.py | N/A |
| `icon` | (Optional) Can be '0','1' or '2' | 0 |
| `DefaultDuration` | Set the Default Run Time | 3600 |


## Getting the Parameters:

* To get the switcherIP, phone_id, device_id and device_pass you will need to follow @NightRang3r instructions at:
https://github.com/NightRang3r/Switcher-V2-Python
You'll need to use his library first (one wat or another) to extract these parameters.

* To get your Python Path, you'll need to figure where the Node Modules lib is located.
Execute the following command to get the path:
```
echo $(npm -g ls --depth=0| head -n1)/node_modules/homebridge-switcherV2/switcherJSON.py
```


## Credits:

@NightRang3r - the switcherJSON.py script in this repository is based on his. I have modified his library to fit this plugin. I could not make it work without it!!
