""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

from six.moves import queue
from google.cloud import speech
import google.oauth2
from curt.modules.voice.base_voice_processing import BaseVoiceProcessing
import numpy as np
import wave
import base64
import threading


class OnlineVoiceProcessing(BaseVoiceProcessing):
    def __init__(self):
        super().__init__()
        self.client = None
        self.config = None
        self.current_text = ""

    def config_module(self, params):
        account_credentials = params["account_crediential"]
        language = params["language"]
        sample_rate = params["sample_rate"]
        channel_count = params["channel_count"]
        credentials = (
            google.oauth2.service_account.Credentials.from_service_account_info(
                account_credentials
            )
        )
        self.client = speech.SpeechClient(credentials=credentials)
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language,
            audio_channel_count=channel_count,
        )
        print("Online account config finished")
        return True

    def cloud_request_thread(self, content):
        audio = speech.RecognitionAudio(content=content)
        operation = self.client.long_running_recognize(
            request={"config": self.config, "audio": audio}
        )
        response = operation.result(timeout=90)
        text = ""
        for result in response.results:
            text = result.alternatives[0].transcript
        self.current_text = text

    def run_inference(self, input_data):
        if self.client is not None:
            content = base64.b64decode(input_data[0])
            if content != b"":
                print("Got speech bytes for processing")
                # print(content)
                # print("******************Done printing content*******************")
                cloud_thread = threading.Thread(
                    target=self.cloud_request_thread, args=(content,), daemon=True
                )
                cloud_thread.start()
            else:
                text = ""
                if self.current_text != "":
                    text = self.current_text
                    self.current_text = ""
                    print("Returning text:", text)
                return text
        else:
            print("Online processing client is not configured.")
            return ""
