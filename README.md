# Olympus Wifi-Enabled Camera on Linux, macOS and Windows

Some Olympus cameras have wifi capability. Photos can be downloaded from them;
they can also remote control the camera: the live camera picture is
transmitted and they take pictures and modify settings via wifi.

This repository provides Python code to connect to a wifi-enabled Olympus
camera, set the camera's date and time, download images, watch the live camera
view in a window, take a picture, change camera settings, and turn off the
camera. In addition, command-line arguments allow to send user-specific commands
to the camera.

## Connect Camera to Wifi

The best way to find out how to enter WiFi mode for a particular Olympus camera
is to check the manual. In general, wifi needs to be enabled in the camera
settings and set to "private". Then, to enter WiFi mode on a TG-5 press and
hold the "Menu" button. In addition to a QR code, the camera display will show
its SSID (wireless network name) and password. The computer must be connected
to the camera's wireless network using this password. This may require
disconnecting from the wireless network to which the computer is initially
connected.

It is important to use a browser to verify that the camera is actually
connected: The camera will respond to
[http://192.168.0.10/DCIM](http://192.168.0.10/DCIM) with a web page.
**If the browser does not display this camera web page, the camera is not yet
connected and the software in this repository will not work.**
The [Olympus Photosync](https://github.com/mauriciojost/olympus-photosync)
repository contains more detailed instructions and images on connecting the
camera to a computer.

## Usage

Several of the scripts can be called. The script `olympus-camera.py` offers the
the full functionality. Others have only a subset of its functionality.

```
usage: olympus-camera.py [-h] [--output OUTPUT] [--download] [--power_off] [--set_clock] [--shoot] [--liveview] [--port PORT] [--cmd CMD [CMD ...]]

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Local directory for downloaded photos.
  --download, -d        Download photos from camera.
  --power_off, -p       Turn camera off.
  --set_clock, -c       Set camera clock to current time.
  --shoot, -S           Take a picture.
  --liveview, -L        Show live camera stream. Close the live view window to quit. This script will run a few more seconds, then exit.
  --port PORT, -P PORT  UPD port for liveview (default: 40000).
  --cmd CMD [CMD ...], -C CMD [CMD ...]
                        Command to send to camera; multiple commands are supported.
```

### Option --download, -d

The options `-d` and `--download` download the images from the camera.

Instead of calling `olympus-camera.py` with option `--download`, download can
be started directly by calling `download.py`.

### Option --output OUTPUT_DIRECTORY, -o OUTPUT_DIRECTORY

Specifies the output directory for image downloads. Without this option, images
will be downloaded to `~/Pictures/YEAR` where YEAR is the year the picture was
taken.

### Option --power_off, -p

Turn the camera off after executing the other commands.

### Option --set_clock, -c

Set the camera clock to the current date and time.

### Option --shoot, -S

The camera takes a picture.

### Option --liveview, -L

Open a window and display the a live view of the camera. Menus allow to take a
photo, select the resolution of the photo stream and adjust all camera
properties.

![LiveView](/images/liveview.png)

Instead of running `olympus-camera.py` with the `--liveview` option, the live
view can be started directly by calling `liveview.py`.

The live view window may not open on Windows. This happens when the Windows
Firewall is blocking Python from receiving the live view stream. In this case
open the firewall settings and allow Python network access.

### Option --cmd CMD, -c CMD

The option `--cmd` allows to send commands directly to the camera. Multiple
options are often needed because most commands work only in certain modes
and the first command usually switches the mode.

Any commands can be sent to the camera in this way. To get started
with camera commands, [this spec](https://raw.githubusercontent.com/ccrome/olympus-omd-remote-control/master/OPC_Communication_Protocol_EN_1.0a/OPC_Communication_Protocol_EN_1.0a.pdf)
might be helpful. It explains a lot but not all its information applies to
other camera models.

#### Send a command

The commands and command options supported by the connected camera can be
obtained as follows:

```
./olympus-camera.py --cmd get_commandlist
```

On Windows, we need to call Python with `olympus-camera.py` as argument
instead:

```
python.exe olympus-camera.py --cmd get_commandlist
```

#### Command with output redirection

The command returns a list of all the supported commands and options in the form
of an XML document. This long document can be saved to a file with redirection:

```
./olympus-camera.py --cmd "get_commandlist > commandlist.xml"
```

#### Commands return XML results

This command returns the date on which the AGPS data expires:

```
$ ./olympus-camera.py --cmd get_agpsinfo
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
<?xml version="1.0"?>
<response>
<modulemaker>3</modulemaker>
<expiredate>20221111</expiredate>
</response>
```

The data returned is often XML. In this case, the camera's AGPS data must
be updated by November 11th, 2022.

#### List images

Images on the camera can also be listed:

```
$ ./olympus-camera.py --cmd "get_imglist DIR=/DCIM/100OLYMP"
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
VER_100
/DCIM/100OLYMP,PA220001.JPG,2514746,0,21846,43106
```

There is only one image. It is `PA220001.JPG` in the directory `/DCIM/100OLYMP`.
The image is a file of 2,514,746 bytes. Note that this command returns a plain
text result. `get_imglist` is one of the few commands commands that return
plain text instead of XML.

We want to download a smaller version of the image using the `get_resizeimg`
command:

#### Command with binary result

```
$ ./olympus-camera.py --cmd "get_resizeimg DIR=/DCIM/100OLYMP/PA220001.JPG size=1024"
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
Command 'get_resizeimg DIR=/DCIM/100OLYMP/PA220001.JPG size=1024' returned 195,186 bytes of image/jpeg. Re-run with redirection to obtain data.
```

While `olympus-camera.py` prints all the output of the command `get_commandlist`
above, it does not write binary data to the terminal. We need to re-run this
command with redirection

```
$ ./olympus-camera.py --cmd "get_resizeimg DIR=/DCIM/100OLYMP/PA220001.JPG size=1024 > pa220001_resized.jpg"
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
```
and the image is downloaded and saved to a file.

#### Command restricted to a particular mode

The TG-5 has 3 modes: `play`, `rec`, and `shutter`. Many commands are only
accepted in one of the modes. The `switch_cammode` command is used to switch
between modes.

```
$ ./olympus-camera.py --cmd "get_camprop com=get propname=takemode"
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
Error #520 for url 'http://192.168.0.10/get_camprop.cgi?com=get&propname=takemode': errorcode=1001.
```

ErrorCode 1001 appears to indicate that the camera is in the wrong mode. We
will set the mode to `rec` and try again:

```
$ ./olympus-camera.py --cmd "switch_cammode mode=rec" "get_camprop com=get propname=takemode"
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
<?xml version="1.0"?><get><value>iAuto</value></get>
```

The command no longer fails and we get the result.

#### Command argument check

The `--cmd` option checks commands and arguments before sending them to the
camera. These checks are based on the data retrieved with `get_commandlist`.
If an argument is wrong, the error message includes a list of valid arguments:

```
$ ./olympus-camera.py --cmd "switch_cammode mode=rec" "get_camprop com=get propname=whatever"
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
Error in get_camprop: 'whatever' in propname=whatever not supported; supported: propname=touchactiveframe, propname=takemode, propname=drivemode,
propname=focalvalue, propname=expcomp, propname=isospeedvalue, propname=wbvalue, propname=artfilter, propname=supermacrosub, propname=supermacrozoom,
propname=colortone, propname=cameradrivemode, propname=colorphase, propname=SceneSub, propname=ArtEffectTypePopart, propname=ArtEffectTypeRoughMonochrome,
propname=ArtEffectTypeToyPhoto, propname=ArtEffectTypeDaydream, propname=ArtEffectTypeCrossProcess, propname=ArtEffectTypeDramaticTone,
propname=ArtEffectTypeLigneClair, propname=ArtEffectTypePastel, propname=ArtEffectTypeMiniature, propname=ArtEffectTypeVintage, propname=ArtEffectTypePartcolor.
```

#### Command name check

These checks also work for commands:

```
$ ./olympus-camera.py --cmd whatever
Connected to Olympus TG-5, version 3.10, oitrackversion 2.20.
Error: command 'whatever' not supported; valid commands: get_commandlist, get_connectmode, switch_cammode, get_caminfo, exec_pwoff, get_resizeimg,
get_movplaytime, clear_resvflg, get_rsvimglist, get_rsvimglist_ext, get_imglist, get_imglist_ext, get_thumbnail, get_screennail, get_movfileinfo,
exec_takemotion, exec_takemisc, get_camprop, set_camprop, get_activate, set_utctimediff, get_gpsdivunit, get_unusedcapacity, get_dcffilenum, req_attachexifgps,
req_storegpsinfo, exec_shutter, get_agpsinfo, send_agpsassistdata, update_agpsassistdata, check_gpsrecording, check_mountmedia, get_gpsloglist,
get_gpsimglist, get_gpsrecordinglog, exec_gpslogfiling, check_snsrecording, get_snsloglist, get_gpssnsimglist, get_snsrecordinglog,
exec_snslogfiling, exec_gpssnslogfiling, get_moviestreaminfo, ready_moviestream, start_moviestream, stop_moviestream, exit_moviestream.
```

Your output may vary. The commands and command arguments vary from camera
model to camera model.

## Python Code

Several of the modules may be useful for other software. Class `OlympiaCamera`
communicates with the camera. This class allows to send commands to the camera
and it converts the camera's XML responses into Python dicts. These member
functions are particularly useful:

```
from camera import OlympiaCamera

camera = OlympiaCamera()
```

Upon initialization the `OlympiaCamera` class issues command `get_commandlist`
and uses this information about all the camera commands and command options
to check further requests to the camera.

```
camera.send_command('command', option1=value, ...)
```

Sends the command to the camera and returns a `requests.Response` object if
successful. On error, it will print an error message and return `None`.

```
camera.xml_query('command', option1=value1, ...)
```

Sends a command to the camera, parses the XML result and returns the result as
a Python `dict`. In case of an error it will print an error message and return
`None`. To obtain the AGPS expiration date as in the example above, we can call
`camera.xml_query('get_agpsinfo')['expiredate']` to get the result `20221111`
as a string.

```
camera.set_clock()
```
Sets date and time.

```
camera.get_images()
```

Returns a list of all images on the camera. For each each image there is the
file name including directory path, the size in bytes, and the date and time in
ISO format. 

```
camera.download_thumbnail('/DCIM/100OLYMP/PA220001.JPG')
camera.download_image('/DCIM/100OLYMP/PA220001.JPG')
```

Return the image thumbnail and the full image respectively.


## Dependencies

This code requires Python 3.7 or later as it uses the `SimpleQueue` class and
the `dataclasses` module. This code relies on the package `requests` to
communicate with the camera as well as on `PIL` to display the live stream from
the camera.

All necessary packages can be installed on Ubuntu Linux and probably many other
Debian-style Linux distributions with this command:
```
sudo apt install python3-tk python3-pil python3-pil.imagetk python3-requests
```

On other platforms, `pip` may do the trick:
```
pip install Pillow requests
```
