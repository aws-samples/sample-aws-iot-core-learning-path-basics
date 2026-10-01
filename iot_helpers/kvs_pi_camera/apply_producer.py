"""Apply the workshop 3-1 Pi (libcamera) changes to kvs_gstreamer_sample.cpp at v3.6.0.

Each replacement must match exactly once, so the script fails if upstream drifts.
"""

import sys

PATH = sys.argv[1]
src = open(PATH, encoding="utf-8").read()

R = []

# Change 0: add useHwEncoder
R.append(
    (
        """    bool vtenc = false, isOnRpi = false;
""",
        """    bool vtenc = false, isOnRpi = false, useHwEncoder = false;
""",
    )
)

# Change 1: encoder and source selection
R.append(
    (
        """    } else {
        // Failed creating vtenc - check pi hardware encoder
        encoder = gst_element_factory_make("omxh264enc", "encoder");
        if (encoder) {
            LOG_DEBUG("Using omxh264enc");
            isOnRpi = true;
        } else {
            // - attempt x264enc
            isOnRpi = false;
            encoder = gst_element_factory_make("x264enc", "encoder");
            if (encoder) {
                LOG_DEBUG("Using x264enc");
            } else {
                LOG_ERROR("Failed to create x264enc");
                return 1;
            }
        }
        source = gst_element_factory_make("v4l2src", "source");
        if (source) {
            LOG_DEBUG("Using v4l2src");
        } else {
            LOG_DEBUG("Failed to create v4l2src, trying ksvideosrc")
            source = gst_element_factory_make("ksvideosrc", "source");
            if (source) {
                LOG_DEBUG("Using ksvideosrc");
            } else {
                LOG_ERROR("Failed to create ksvideosrc");
                return 1;
            }
        }
        vtenc = false;
    }
""",
        """    } else {
        // Pi 4: use v4l2h264enc (hardware H.264 via V4L2 M2M)
        encoder = gst_element_factory_make("v4l2h264enc", "encoder");
        if (encoder) {
            LOG_DEBUG("Using v4l2h264enc");
            isOnRpi = true;
            useHwEncoder = true;

            // Pi Camera requires libcamerasrc on Bookworm and later
            source = gst_element_factory_make("libcamerasrc", "source");
            if (source) {
                LOG_DEBUG("Using libcamerasrc");
            } else {
                LOG_DEBUG("libcamerasrc not available, trying v4l2src");
                source = gst_element_factory_make("v4l2src", "source");
                if (!source) {
                    LOG_ERROR("Failed to create video source");
                    return 1;
                }
            }
        } else {
            // Software fallback (Pi 5 or missing hardware encoder)
            encoder = gst_element_factory_make("x264enc", "encoder");
            if (!encoder) {
                LOG_ERROR("Failed to create any H.264 encoder");
                return 1;
            }
            LOG_DEBUG("Using x264enc");

            // On Pi 5 with Pi Camera, we still need libcamerasrc
            source = gst_element_factory_make("libcamerasrc", "source");
            if (source) {
                LOG_DEBUG("Using libcamerasrc (Pi 5 software encode path)");
                isOnRpi = true;
            } else {
                // Non-Pi fallback (EC2, desktop Linux, Windows)
                isOnRpi = false;
                source = gst_element_factory_make("v4l2src", "source");
                if (!source) {
                    source = gst_element_factory_make("ksvideosrc", "source");
                    if (!source) {
                        LOG_ERROR("Failed to create video source");
                        return 1;
                    }
                }
            }
        }
        vtenc = false;
    }
""",
    )
)

# Change 2: source configuration
R.append(
    (
        """    } else {
        g_object_set(G_OBJECT (source), "do-timestamp", TRUE, "device", "/dev/video0", NULL);
    }
""",
        """    } else if (!isOnRpi) {
        // Only set device for non-Pi sources (v4l2src/ksvideosrc)
        g_object_set(G_OBJECT (source), "do-timestamp", TRUE, "device", "/dev/video0", NULL);
    }
    // libcamerasrc on Pi needs no additional configuration
""",
    )
)

# Change 3: skip caps query for libcamerasrc (wrap the whole query block)
OLD3_START = """    /* Determine whether device supports h264 encoding and select a streaming resolution supported by the device*/
"""
OLD3_END = """    gst_caps_unref(src_caps);
    gst_object_unref(srcpad);
"""
s = src.find(OLD3_START)
e = src.find(OLD3_END)
if s < 0 or e < 0 or src.count(OLD3_START) != 1 or src.count(OLD3_END) != 1:
    sys.exit("Change 3 anchors not found exactly once")
e += len(OLD3_END)
body = src[s + len(OLD3_START) : e]
indented = "".join(("    " + line if line.strip() else line) for line in body.splitlines(True))
new3 = (
    OLD3_START
    + """    if (isOnRpi) {
        // Skip caps query for libcamerasrc: the READY->NULL cycle leaves the
        // V4L2 M2M encoder in a bad state causing "not enough memory" errors.
        if (width == 0 && height == 0) {
            if (useHwEncoder) {
                width = 1296;
                height = 972;
                framerate = 30;
            } else {
                // Pi 5 software encoding: default to 720p for performance
                width = 1280;
                height = 720;
                framerate = 30;
            }
        }
        data->h264_stream_supported = false;
    } else {
"""
    + indented
    + """        gst_caps_unref(query_caps_h264);
        gst_caps_unref(query_caps_raw);
    }
"""
)
src = src[:s] + new3 + src[e:]

