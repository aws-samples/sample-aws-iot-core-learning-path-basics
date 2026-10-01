# Raspberry Pi Camera patch for the KVS Producer SDK C++

These files make the `kvs_gstreamer_sample` application of the
[Amazon Kinesis Video Streams Producer SDK C++](https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp)
work with a Raspberry Pi Camera on current Raspberry Pi OS. They are used by the Amazon Kinesis Video Streams workshop.

| File | Purpose |
|---|---|
| `kvs-producer-pi-libcamera.patch` | Patch against SDK tag `v3.6.0`. This is what the workshop applies. |
| `kvs_gstreamer_sample.cpp` | The same change as a complete file, for reference. |
| `apply_producer.py` | Regenerates the patch when moving to a newer SDK tag. Fails if the upstream code no longer matches. |

## Tested with

- Raspberry Pi 4 with Camera Module v1.3 (`ov5647`)
- Raspberry Pi OS Trixie (64-bit)
- Producer SDK C++ `v3.6.0` (commit `a6efdf5d2fe1fcc5be85048a0c1b6a90ab80ff72`)

## Apply

```bash
cd ~
git clone --branch v3.6.0 --depth 1 \
  https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp.git kvs-producer-sdk-cpp
cd ~/kvs-producer-sdk-cpp
curl -sL https://raw.githubusercontent.com/aws-samples/sample-aws-iot-core-learning-path-basics/main/iot_helpers/kvs_pi_camera/kvs-producer-pi-libcamera.patch \
  | git apply
mkdir -p build && cd build
cmake .. -DBUILD_GSTREAMER_PLUGIN=ON -DBUILD_DEPENDENCIES=OFF -DALIGNED_MEMORY_MODEL=ON \
  -DCMAKE_C_FLAGS="-D_GNU_SOURCE"
make -j$(nproc)
```

`-D_GNU_SOURCE` is needed on Raspberry Pi OS Trixie: its GCC 14 rejects the undeclared
`pthread_getname_np` call in the SDK's PIC dependency. It is harmless on older releases.

## What the patch changes

All changes are inside `gstreamer_live_source_init()` in `samples/kvs_gstreamer_sample.cpp`:

- Uses `v4l2h264enc` (Pi 4 hardware encoder) instead of the removed `omxh264enc`, with `x264enc` as fallback (Pi 5).
- Uses `libcamerasrc` instead of `v4l2src` for the Pi Camera.
- Uses `v4l2convert` instead of `videoconvert` on the Pi to avoid a green image.
- Skips the caps query for `libcamerasrc`, which leaves the hardware encoder in a bad state.
- Sets `level=4` instead of `profile=baseline` on the Pi, and builds caps with an explicit framerate.

## Regenerate for a newer SDK tag

```bash
git clone --branch <new-tag> --depth 1 \
  https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp.git kvs-producer-sdk-cpp
cd kvs-producer-sdk-cpp
python3 /path/to/apply_producer.py samples/kvs_gstreamer_sample.cpp
git diff > kvs-producer-pi-libcamera.patch
```

## License

`kvs_gstreamer_sample.cpp` and `kvs-producer-pi-libcamera.patch` are derived from the Amazon Kinesis Video Streams
Producer SDK C++, Copyright 2017 Amazon.com, Inc. or its affiliates, licensed under the Apache License 2.0.
`kvs_gstreamer_sample.cpp` was modified from the `v3.6.0` original as described above.
See `THIRD_PARTY_LICENSES.txt` at the repository root.
