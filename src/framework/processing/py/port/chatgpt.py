"""
DDP extract ChatGPT module
"""
from pathlib import Path
from typing import Tuple
import logging
import zipfile

import pandas as pd
import numpy as np

import port.unzipddp as unzipddp
import port.helpers as helpers

from port.validate import (
    DDPCategory,
    Language,
    DDPFiletype,
    ValidateInput,
    StatusCode,
)

logger = logging.getLogger(__name__)

DDP_CATEGORIES = [
    DDPCategory(
        id="json",
        ddp_filetype=DDPFiletype.JSON,
        language=Language.EN,
        known_files=["chat.html", "conversations.json", "message_feedback.json", "model_comparisons.json", "user.json"]
    )
]

STATUS_CODES = [
    StatusCode(id=0, description="Valid zip", message="Valid zip"),
    StatusCode(id=1, description="Bad zipfile", message="Bad zipfile"),
]


def validate_zip(zfile: Path) -> ValidateInput:
    """
    Make sure you always set a status code
    """

    validate = ValidateInput(STATUS_CODES, DDP_CATEGORIES)

    try:
        paths = []
        with zipfile.ZipFile(zfile, "r") as zf:
            for f in zf.namelist():
                p = Path(f)
                if p.suffix in (".html", ".json"):
                    logger.debug("Found: %s in zip", p.name)
                    paths.append(p.name)

        if validate.infer_ddp_category(paths):
            validate.set_status_code_by_id(0)
        else:
            validate.set_status_code_by_id(1)
    except zipfile.BadZipFile:
        validate.set_status_code_by_id(1)

    return validate



def conversations_to_df(chatgpt_zip: str)  -> pd.DataFrame:

    b = unzipddp.extract_file_from_zip(chatgpt_zip, "conversations.json")
    conversations = unzipddp.read_json_from_bytes(b)

    datapoints = []
    out = pd.DataFrame()

    try:
        for conversation in conversations:
            title = conversation["title"]
            for _, turn in conversation["mapping"].items():

                denested_d = helpers.dict_denester(turn)
                is_hidden = helpers.find_item(denested_d, "is_visually_hidden_from_conversation")
                if is_hidden != "True":
                    role = helpers.find_item(denested_d, "role")
                    message = "".join(helpers.find_items(denested_d, "part"))
                    model = helpers.find_item(denested_d, "-model_slug")
                    time = helpers.convert_unix_timestamp(helpers.find_item(denested_d, "create_time"))

                    datapoint = {
                        "conversation title": title,
                        "role": role,
                        "message": message,
                        "model": model,
                        "time": time,
                    }
                    if role != "":
                        datapoints.append(datapoint)

        out = pd.DataFrame(datapoints)

    except Exception as e:
        logger.error("Data extraction error: %s", e)
        
    return out



def select_random_qa(chatgpt_zip: str)  -> Tuple[str, str]:
    """
    The extra effort is made here to make sure the answers is actually a follow up of the question 
    and to make sure the question is the first in the conversation
    """

    b = unzipddp.extract_file_from_zip(chatgpt_zip, "conversations.json")
    conversations = unzipddp.read_json_from_bytes(b)

    datapoints = []
    question = ""
    answer = ""
    try:
        for conversation in conversations:
            title = conversation["title"]
            for _, turn in conversation["mapping"].items():

                denested_d = helpers.dict_denester(turn)
                is_hidden = helpers.find_item(denested_d, "is_visually_hidden_from_conversation")
                if is_hidden != "True":
                    role = helpers.find_item(denested_d, "role")
                    message = "".join(helpers.find_items(denested_d, "part"))
                    id = helpers.find_item(denested_d, "id")
                    child = helpers.find_item(denested_d, "children-0")
                    parent = helpers.find_item(denested_d, "parent")

                    datapoint = {
                        "conversation title": title,
                        "role": role,
                        "message": message,
                        "id": id,
                        "child": child,
                        "parent": parent,
                    }
                    if role != "":
                        datapoints.append(datapoint)

        df = pd.DataFrame(datapoints)
        print(df)

        # conversation selection criterion
        no_parents = ~df["id"].isin(df["child"]) # Indicates the start of a convo: i.e. an message is no ones child
        is_user = df["role"] == "user"           # The role should be user: ai cannot start
        condition = no_parents & is_user 

        ids = df["id"][condition].tolist()
        np.random.shuffle(ids)

        # check all suitable id's if for some reason a mistake happens check the next id
        for id in ids:
            ql = df["message"][df["id"] == id].tolist()
            al = df["message"][df["parent"] == id].tolist()
            if (
                len(ql) == 1 and 
                len(al) == 1 and 
                ql[0] != "" and 
                al[0] != ""
            ):
                question = ql[0]
                answer = al[0]
                break

    except Exception as e:
        logger.error("Data extraction error: %s", e)
        
    return question, answer




