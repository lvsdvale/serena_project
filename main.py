"""this file implements AI agent pipeline"""

import json
import os
import time

from llm_interactions.config import *
from llm_interactions.prompt_templates.user_interaction_template import \
    user_interaction_prompt
from llm_interactions.tools.get_compartment_stock_tool import \
    get_compartment_stock_by_device
from llm_interactions.tools.get_diagnoses_tool import get_diagnoses_by_device
from llm_interactions.tools.get_medication_names_tool import get_medication
from llm_interactions.tools.get_prescripiton_tool import \
    get_prescriptions_by_device
from llm_interactions.tools.log_interaction_tool import log_interaction
from llm_interactions.tools.update_compartment_stock_amout_tool import \
    update_compartment_stock
from medicine_recognizer.detection_pipeline import DetectionPipeline
from utils import (computer_vision_pipeline, dispenser_pipeline,
                   extract_quantity_from_dose, get_stock_ids_by_name,
                   hash_option)
from voice_decoder.voice_decoder import VoiceDecoder

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


def run_serena_assistent(database_url: str, device_id: str):
    decoder = VoiceDecoder(language="pt-BR", wake_word="Serena")
    while True:
        # query -> verificar horario where data < datetime now
        if decoder.listen_for_wake_word():
            command = decoder.audio_to_string()
            while not command.strip():
                decoder.string_to_speech("Desculpe, não entendi. Pode repetir?")
                command = decoder.audio_to_string()
            user_interaction_agent = user_interaction_prompt | llm
            diagnoses = get_diagnoses_by_device(
                {"database_url": database_url, "device_id": device_id}
            )
            prescriptions = get_prescriptions_by_device(
                {"database_url": database_url, "device_id": device_id}
            )
            user_interaction_inputs = dict()
            user_interaction_inputs["command"] = command
            user_interaction_inputs["diagnoses"] = diagnoses
            user_interaction_inputs["prescriptions"] = prescriptions
            response = user_interaction_agent.invoke(user_interaction_inputs)
            parsed_response = json.loads(response)
            log_interaction(
                {
                    "device_id": device_id,
                    "database_url": database_url,
                    "symptom": parsed_response["sintoma"],
                    "suggestion": parsed_response["motivo"],
                }
            )
            decoder.string_to_speech(
                f"{parsed_response['motivo']},você gostaria de tomar via dispenser ou utilizando a câmera"
            )
            option = decoder.audio_to_string()
            hashed_option = hash_option(option)
            while hashed_option is None:
                decoder.string_to_speech(
                    "opção selecionada invalida, por favor fale novamente e escolha entre câmera ou dispenser"
                )
                option = decoder.audio_to_string()
                hashed_option = hash_option(option)

            if hashed_option == 1:
                medicine_name = parsed_response["medicamento_recomendado"]
                quantity_used = extract_quantity_from_dose(parsed_response["dose"])
                quantity_used_list = list()
                quantity_used_list.append(quantity_used)
                dispenser_pipeline(
                    database_url,
                    device_id,
                    medicine_names=medicine_name,
                    quantity_used_list=quantity_used_list,
                    decoder=decoder,
                )
            if hashed_option == 2:
                medicine_names = list()
                medicine_names.append(parsed_response["medicamento_recomendado"])
                computer_vision_pipeline(database_url, medicine_names, decoder)


def test_serena_assistent(database_url: str, device_id: str):
    decoder = VoiceDecoder(language="pt-BR", wake_word="Serena")
    while True:
        if decoder.listen_for_wake_word():
            command = decoder.audio_to_string()
            print(command)
            while not command.strip():
                decoder.string_to_speech("Desculpe, não entendi. Pode repetir?")
                command = decoder.audio_to_string()
            user_interaction_agent = user_interaction_prompt | llm
            diagnoses = get_diagnoses_by_device(
                {"database_url": database_url, "device_id": device_id}
            )
            prescriptions = get_prescriptions_by_device(
                {"database_url": database_url, "device_id": device_id}
            )
            user_interaction_inputs = dict()
            user_interaction_inputs["command"] = command
            user_interaction_inputs["diagnoses"] = diagnoses
            user_interaction_inputs["prescriptions"] = prescriptions
            response = user_interaction_agent.invoke(user_interaction_inputs)
            parsed_response = json.loads(response)
            log_interaction(
                {
                    "device_id": device_id,
                    "database_url": database_url,
                    "symptom": parsed_response["sintoma"],
                    "suggestion": parsed_response["motivo"],
                }
            )
            decoder.string_to_speech(
                f"{parsed_response['motivo']},você gostaria de tomar via dispenser ou utilizando a câmera"
            )
            option = decoder.audio_to_string()
            hashed_option = hash_option(option)
            while hashed_option is None:
                decoder.string_to_speech(
                    "opção selecionada invalida, por favor fale novamente e escolha entre câmera ou dispenser"
                )
                option = decoder.audio_to_string()
                hashed_option = hash_option(option)

            if hashed_option == 1:
                medicine_name = parsed_response["medicamento_recomendado"]
                quantity_used = extract_quantity_from_dose(parsed_response["dose"])
                quantity_used_list = list()
                quantity_used_list.append(quantity_used)
                dispenser_pipeline(
                    database_url,
                    device_id,
                    medicine_names=medicine_name,
                    quantity_used_list=quantity_used_list,
                    decoder=decoder,
                )
            if hashed_option == 2:
                medicine_names = list()
                medicine_names.append(parsed_response["medicamento_recomendado"])
                computer_vision_pipeline(database_url, medicine_names, decoder)


test_serena_assistent(DATABASE_URL, device_id)
