import importlib
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


with mock.patch.object(sys, "argv", ["surroundsep"]):
    surroundsep = importlib.import_module("surroundsep")


class AudioStreamInfoTests(unittest.TestCase):
    def test_reads_first_audio_stream_as_json(self):
        probe_result = {
            "streams": [
                {
                    "codec_name": "pcm_f32le",
                    "sample_fmt": "flt",
                    "bits_per_sample": 32,
                }
            ]
        }

        with mock.patch.object(
            surroundsep.subprocess,
            "check_output",
            return_value=json.dumps(probe_result).encode(),
        ) as check_output:
            stream_info = surroundsep.get_audio_stream_info()

        self.assertEqual(stream_info, probe_result["streams"][0])
        command = check_output.call_args.args[0]
        self.assertIn("a:0", command)
        self.assertIn("json", command)

    def test_rejects_missing_audio_stream(self):
        with mock.patch.object(
            surroundsep.subprocess, "check_output", return_value=b'{"streams": []}'
        ):
            with self.assertRaisesRegex(ValueError, "did not return an audio stream"):
                surroundsep.get_audio_stream_info()


class Ortf3DTests(unittest.TestCase):
    def test_detects_the_official_channel_signature(self):
        self.assertTrue(
            surroundsep.is_ortf_3d_file(
                "Rain-L,R,Ls,Rs,Lh,Rh,Lsh,Rsh_Australia.wav"
            )
        )
        self.assertTrue(
            surroundsep.is_ortf_3d_file(
                "Rain-L,R,LS,RS,LH,RH,LSH,RSH_Australia.wav"
            )
        )

    def test_does_not_accept_a_different_channel_order(self):
        self.assertFalse(
            surroundsep.is_ortf_3d_file(
                "Rain-L,R,Lh,Rh,Ls,Rs,Lsh,Rsh_Australia.wav"
            )
        )

    def test_uses_ortf3d_name_marker(self):
        self.assertTrue(surroundsep.is_ortf_3d_file("Rain_Ortf3d.wav"))

    def test_auto_detects_the_exact_recording_as_ortf3d(self):
        recording = (
            "RAINGlas-L,R,Ls,Rs,Lh,Rh,Lsh,Rsh_Australia-Rain, Glass, "
            "Wind Driven Rain, Pelting Window Impact_Ortf3d.wav"
        )

        with mock.patch.multiple(
            surroundsep,
            create=True,
            INPUT_PATH=recording,
            FILE_EXTENSION=".wav",
            CHANNEL_LAYOUT_OVERRIDE="auto",
        ), mock.patch.object(
            surroundsep.subprocess,
            "check_output",
            side_effect=[b"8\n", b"unknown\n"],
        ):
            self.assertEqual(
                surroundsep.get_audio_channels_info(), (8, "ortf-3d")
            )

    def test_unknown_eight_channel_wav_is_not_silently_called_7_1(self):
        with mock.patch.multiple(
            surroundsep,
            create=True,
            INPUT_PATH="unlabelled.wav",
            FILE_EXTENSION=".wav",
            CHANNEL_LAYOUT_OVERRIDE="auto",
        ), mock.patch.object(
            surroundsep.subprocess,
            "check_output",
            side_effect=[b"8\n", b"unknown\n"],
        ):
            self.assertEqual(surroundsep.get_audio_channels_info(), (8, None))

    def test_keeps_an_embedded_standard_7_1_layout(self):
        with mock.patch.multiple(
            surroundsep,
            create=True,
            INPUT_PATH="standard.wav",
            FILE_EXTENSION=".wav",
            CHANNEL_LAYOUT_OVERRIDE="auto",
        ), mock.patch.object(
            surroundsep.subprocess,
            "check_output",
            side_effect=[b"8\n", b"7.1\n"],
        ):
            self.assertEqual(surroundsep.get_audio_channels_info(), (8, "7.1"))

    def test_explicit_ortf3d_layout_overrides_incorrect_7_1_metadata(self):
        with mock.patch.multiple(
            surroundsep,
            create=True,
            INPUT_PATH="renamed.wav",
            FILE_EXTENSION=".wav",
            CHANNEL_LAYOUT_OVERRIDE="ortf-3d",
        ), mock.patch.object(
            surroundsep.subprocess,
            "check_output",
            side_effect=[b"8\n", b"7.1\n"],
        ):
            self.assertEqual(
                surroundsep.get_audio_channels_info(), (8, "ortf-3d")
            )

    def test_split_maps_each_numeric_channel_to_the_official_name(self):
        with mock.patch.multiple(
            surroundsep,
            create=True,
            INPUT_PATH="recording.wav",
            OUTPUT_PATH="output",
            FILE_NAME="recording",
            CODEC="pcm_f32le",
        ), mock.patch.object(surroundsep.subprocess, "run") as run:
            surroundsep.split_ortf_3d_channels()

        command = run.call_args.args[0]
        filter_complex = command[command.index("-filter_complex") + 1]
        self.assertNotIn("7.1", filter_complex)
        for index in range(8):
            self.assertIn(f"pan=mono|c0=c{index}", filter_complex)

        output_names = [
            argument
            for argument in command
            if argument.endswith(".wav") and argument != "recording.wav"
        ]
        self.assertEqual(
            output_names,
            [
                f"output/recording/recording [{index} {channel}].wav"
                for index, channel in enumerate(
                    surroundsep.ORTF_3D_CHANNELS, start=1
                )
            ],
        )
        run.assert_called_once_with(command, check=True)


class BitDepthTests(unittest.TestCase):
    def get_bit_depth(self, stream_info):
        with redirect_stdout(io.StringIO()):
            return surroundsep.get_bit_depth(stream_info)

    def test_prefers_positive_raw_sample_depth(self):
        self.assertEqual(
            self.get_bit_depth(
                {"bits_per_raw_sample": "24", "bits_per_sample": 32}
            ),
            24,
        )

    def test_falls_back_to_sample_depth_when_raw_depth_is_unavailable(self):
        for raw_depth in ("N/A", None, 0):
            with self.subTest(raw_depth=raw_depth):
                self.assertEqual(
                    self.get_bit_depth(
                        {
                            "bits_per_raw_sample": raw_depth,
                            "bits_per_sample": 32,
                        }
                    ),
                    32,
                )

    def test_rejects_unusable_depth_fields(self):
        with self.assertRaisesRegex(ValueError, "Unable to determine"):
            self.get_bit_depth(
                {"bits_per_raw_sample": "N/A", "bits_per_sample": 0}
            )


class CodecTests(unittest.TestCase):
    def get_codec(self, bit_depth, stream_info=None):
        surroundsep.BIT_DEPTH = bit_depth
        with redirect_stdout(io.StringIO()):
            return surroundsep.get_codec(stream_info)

    def test_selects_integer_pcm_from_bit_depth(self):
        self.assertEqual(self.get_codec(16), "pcm_s16le")
        self.assertEqual(self.get_codec(24), "pcm_s24le")
        self.assertEqual(self.get_codec(32), "pcm_s32le")

    def test_preserves_32_bit_float_pcm(self):
        self.assertEqual(
            self.get_codec(32, {"codec_name": "pcm_f32le"}), "pcm_f32le"
        )


if __name__ == "__main__":
    unittest.main()