# Change 4: video converter + fresh source filter caps
R.append(
    (
        """    if (!data->h264_stream_supported) {
        video_convert = gst_element_factory_make("videoconvert", "video_convert");

        if (!video_convert) {
""",
        """    if (!data->h264_stream_supported) {
        if (isOnRpi) {
            video_convert = gst_element_factory_make("v4l2convert", "video_convert");
            if (!video_convert) {
                LOG_WARN("v4l2convert not available, falling back to videoconvert");
                video_convert = gst_element_factory_make("videoconvert", "video_convert");
            }
        } else {
            video_convert = gst_element_factory_make("videoconvert", "video_convert");
        }

        if (!video_convert) {
""",
    )
)
R.append(
    (
        """    /* source filter */
    if (!data->h264_stream_supported) {
        gst_caps_set_simple(query_caps_raw,
                            "format", G_TYPE_STRING, "I420",
                            NULL);
        g_object_set(G_OBJECT (source_filter), "caps", query_caps_raw, NULL);
    } else {
        gst_caps_set_simple(query_caps_h264,
                            "stream-format", G_TYPE_STRING, "byte-stream",
                            "alignment", G_TYPE_STRING, "au",
                            NULL);
        g_object_set(G_OBJECT (source_filter), "caps", query_caps_h264, NULL);
    }
    gst_caps_unref(query_caps_h264);
    gst_caps_unref(query_caps_raw);
""",
        """    /* source filter: create fresh caps with explicit framerate */
    if (!data->h264_stream_supported) {
        GstCaps *raw_caps = gst_caps_new_simple("video/x-raw",
                                                "format", G_TYPE_STRING, "I420",
                                                "width", G_TYPE_INT, width,
                                                "height", G_TYPE_INT, height,
                                                "framerate", GST_TYPE_FRACTION, framerate, 1,
                                                NULL);
        g_object_set(G_OBJECT (source_filter), "caps", raw_caps, NULL);
        gst_caps_unref(raw_caps);
    } else {
        GstCaps *h264_src_caps = gst_caps_new_simple("video/x-h264",
                                                     "width", G_TYPE_INT, width,
                                                     "height", G_TYPE_INT, height,
                                                     "framerate", GST_TYPE_FRACTION, framerate, 1,
                                                     "stream-format", G_TYPE_STRING, "byte-stream",
                                                     "alignment", G_TYPE_STRING, "au",
                                                     NULL);
        g_object_set(G_OBJECT (source_filter), "caps", h264_src_caps, NULL);
        gst_caps_unref(h264_src_caps);
    }
""",
    )
)

# Change 5: encoder configuration
R.append(
    (
        """        } else if (isOnRpi) {
            g_object_set(G_OBJECT (encoder), "control-rate", 2, "target-bitrate", bitrateInKBPS*1000,
                         "periodicty-idr", 45, "inline-header", FALSE, NULL);
        } else {
            g_object_set(G_OBJECT (encoder), "bframes", 0, "key-int-max", 45, "bitrate", bitrateInKBPS, NULL);
        }
""",
        """        } else if (useHwEncoder) {
            // v4l2h264enc uses extra-controls (V4L2 control interface)
            GstStructure *extra_controls = gst_structure_new("controls",
                "repeat_sequence_header", G_TYPE_INT, 1,
                "video_bitrate", G_TYPE_INT, bitrateInKBPS * 1000,
                "video_gop_size", G_TYPE_INT, 30,
                "h264_i_frame_period", G_TYPE_INT, 30,
                NULL);
            g_object_set(G_OBJECT(encoder), "extra-controls", extra_controls, NULL);
            gst_structure_free(extra_controls);
        } else {
            g_object_set(G_OBJECT (encoder), "bframes", 0, "key-int-max", 45, "bitrate", bitrateInKBPS, NULL);
            if (isOnRpi) {
                // Pi 5 software encoding: ultrafast preset for real-time,
                // key-int-max = framerate for ~1 second fragments
                g_object_set(G_OBJECT (encoder), "speed-preset", 1, "tune", 0x4,
                             "key-int-max", framerate, NULL);
            }
        }
""",
    )
)

# Change 6: output filter caps
R.append(
    (
        """    if (!data->h264_stream_supported) {
        gst_caps_set_simple(h264_caps, "profile", G_TYPE_STRING, "baseline",
                            NULL);
    }
""",
        """    if (!data->h264_stream_supported) {
        if (isOnRpi) {
            gst_caps_set_simple(h264_caps, "level", G_TYPE_STRING, "4", NULL);
        } else {
            gst_caps_set_simple(h264_caps, "profile", G_TYPE_STRING, "baseline", NULL);
        }
    }
""",
    )
)

for i, (old, new) in enumerate(R):
    n = src.count(old)
    if n != 1:
        sys.exit(f"Replacement {i} matched {n} times, expected 1")
    src = src.replace(old, new)

open(PATH, "w", encoding="utf-8").write(src)
print("All changes applied")
