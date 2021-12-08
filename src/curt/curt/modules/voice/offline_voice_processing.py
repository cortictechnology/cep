""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import deepspeech
import base64
import numpy as np
from curt.modules.voice.base_voice_processing import BaseVoiceProcessing

MODEL_FILE = "/opt/deepspeech-models/deepspeech-0.9.1-models.tflite"
SCORE_FILE = "/opt/deepspeech-models/deepspeech-0.9.1-models.scorer"


class OfflineVoiceProcessing(BaseVoiceProcessing):
    def __init__(self):
        super().__init__()
        self.model = deepspeech.Model(MODEL_FILE)
        self.model.enableExternalScorer(SCORE_FILE)

    def config_module(self, params):
        pass

    def run_inference(self, input_data):
        text = ""
        if input_data[0] is not None:
            content = base64.b64decode(input_data[0])
            if content != b"":
                print("Got speech bytes for processing")
                audio_frames = np.frombuffer(content, np.int16)
                stream_context = self.model.createStream()
                # for audio_frame in audio_frames:
                stream_context.feedAudioContent(audio_frames)
                text = stream_context.finishStream()
                print("Returning text:", text)
            else:
                return ""
        else:
            return ""
        return text
