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
from voice_decoder.voice_decoder import VoiceDecoder

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


def run_serena_assistent(database_url: str, device_id: str):
    decoder = VoiceDecoder(language="pt-BR", wake_word="Serena")
    while True:
        # query -> verificar horario where data < datetime now
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
                f"{parsed_response['motivo']},você gostaria de tomar via dispenser ou utilizando a visão computacional"
            )
            option = decoder.audio_to_string()
            if "dispenser" in option:
                pass  # do stuff
            if "visao computacional" in option:
                medication_list = [
                    medication["medication_name"]
                    for medication in get_medication({"database_url": database_url})
                ]
                medicine_confirmation = False
                detection_pipeline = DetectionPipeline()
                while not medicine_confirmation:
                    detection_response = detection_pipeline.run_detection()
                    medication_found = set(detection_response.split(" ")) & set(
                        medication_list
                    )
                    if medication_found:
                        if (
                            parsed_response["medicamento_recomendado"]
                            in detection_response
                        ):
                            medicine_confirmation = True
                    else:
                        decoder.string_to_speech(
                            f"Esse não é o remédio correto, o remédio correto é {parsed_response['medicamento_recomendado']}, você mostrou o {medication_found[0]}"
                        )
                decoder.string_to_speech("Esse é o remédio certo pode tomar")


print(llm)


def test_serena_assistent(
    database_url: str, device_id: str, command="estou com dor de cabeça"
):
    decoder = VoiceDecoder(language="pt-BR", wake_word="Serena")
    user_interaction_agent = user_interaction_prompt | llm
    diagnoses = get_diagnoses_by_device(
        {"database_url": database_url, "device_id": device_id}
    )
    prescriptions = get_prescriptions_by_device(
        {"database_url": database_url, "device_id": device_id}
    )
    user_interaction_inputs = dict()
    user_interaction_inputs["command"] = command
    user_interaction_inputs["diagnoses"] = (diagnoses,)
    user_interaction_inputs["prescriptions"] = (prescriptions,)

    response = user_interaction_agent.invoke(user_interaction_inputs)
    parsed_response = json.loads(response)
    print(type(parsed_response))
    print(parsed_response.keys())
    log_interaction(
        {
            "device_id": device_id,
            "database_url": database_url,
            "symptom": parsed_response["sintoma"],
            "suggestion": parsed_response["motivo"],
        }
    )
    decoder.string_to_speech(
        f"{parsed_response['motivo']},você gostaria de tomar via dispenser ou utilizando a visão computacional"
    )


test_serena_assistent(DATABASE_URL, device_id)
