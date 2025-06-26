"""this file implements AI agent pipeline"""

import json
import os
import time

from api_consumer import SerenaAPIClient
from dispenser_controller.dispenser import MedicineDispenser
from llm_interactions.config import *
from llm_interactions.prompt_templates.user_interaction_template import \
    user_interaction_prompt
from medicine_recognizer.detection_pipeline import DetectionPipeline
from utils import (computer_vision_pipeline, dispenser_pipeline,
                   extract_quantity_from_dose, get_stock_ids_by_name,
                   hash_option, parse_to_json)
from voice_decoder.voice_decoder import VoiceDecoder


def run_serena_assistent(device_id: str):
    step_pin = 17
    dir_pin = 27
    relay_pin = 22
    dispenser_controller = MedicineDispenser(step_pin, dir_pin, relay_pin)
    decoder = VoiceDecoder(language="pt-BR", wake_word="Serena")
    while True:
        if decoder.listen_for_wake_word():
            command = decoder.audio_to_string()
            print(command)
            while not command.strip():
                decoder.string_to_speech("Desculpe, não entendi. Pode repetir?")
                command = decoder.audio_to_string()
            user_interaction_agent = user_interaction_prompt | llm
            client = SerenaAPIClient(email=api_email, password=api_password)
            prescriptions = client.get_enriched_prescriptions(device_id)
            user_interaction_inputs = dict()
            user_interaction_inputs["command"] = command
            user_interaction_inputs["prescriptions"] = prescriptions
            response = user_interaction_agent.invoke(user_interaction_inputs)
            print(response.content)
            parsed_response = parse_to_json(response.content)
            if parsed_response["medicamento_recomendado"].lower() == "nenhum":
                decoder.string_to_speech(f"{parsed_response['sugestão']}")
                continue
            senior_id = client.get_senior_id_by_device(device_id)["senior_id"]
            symptom_name = parsed_response["sintoma"]
            client.create_symptom_by_device(
                device_id=device_id,
                senior_id=senior_id,
                symptom_name=symptom_name,
                description=parsed_response["sugestão"],
                pain_level=1,
            )
            decoder.string_to_speech(
                f"{parsed_response['sugestão']},você gostaria de tomar o medicamento agora ?"
            )
            option = decoder.audio_to_string()
            while not option.strip():
                decoder.string_to_speech("Desculpe, não entendi. Pode repetir?")
                option = decoder.audio_to_string()
            if "não" in option.lower():
                continue
            decoder.string_to_speech(
                f"você gostaria de tomar o medicamento pela camêra ou pelo dispenser?"
            )
            medicine_list = client.get_medication_list()
            medicine_list = [medicine["name"] for medicine in medicine_list]
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
                device_compartments = client.get_full_dispenser_status(device_id)
                compartments_update_list = dispenser_pipeline(
                    device_compartments=device_compartments,
                    medicine_names=medicine_name,
                    medication_list=medicine_list,
                    quantity_used_list=quantity_used_list,
                    decoder=decoder,
                    dispenser_controller=dispenser_controller,
                )
                print(compartments_update_list)
                for compartment_to_update in compartments_update_list:
                    client.update_compartment_amount(
                        compartment_to_update["compartment_id"],
                        compartment_to_update["medication_id"],
                        compartment_to_update["quantity"],
                    )

            if hashed_option == 2:
                medicine_names = list()
                medicine_names.append(parsed_response["medicamento_recomendado"])
                computer_vision_pipeline(medicine_names, medicine_list, decoder)


run_serena_assistent(device_id)
