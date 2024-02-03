# Epic Games Store Weekly Free Game Claimer

This project is based (and a few functions just straight up copied) on [this repository by MasonStooksbury](https://github.com/MasonStooksbury/Free-Games-V2/blob/main/README.md). That repo is a free games claimer for the epic games desktop app with login included, however, i use linux and the [Heroic Games Launcher](https://heroicgameslauncher.com/) so it's modified to work with that but i am kinda new to python and linux so may be very buggy (check the [caveats](#caveats)).

Any bugfix or improvement is welcomed, just raise an issue or make a pull request and i'll get to it when i have the time.

## Installation
Make sure to have `python3` installed along with `pip3` (i used pip, i don't know if it works with others like `conda` or such, but i guess it should).

* Clone the repo.
* Run `pip3 install -r requirements.txt`

> [!NOTE]
> On debian for some reason this throws: `error: externally-managed-environment`. So you either make a virtual environment (read below) or just delete/change the name of the `/usr/lib/python3.11/EXTERNALLY-MANAGED` file. I got the solution [from here](https://www.jeffgeerling.com/blog/2023/how-solve-error-externally-managed-environment-when-installing-pip3).
> 
> I tried to make it work in a `virtualenv` but i got some kind of permission error idk (`[1061313:0203/091228.625402:FATAL:zygote_host_impl_linux.cc(215)] Check failed: . : Invalid argument (22) Trace/breakpoint trap`). If you can solve it, great, make a pull request please.

## Usage

It's really simple honestly, since heroic can be opened with command line as `heroic`, and this file does that...

**Just execute the `claimer.py` file with `python3 claimer.py`!**

> [!IMPORTANT]
> If you get an error like `Xlib.error.DisplayConnectionError: Can't connect to display ":0": b'Authorization required, but no authorization protocol specified` then you might need to execute `xhost +` just before running the `claimer.py`. All i could get on google is that this is an error in the `python-xlib` package and that it should have been solved but i still get that error. After running the script you can make run `xhost -` to reverse.

The script will open heroic games launcher with the `subprocess` module (it assumes you are logged in and the `Remember me` is activated), and it'll go straight to the Epic Games Store and look for the free game and claim it.

This doesn't include login since when opening the Heroic Games Launcher (at least for me), the session is still open. So feel free to fork the repo if you need login. Based on this and MasonStooksbury's repo it should be fairly ease.

## Schedule to run automatically

I use `cron` to run this weekly (as of feb 2 2024 games are released every thursday at 1:00 PM).

In case you don't know how to use `cron`:
```
+---------------- minute (0 - 59)
|  +------------- hour (0 - 23)
|  |  +---------- day of month (1 - 31)
|  |  |  +------- month (1 - 12) OR jan,feb,mar,apr ...
|  |  |  |  +---- day of week (0 - 6) (Sunday = 0 or 7) OR sun,mon,tue,wed,thu,fri,sat
|  |  |  |  |
*  *  *  *  * command to be executed
```

You can add this into your cronjobs to execute this script weekly (run `crontab -e` to edit your cronjobs):
```shell
# Runs every Thursday at 13:30 hs.
30 13 * * thu python3 /path/to/script/claimer.py
```

If you got the error i talked about in [usage section](#usage) then you can make a script to execute `xhost +` right before running `claimer.py` and `xhost -` right after, like this:
```shell
#!/bin/bash
xhost +
python3 claimer.py
xhost -
```

Make sure to give execute permissions to the script using the following command:
```shell
chmod +x script.sh
```

And then you can run this script instead of the python file directly:
```shell
# Runs every Thursday at 13:30 hs.
30 13 * * thu /path/to/script.sh
```

## Caveats

I already mentioned them along this file but in case you skipped here:

* It doesn't work on a virtual environment.
* If you get a display connection error from xlib you need to run `xhost +` before executing the file.
* Check in source code when the app is scrolling in case it's scrolling to much or too little. Look for `MAY_MODIFY` in `claimer.py`.
* I also got an error (`OSError: X get_image failed: error 8 (73, 0, 1178)`) with wayland and the `Pillow` module from python, so if there is a something like a `ImageGrab.grab()` error you may have to uncomment the line `#WaylandEnable=false` on `/etc/gdm3/daemon.conf`:
	```conf
	[daemon]
	# Uncomment the line below to force the login screen to use Xorg
	WaylandEnable=false
	```
	And after that `systemctl restart gdm3` (**THIS WILL RESET THE PC**).

If you know how to solve any of this, then please tell or just make a pull request.

## TODO

* Test/Trim sleep times in between actions to make it faster.