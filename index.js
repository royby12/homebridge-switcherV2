var Service, Characteristic;
const {spawn} = require('child_process')


module.exports = function(homebridge) {
    Service = homebridge.hap.Service;
    Characteristic = homebridge.hap.Characteristic;
    homebridge.registerAccessory("homebridge-switcherV2", "SwitcherV2", SwitcherV2);
};

function SwitcherV2(log, config) {
	this.log = log;

	// Get config info
	this.name                 = config["name"]          	|| "HTTP Switcher";
	this.switcherIP           = config["switcherIP"];
  this.phone_id             = config["phone_id"];
  this.device_id            = config["device_id"];
  this.device_pass          = config["device_pass"];
  this.pythonPath           = config["pythonPath"];
  this.icon			           	= config["icon"]			      || 3;
	this.durationInSeconds	  = config["DefaultDuration"]	|| 60*60; //1 Hour

	//Dynamic Variables
	this.remainingHMS;   				//HH:MM:SS
	this.remaining 			= 0;
	this.powerOn 			= 0;
	this.JSONPyResponse; 				//Store the last response as cache
}

SwitcherV2.prototype = {

  pyScript: function (method, callback){
    var callbackMethod = callback;
    var jsonPyResponse = "";
    var pyResponse = spawn('python', ["-u", this.pythonPath, method, this.switcherIP, this.phone_id, this.device_id, this.device_pass]);
    pyResponse.stdout.on('data', (data) => {
      jsonPyResponse += data;
      //this.log(`data:${data}`);
    });
    pyResponse.stderr.on('data', (data) => {
       this.log(`error:${data}`);
    });
    pyResponse.stderr.on('close', () => {
      callback(jsonPyResponse);
      //this.log("Closed");
    });
  },

	getPowerState: function (callback) {
      this.valveService.getCharacteristic(Characteristic.Active).updateValue(this.powerOn);
      //this.valveService.getCharacteristic(Characteristic.InUse).updateValue(this.powerOn);
      callback()
  },

	setPowerState: function (powerOn, callback) {
		this.powerOn = powerOn;
		if (this.powerOn){
      this.pyScript("t"+this.durationInSeconds/60, function(response) {
        try {
          this.JSONPyResponse = JSON.parse(response);
          this.log("HIT");
        }
        catch(err) {
          this.log("CACHE");
        }
        this.remainingHMS = this.JSONPyResponse.time_left;
        var a = this.remainingHMS.split(':');
        this.remaining = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]); //In seconds

        this.log("Remaining time is: " + this.remainingHMS);
        this.valveService.getCharacteristic(Characteristic.RemainingDuration).updateValue(this.remaining);
      }.bind(this))
			this.log("Setting power state to ON");
		}
		else {
      ///
      this.pyScript("0", function(response) {
        try {
          this.JSONPyResponse = JSON.parse(response);
          this.log("HIT");
        }
        catch(err) {
          this.log("CACHE");
        }
        this.valveService.getCharacteristic(Characteristic.RemainingDuration).updateValue(this.remaining);
      }.bind(this))
			this.log("Setting power state to OFF");
		}

		this.valveService.getCharacteristic(Characteristic.InUse).updateValue(this.powerOn);
		this.valveService.getCharacteristic(Characteristic.Active).updateValue(this.powerOn);
		callback();
	},

	getDurationTime: function(callback){
		this.valveService.getCharacteristic(Characteristic.SetDuration).updateValue(this.durationInSeconds);
		callback();
	},

	setDurationTime: function(data, callback){
		this.log("Time set to: " , data.newValue/60 , "minutes");
		this.durationInSeconds = data.newValue;
	},

	getRemainingTime: function(callback){
    this.pyScript("2", function(response) {
      try {
        this.JSONPyResponse = JSON.parse(response);
        this.log("HIT");
      }
      catch(err) {
        this.log("CACHE");
        return;
      }
      this.remainingHMS = this.JSONPyResponse.time_left;
      var a = this.remainingHMS.split(':');
      this.remaining = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]); //In seconds

      this.log("Remaining time is: " + this.remainingHMS);
      if (this.JSONPyResponse.state == "ON") {
        this.powerOn = 1;
        this.log("Power is ON");
      }
      else {
        this.powerOn = 0;
        this.log("Power is OFF")
      }
      this.valveService.getCharacteristic(Characteristic.RemainingDuration).updateValue(this.remaining);
      callback()
    }.bind(this))
	},

	ChangedInUse: function(data, callback){
		this.powerOn = data.newValue;
    this.valveService.getCharacteristic(Characteristic.InUse).updateValue(this.powerOn);
    //this.valveService.setCharacteristic(Characteristic.InUse, this.powerOn);

		switch(this.powerOn)
		{
			case 0: {
				clearTimeout(this.valveService.timer); // clear the timer if it was used
				this.valveService.getCharacteristic(Characteristic.RemainingDuration).updateValue(0);
				this.log("Time out is cleared");
				break;
			}
			case 1: {
				this.valveService.getCharacteristic(Characteristic.RemainingDuration).updateValue(this.durationInSeconds);
				this.valveService.timer = setTimeout( ()=>
				{
				this.log("Timeout ended counting");
				this.valveService.getCharacteristic(Characteristic.InUse).updateValue(0);
				this.valveService.getCharacteristic(Characteristic.Active).updateValue(0);
				}, (this.durationInSeconds*1000));
				break;
			}
		}


	},

	getServices: function (){
		var that = this;

		var informationService = new Service.AccessoryInformation();

		informationService
			.setCharacteristic(Characteristic.Manufacturer, "Sprinkler")
			.setCharacteristic(Characteristic.Model, "Sprinkler Model")
			.setCharacteristic(Characteristic.SerialNumber, "Sprinkler");

		this.valveService = new Service.Valve(this.name);

		this.valveService.getCharacteristic(Characteristic.ValveType).updateValue(this.icon);// Set The ICON

		this.valveService.getCharacteristic(Characteristic.Active)
			.on('set', this.setPowerState.bind(this))
			.on('get', this.getPowerState.bind(this));


		this.valveService.addCharacteristic(Characteristic.SetDuration);
		this.valveService.addCharacteristic(Characteristic.RemainingDuration);

			//this.valveService.addCharacteristic(Characteristic.IsConfigured);

		this.valveService.getCharacteristic(Characteristic.SetDuration)
			.on('change', this.setDurationTime.bind(this))
			.on('get'   , this.getDurationTime.bind(this));

		this.valveService.getCharacteristic(Characteristic.RemainingDuration)
			.on('get', this.getRemainingTime.bind(this));

		this.valveService.getCharacteristic(Characteristic.InUse)
			.on('change', this.ChangedInUse.bind(this));


		return [this.valveService];
	}
};
