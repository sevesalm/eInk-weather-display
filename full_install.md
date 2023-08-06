# Raspberry

## Setup Raspberry in headeless mode

See: [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html) for a more detailed guide.

### Install Raspberry Pi OS on MicroSD card

_Note_: Be very careful when using `dd` command below. Wrong target device (`of` parameter) might do serious harm.

1. Download the [OS Image](https://www.raspberrypi.com/software/)
1. List your disks: `diskutil list`
1. Unmount the MicroSD :`diskutil unmountDisk /dev/diskN`
1. Write the image: `sudo dd bs=1m if=path_of_your_image.img of=/dev/rdiskN; sync`
1. Eject the MicroSD: `sudo diskutil eject /dev/rdiskN`

### Enable WiFi and SSH

Create `wpa_supplicant.conf`:

```text
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FI

network={
    ssid="[WiFi SSID name]"
    psk="[Wifi Password]"
}
```

Create empty `ssh` file in the root.

### Enable static IP

Edit `/etc/dhcpcd.conf` and use values for your own use case:

```text
interface wlan0
static ip_address=192.168.0.253/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1
```

### User account

1. Update Vim: `sudo apt update; sudo apt install vim`
1. Create user: `sudo useradd [USERNAME]`
1. Set password: `sudo passwd [USERNAME]`
1. Copy SSH key from host: `ssh-copy-id -i [KEYFILE] [USERNAME]@[RASPBERRY_IP]`
1. Add God Powers: `sudo visudo` and add: `[USERNAME] ALL=(ALL) NOPASSWD: ALL`
1. Remove default user: `sudo deluser --remove-home pi`

### Hosts and Hostname

1. Add `127.0.0.1 localhost raspberrypi` to `/etc/hosts`

### Configure SSH

Edit `/etc/ssh/sshd_config`:

```text
PubkeyAcceptedKeyTypes ssh-ed25519,sk-ssh-ed25519@openssh.com
PermitRootLogin no
PermitEmptyPasswords no
PubkeyAuthentication yes
PasswordAuthentication no
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no
PrintMotd no
X11Forwarding no
UsePAM no
AcceptEnv LANG LC_*

# AllowUsers [USERNAME]
```

Restart the SSH daemon: `sudo service ssh restart`

### Set localization

`sudo raspi-config`

- Timezone

### Verify

Reboot and check that everything works and you can connect to Raspberry using SSH.

## Install base dependencies

Install dependencies on Raspberry Pi:

1. Install [BCM2835 Driver](https://www.airspayce.com/mikem/bcm2835/)
1. Install [BlueZ](https://github.com/ttu/ruuvitag-sensor#BlueZ)
1. Install `python3-venv`: `sudo apt install python3-venv`
1. Install `libpython3.9-dev`: `sudo apt install libpython3.9-dev`
1. Install `tmux`: `sudo apt install tmux`
1. Install `Raqm`: `sudo apt install libraqm0`

## Setup and Deploy

### Install eInk-weather-display

Do the steps from the host machine:

1. Add your configuration to `scripts/config.env` file. Please see [scripts/config.env.example](scripts/config.env.example) for an example.
1. Install venv and Pip dependencies: `scripts/install_deps.sh`
1. Install host machine deps: `brew install librsvg`
1. Convert SVG images: `scripts/convert.sh`
1. Deploy: `scripts/deploy.sh`
