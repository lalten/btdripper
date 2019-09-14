# btdripper

Control your [Kamoer Dripping Pro](http://kamoer.com/Products/showproduct.php?id=308&lang=en) plant irrigation pump with Python.

You can read more about the idea behind this in [this blog post](https://blog.laure.nz/2019/08/29/reverse-engineering-towards-a-smarter-bluetooth-balcony-plant-irrigation-system-part-1/).

## Installation

```sh
pip3 install btdripper
```

## Demo

You can run `btdripper.py` from the command line.
```
$ btdripper.py --help
usage: btdripper.py [-h] [--adapter ADAPTER] [--mac MAC] [--duration DURATION]

Dripper Pro SDK Demo

optional arguments:
  -h, --help           show this help message and exit
  --adapter ADAPTER    Name of Bluetooth adapter, defaults to 'hci0'
  --mac MAC            Mac address of Dripper Pro device to connect to
  --duration DURATION  Duration in seconds to turn on the pump. Default is 1s
```

Or you can directly import it into your project
```python
$ python
Python 3.6.8 (default, Jan 14 2019, 11:02:34)
>>> import btdripper
>>> dripper = btdripper.BtDripper()
>>> dripper.on()
>>> dripper.off()
```

## API

First, you need to create a new `BtDripper` instance.
When you use an empty constructor, the library will try to connect to the first BLE device called "grow_c" that it finds.
If you already know your dripper's MAC address, you can provide it as a parameter to speed up connection. The parameter is `mac_address` and it takes an address in the format `"90:e2:02:9c:db:50"`.
Should you have more than one bluetooth adapter, you can supply that with the `adapter_name` parameter (default is `"hci0"`)
There is also a way to reuse a `gatt.DeviceManager` via the `manager` parameter if you need to support more than one bluetooth device.

The BtDripper class supports the following methods:

* `on` - turns dripper on
* `off` - turns dripper off
* `send_sequence` - sends a sequence of user-defined byte strings, should you want to experiment yourself.

Note that if you send malformed custom sequences, it can cause the driiper's software to hang. It will not reconnect and only a power cycle helps.

## Todo

This is a very basic implementation. It should be possible to find out how the timer mode works and integrate that. Maybe there is even a way to run the pump at lower speeds?

There are currently no timeouts or error handling. Also I wouldn't be surprised if the library breaks in an unexpected situation. Use at your own risk :)
