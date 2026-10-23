# Audient / MK3 speaker check

Double-click **Open Sound Player.command** in the project folder, or run:

```sh
python3 scripts/start_sound_player.py --configure
```

Open <http://127.0.0.1:8765/>. Keep the Audient monitor knob low, choose **1 kHz test**, and gradually adjust the hardware knob until comfortable. The default digital peak is −36 dBFS. Choose left, right, or both to check the connected speakers. **Stop** ends playback. Nothing plays automatically.

**100 Hz–20 kHz sweep** plays a five-second logarithmic sweep with 20 ms raised-cosine end ramps. This is a local connection-check signal, not a paper stimulus. **Start microphone check** requests browser permission and selects the Audient input by name. The stream requests 96 kHz, two channels, and disables echo cancellation, noise suppression, and automatic gain; actual settings appear on screen. The microphone is metered through a silent analysis path and is never monitored through the speakers. The live display shows peak/RMS digital levels and a dominant FFT frequency; each playback retains a summary. **Stop microphone** releases input tracks; **Stop all** ends playback and microphone capture.

For the planned Earthworks M50 on XLR input 1, enable the left +48V control beneath gain knob 1, with speaker volume turned down while switching. The microphone requires 24–48 V phantom power at 10 mA ([Earthworks specification](https://earthworksaudio.com/measurement-microphones/m50/)); the Audient provides independent phantom power per input ([Audient hardware guide](https://audient.github.io/audient-documentation-site/id14/front-panel/)). Software does not verify the physical switch position. On October 23, input 1 showed a peak near 996 Hz during the 1 kHz test and received signal during the sweep; see the [observed check record](../docs/verification/2026-10-23_Audient_Microphone_Check.json). This was not a calibrated acoustic response measurement.

The launcher selects the connected Audient interface as macOS application playback output at 96 kHz. System alert output and microphone input are not changed. Other applications using the default playback device may also use the Audient. Without `--configure`, the launcher only reads device status. Stop the server with Ctrl+C.

The player contains a short 1 kHz test and a bounded sequence of synthetic sine pips. The default frequency subset is 2, 4, 6, 8, 9, and 10.5 kHz. The optional full set uses the paper's 14 listed Sheep E frequencies, extending to 27 kHz. See [paper notes, stimulus construction](../docs/paper/Paper_Notes.md). These are generated test sounds, not recordings or a recovery of the paper's stimulus order. The paper's unresolved 37-frequency Sheep C array is not reconstructed.

Pips are 10 ms at 96 kHz, start at zero phase, and use 2 ms raised-cosine onset/offset ramps. The 96-kHz output is a local choice; the paper used a 192-kHz DAC. Raised cosine is also a local choice: the paper gives the ramp duration but does not specify its shape. A single precomputed buffer holds each sequence; browser scheduling is not a measured acoustic timestamp. The UI reports its actual audio-context sample rate and checks the Mac output before playback.

This is a human speaker-connection check. A successful software check does not verify the physical Audient mixer route, speaker wiring, acoustic bandwidth, SPL, distortion, or stimulus timing. Frequencies above normal hearing may be inaudible; do not increase level to chase them. Digital dBFS is not acoustic dB SPL. No animal protocol, calibration recording, neural recorder integration, or experimental performance is supplied. The educational walkthrough in `web/` remains separate.

On October 23, 2026, macOS reported an **Audient iD14**, six output channels, USB transport. Its application playback default was changed from Bose QC Ultra 2 HP at 44.1 kHz to Audient iD14 at 96 kHz and verified by CoreAudio readback and `system_profiler`. Hardware gain was not changed. The connected speakers' model and cabling are user-reported; the software cannot inspect them.
