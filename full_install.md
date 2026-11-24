# Setup Raspberry Pi in headless mode

See: [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html) for a more detailed guide.

_Note_: The BCM2835 library does not work on Raspberry Pi 5. Use Raspberry Pi Zero 2 W, 3 or 4 (64-bit).

## Install Raspberry Pi OS on MicroSD card

_Note_: Be very careful when using `dd` command below. Wrong target device (`of` parameter) might do serious harm.

1. Download the [OS Image](https://www.raspberrypi.com/software/operating-systems). This manual has been tested with 64-bit Raspberry Pi OS 13 (trixie), image dated 6 Oct 2026, kernel 6.18.
1. Uncompress the `.xz` file so you get the contained `.img` image.
1. List your disks: `diskutil list`
1. Unmount the MicroSD: `diskutil unmountDisk /dev/diskN`
1. Write the image: `sudo dd bs=1m if=path_of_your_image.img of=/dev/rdiskN; sync`

## Enable WiFi and SSH

After `dd` has finished, macOS usually mounts the `bootfs` partition of the MicroSD at `/Volumes/bootfs`. If it does not, mount it: `diskutil mountDisk /dev/diskN`. The `network-config` and `user-data` files edited below are in that partition.

Edit the `network-config` by adding the following:

```yaml
network:
  version: 2
  wifis:
    wlan0:
      dhcp4: true
      optional: true
      regulatory-domain: FI         # Replace with your country code
      access-points:
        "MY SSID":                  # Replace with your SSID
          password: "mypassword"    # Replace with your WiFi password
```

Replace the `user-data` contents with the following and replace the `<PLACEHOLDERS>` (including the angle brackets). The config installs BCM2835 library version 1.77. Newer versions may also work.

```yaml
#cloud-config
hostname: <HOSTNAME>
timezone: <TIMEZONE>   # e.g. Europe/Helsinki
users:
- name: <USERNAME>
  groups: [sudo, gpio, spi, i2c, video]
  shell: /bin/bash
  sudo: ALL=(ALL) NOPASSWD:ALL
  lock_passwd: true
  ssh_authorized_keys:
  - <PUBLIC_KEY>       # contents of ~/.ssh/id_ed25519.pub
ssh_pwauth: false
disable_root: true
package_update: true
package_upgrade: true
packages:
- unattended-upgrades
- build-essential
- wget
- libraqm0
- vim
write_files:
- path: /etc/ssh/sshd_config.d/10-hardening.conf
  permissions: '0644'
  content: |
    PermitRootLogin no
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    AuthenticationMethods publickey
    X11Forwarding no
runcmd:
- [systemctl, enable, --now, ssh]
- [raspi-config, nonint, do_spi, "0"]
- |
  set -e
  cd /tmp
  wget -q https://www.airspayce.com/mikem/bcm2835/bcm2835-1.77.tar.gz
  tar xzf bcm2835-1.77.tar.gz
  cd bcm2835-1.77
  ./configure
  make
  make install
power_state:
  mode: reboot
  message: Rebooting to apply config.txt changes
  condition: true
```

_Note_: SPI is enabled with `raspi-config` in `runcmd` instead of the `rpi` module, because the `rpi` module reboots immediately and interrupts the package installation. `power_state` reboots once after cloud-init has finished.

Eject the MicroSD: `diskutil eject /dev/diskN` and insert in Raspberry Pi and turn it on.

## Verify

Start up the Raspberry Pi. The first boot can take several minutes as cloud-init upgrades packages and compiles the BCM2835 library, and then reboots once automatically. Do not power off or reboot it yourself during that time. Then check the setup:

1. Connect: `ssh <USERNAME>@<HOSTNAME>.local`
1. Wait for cloud-init to finish: `cloud-init status --wait` (should print `status: done`)
1. SPI is enabled: `ls /dev/spidev*` (should list `/dev/spidev0.0` and `/dev/spidev0.1`)
1. BCM2835 is installed: `ls /usr/local/lib/libbcm2835.a`
1. Timezone is set: `timedatectl`

If something failed, see `/var/log/cloud-init-output.log` and `/var/log/cloud-init.log`.

# Setup and Deploy

## Install eInk Weather Display

Do the steps from the host machine:

1. Create `scripts/config.env` from [scripts/config.env.example](scripts/config.env.example) and set the Raspberry's SSH host and install directories. See [CONFIGURATION.md](CONFIGURATION.md#deployment-configuration-scriptsconfigenv).
1. Create `eInk-weather-display/config.toml` from [config_example.toml](eInk-weather-display/config_example.toml) (all options are documented in [CONFIGURATION.md](CONFIGURATION.md)) and set `dev_mode = false` (and the `dev_mode_random_*` options to `false`). `scripts/deploy.sh` copies your local `config.toml` to the Raspberry as is, so a development config would be deployed too.
1. Deploy: `scripts/deploy.sh`. This installs uv, Python and the Python dependencies on Raspberry, copies the app and (re)starts it as the systemd service `eink-weather`, which also starts on boot and restarts after a crash. Run it again after any change; use `scripts/deploy.sh --fresh` to recreate the virtual env from scratch (e.g. after a Python upgrade). The dependencies are installed from `uv.lock` with `uv sync --frozen`, so the Raspberry gets exactly the locked versions and packages dropped from `pyproject.toml` are removed on a normal deploy.

On Raspberry, follow the logs with `journalctl -u eink-weather -f` and check the state with `systemctl status eink-weather`. Warnings and errors are also written to `logger.log` in the app directory.

To reduce SD card wear, `scripts/deploy.sh` configures the systemd journal to be kept in RAM only (`Storage=volatile` in `/etc/systemd/journald.conf.d/eink-weather-volatile.conf`), so the journal is lost on reboot; `logger.log` persists. Journal files written before the change stay in `/var/log/journal` and can be removed with `sudo rm -rf /var/log/journal`.
