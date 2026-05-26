# Streaming Performance Tuning (Raspberry Pi 3)

Runbook for getting reliable YouTube live / mpv playback on a Pi 3.
The most common symptom — periodic 1-second stutters during live news
playback — usually turns out to be a stack of unrelated issues: weak
onboard WiFi, BT/WiFi RF coexistence, mpv flags hostile to flaky
networks. This doc captures the diagnostic flow and the fixes.

Hardware in scope: **Raspberry Pi 3 Model B Rev 1.2**, Raspberry Pi OS
Bookworm Lite. Pi 3 A+, Pi Zero 2 W, and Pi 4 share most issues with
different memory / RF profiles — fixes generalize.

---

## Diagnostic playbook

Run in order, stop at whichever shows abnormal results.

### 1. Throttling / thermal / PSU

```bash
vcgencmd get_throttled       # expect 0x0
vcgencmd measure_temp        # expect <70°C
vcgencmd measure_clock arm   # expect 1200000000 (1.2 GHz) under load
vcgencmd measure_volts core  # expect ~1.2–1.35V
```

Any non-zero `get_throttled` = undervoltage or thermal capping. Most
common cause: marginal PSU. Use a real 5V/2.5A supply.

### 2. CPU governor

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor   # expect ondemand
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq   # expect 1200000 under load
```

### 3. CPU decode bottleneck

While mpv plays:
```bash
top -d 1
```

- mpv at 200–400 % CPU → software-decoding heavy codec (VP9/AV1).
  Force H.264 via `--ytdl-format='...[vcodec^=avc1]...'`.
- mpv at <100 % CPU but stuttering → not decode-bound, look at network.

### 4. WiFi link health

```bash
iw dev wlan0 link
ping -c 10 192.168.0.1
```

Healthy 5 GHz: `tx bitrate:` hundreds of Mbit/s with `VHT MCS`, signal
> −60 dBm, ping <10 ms, 0 % loss.

If you see legacy b-rates (5.5 / 2.0 Mbit/s) with good signal, rate
adaptation is failing — see "WiFi: USB dongle" below.

### 5. Actual throughput

```bash
ifstat -i wlan0 1
# or:
watch -n 1 'cat /proc/net/dev | grep wlan0'
```

480p YouTube live needs ~190 KB/s sustained. <100 KB/s with drops to
near zero = guaranteed stutter.

---

## Fix 1: USB WiFi dongle on 5 GHz

The Pi 3 B's onboard BCM43438 WiFi is 2.4 GHz only, shares its antenna
with onboard Bluetooth (RF coexistence penalty), and has chronic
rate-adaptation issues with the `brcmfmac` driver. A USB WiFi dongle on
5 GHz bypasses all three problems.

Tested with **TP-Link T2UB Nano** (Realtek RTL8821CU, USB ID `0bda:c820`).
Driver loads automatically on Bookworm — no DKMS needed.

### Disable onboard WiFi first

```bash
grep '^dtoverlay=disable-wifi' /boot/firmware/config.txt
# if missing or commented:
echo 'dtoverlay=disable-wifi' | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

After reboot, `ip link show` should list only `wlan0` (now the USB
dongle, which has taken the `wlan0` name).

> `dtoverlay=disable-wifi` only disables the SDIO WiFi side of the
> onboard chip. USB devices are enumerated by the USB subsystem
> independent of the device tree, so the dongle is unaffected. The same
> applies to `dtoverlay=disable-bt` (UART-attached BT).

### Connect to a 5 GHz AP

Prefer a 5 GHz SSID (`*_5G` or similar) for clean spectrum:

```bash
sudo nmcli device wifi list
sudo nmcli device wifi connect <SSID-5G> --ask
```

Verify:
```bash
iw dev wlan0 link
ping -c 10 192.168.0.1
```

Expected: `freq: 5xxx`, `VHT MCS` rates in the hundreds of Mbit/s,
sub-10 ms ping, 0 % loss.

### Keep onboard Bluetooth, block USB BT

With onboard WiFi disabled, the BCM43438's antenna is dedicated to BT.
**Don't** add `dtoverlay=disable-bt` — let the onboard BT run with
exclusive antenna access.

The T2UB Nano is a single-antenna combo dongle (WiFi + BT share the
antenna). If both are active, you re-create the coexistence problem on
the USB side. Block the USB BT controller:

```bash
hciconfig -a
#   hci0 - Bus: UART, MAC B8:27:EB:* → onboard, keep
#   hci1 - Bus: USB,  MAC 9C:53:22:* → T2UB Nano, block

rfkill list                # find rfkill index of hci1
sudo rfkill block <index>  # blocks the USB BT; persists across reboots
```

> `rfkill` state is persisted by `systemd-rfkill.service` to
> `/var/lib/systemd/rfkill/` and restored at boot.

---

## Fix 2: Remove `--no-cache` from mpv

The most common single fix. `--no-cache` disables mpv's stream cache
entirely — any brief WiFi or USB latency spike immediately starves the
demuxer, even on a fast link. Live streams are affected too: caching a
few seconds lets you ride out network jitter (you play 5–10 s behind
absolute live edge, which is meaningless for 24/7 news).

The `yt-news` script previously passed `--no-cache` to save RAM on
512 MB boards (Pi 3 A+ / Pi Zero 2 W). On the 1 GB Pi 3 B or Pi 4,
remove it — mpv's default cache (a few MB) is plenty.

See [yt-news](yt-news#L12).

---

## Verification checklist

- [ ] `vcgencmd get_throttled` → `0x0`
- [ ] `ip link show` → only `wlan0` (USB dongle), no onboard `wlan*`
- [ ] `iw dev wlan0 link` → 5 GHz, `VHT MCS`, sub-10 ms ping
- [ ] `hciconfig` → `hci0` Bus UART (onboard BT only active)
- [ ] `yt-news` has no `--no-cache` flag
- [ ] YouTube live plays smoothly

---

## Deploying the `--no-cache` removal to other systems

For systems already in the field running an older `yt-news`, you don't
need anyone to hand-edit the file. A single SSH command from any Mac
(Terminal, built-in) does it. The operator never needs to know paths,
use a text editor, or see the file contents.

Send the operator this — substituting actual values:

```bash
ssh -t USERNAME@HOSTNAME 'F=$(command -v yt-news) && sudo sed -i.bak "s/ --no-cache//" "$F" && grep MPV_OPTS "$F"'
```

What it does:

- Finds `yt-news` via `$PATH` (no need to hardcode the install path)
- Removes `--no-cache` in place, keeping `yt-news.bak` as a backup
- Prints the modified `MPV_OPTS=` line so the operator can visually
  confirm the change

The operator will be prompted for **two passwords**: the SSH login
password, then sudo. (Usually the same password for a regular Pi user.)

### Revert if needed

```bash
ssh -t USERNAME@HOSTNAME 'F=$(command -v yt-news) && sudo mv "$F.bak" "$F"'
```

---

## Reverting

```bash
# Restore onboard WiFi
sudo sed -i '/^dtoverlay=disable-wifi/d' /boot/firmware/config.txt

# Unblock USB BT (if you ever want it back)
sudo rfkill unblock <index>

sudo reboot
```

For low-memory boards (Pi 3 A+ / Zero 2 W), re-add `--no-cache` to
`MPV_OPTS` in [yt-news](yt-news#L12).
