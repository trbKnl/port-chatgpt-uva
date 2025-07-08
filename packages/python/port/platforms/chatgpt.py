"""
ChatGPT

This module provides an example flow of a ChatGPT data donation study

Assumptions:
It handles DDPs in the english language with filetype JSON.
"""
import logging
from typing import Tuple

import pandas as pd
import numpy as np

import port.api.props as props
import port.api.d3i_props as d3i_props
import port.helpers.extraction_helpers as eh
import port.helpers.validate as validate
from port.platforms.flow_builder import FlowBuilder

from port.helpers.validate import (
    DDPCategory,
    DDPFiletype,
    Language,
)

logger = logging.getLogger(__name__)

DDP_CATEGORIES = [
    DDPCategory(
        id="json",
        ddp_filetype=DDPFiletype.JSON,
        language=Language.EN,
        known_files=[
            "chat.html", 
            "conversations.json",
            "message_feedback.json",
            "model_comparisons.json",
            "user.json"
        ]
    )
]


def conversations_to_df(chatgpt_zip: str)  -> pd.DataFrame:
    b = eh.extract_file_from_zip(chatgpt_zip, "conversations.json")
    conversations = eh.read_json_from_bytes(b)

    datapoints = []
    out = pd.DataFrame()

    try:
        for conversation in conversations:
            title = conversation["title"]
            for _, turn in conversation["mapping"].items():

                denested_d = eh.dict_denester(turn)
                is_hidden = eh.find_item(denested_d, "is_visually_hidden_from_conversation")
                if is_hidden != "True":
                    role = eh.find_item(denested_d, "role")
                    message = "".join(eh.find_items(denested_d, "part"))
                    model = eh.find_item(denested_d, "-model_slug")
                    time = eh.epoch_to_iso(eh.find_item(denested_d, "create_time"))

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



def extraction(chatgpt_zip: str) -> list[d3i_props.PropsUIPromptConsentFormTableViz]:
    """
    Add your table definitions below in the list
    """
    tables = [
        d3i_props.PropsUIPromptConsentFormTableViz(
            id="chatgpt_conversations",
            data_frame=conversations_to_df(chatgpt_zip),
            title=props.Translatable({
                "en": "Your conversations with ChatGPT",
                "nl": "Uw gesprekken met ChatGPT"
            }),
            description=props.Translatable({
                "en": "In this table you find your conversations with ChatGPT sorted by time. Below, you find a wordcloud, where the size of the words represents how frequent these words have been used in the conversations.", 
                "nl": "In this table you find your conversations with ChatGPT sorted by time. Below, you find a wordcloud, where the size of the words represents how frequent these words have been used in the conversations.", 
            }),
            visualizations=[
                {
                    "title": {
                        "en": "Your messages in a wordcloud", 
                        "nl": "Your messages in a wordcloud"
                    },
                    "type": "wordcloud",
                    "textColumn": "message",
                    "tokenize": True,
                }
            ]
        ),
    ]

    tables_to_render = [table for table in tables if not table.data_frame.empty]

    return tables_to_render


def select_random_qa(chatgpt_zip: str)  -> Tuple[str, str]:
    """
    The extra effort is made here to make sure the answers is actually a follow up of the question 
    and to make sure the question is the first in the conversation
    """

    b = eh.extract_file_from_zip(chatgpt_zip, "conversations.json")
    conversations = eh.read_json_from_bytes(b)

    datapoints = []
    question = ""
    answer = ""
    try:
        for conversation in conversations:
            title = conversation["title"]
            for _, turn in conversation["mapping"].items():

                denested_d = eh.dict_denester(turn)
                is_hidden = eh.find_item(denested_d, "is_visually_hidden_from_conversation")
                if is_hidden != "True":
                    role = eh.find_item(denested_d, "role")
                    message = "".join(eh.find_items(denested_d, "part"))
                    id = eh.find_item(denested_d, "id")
                    child = eh.find_item(denested_d, "children-0")
                    parent = eh.find_item(denested_d, "parent")

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


# Random question questionnaire

Q1 = props.Translatable(
    {
        "en": "To what extent do you trust the answer provided by ChatGPT?",
        "nl": "In hoeverre vertrouwt u het antwoord van ChatGPT?"
    })
Q1_CHOICES = [
    props.Translatable(
        {
            "en": "1. I do not trust it at all", 
            "nl": "1. Ik vertrouw het helemaal niet"
        }),
    props.Translatable(
        {
            "en": "2", 
             "nl": "2"
        }),
    props.Translatable(
        {
            "en": "3", 
            "nl": "3"
        }),
    props.Translatable(
        {
            "en": "4",
             "nl": "4"
         }),
    props.Translatable({
        "en": "5. I trust it completely", 
        "nl": "5. Ik vertrouw het volledig"
    })
]


#def render_questionnaire(question: str, answer: str):
#    questions = [
#        props.PropsUIQuestionMultipleChoice(question=Q1, id=1, choices=Q1_CHOICES),
#    ]
#
#    description = props.Translatable(
#        {
#            "en": "Below you can find the start of a conversation you had with ChatGPT. We would like to ask you a question about it.",
#            "nl": "Hieronder vind u het begin van een gesprek dat u heeft gehad met ChatGPT. We willen u daar een vraag over stellen."
#        })
#    header = props.PropsUIHeader(props.Translatable({"en": "Questionnaire", "nl": "Vragenlijst"}))
#    body = props.PropsUIPromptQuestionnaire(
#        questions=questions, 
#        description=description,
#        questionToChatgpt=question,
#        answerFromChatgpt=answer,
#    )
#    footer = props.PropsUIFooter()
#
#    page = props.PropsUIPageDonation("ASD", header, body, footer)
#    return CommandUIRender(page)


def generate_questionnaire(question: str, answer: str) -> d3i_props.PropsUIPromptQuestionnaire:
    """
    Administer a basic questionnaire in Port.

    This function generates a prompt which can be rendered with render_page().
    The questionnaire demonstrates all currently implemented question types.
    In the current implementation, all questions are optional.

    You can build in logic by:
    - Chaining questionnaires together
    - Using extracted data in your questionnaires

    Usage:
        prompt = generate_questionnaire()
        results = yield render_page(header_text, prompt)
        
    The results.value contains a JSON string with question answers that 
    can then be donated with donate().
    """

    questionnaire_description = props.Translatable(
        {
            "en": "Below you can find the start of a conversation you had with ChatGPT. We would like to ask you a question about it.",
            "nl": "Hieronder vind u het begin van een gesprek dat u heeft gehad met ChatGPT. We willen u daar een vraag over stellen."
    })


    multiple_choice_question = d3i_props.PropsUIQuestionMultipleChoice(
        id=1,
        question=Q1,
        choices=Q1_CHOICES,
    )

    return d3i_props.PropsUIPromptQuestionnaire(
        description=questionnaire_description,
        questions=[
            multiple_choice_question,
        ],
        questionToChatgpt=question,
        answerFromChatgpt=answer,
    )


class ChatGPTFlow(FlowBuilder):
    def __init__(self, session_id: int):
        super().__init__(session_id, "ChatGPT")
        
    def validate_file(self, file):
        return validate.validate_zip(DDP_CATEGORIES, file)
        
    def extract_data(self, file_value, validation):
        return extraction(file_value)


def process(session_id):
    flow = ChatGPTFlow(session_id)
    return flow.start_flow()
