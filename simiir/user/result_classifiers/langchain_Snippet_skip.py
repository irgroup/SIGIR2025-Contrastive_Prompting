#Authors: Adam Roegiest and Leif Azzopardi
#Date:   2024-04-05

from simiir.user.result_classifiers.base import BaseTextClassifier
from simiir.user.utils.langchain_wrapper import LangChainWrapper
from simiir.utils.tidy import clean_html
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

import logging
log = logging.getLogger('result_classifier.LangChainTextClassifier')


snippet_response_schema = [
            ResponseSchema(name="relevant", description="Is this result snippet relevant to the topic? True or False.", type="boolean"),
            ResponseSchema(name="topic", description="Is this result snippet about the subject matter in the topic description? True or False.", type="boolean")
            ]

document_response_schema = [
            ResponseSchema(name="relevant", description="Is this document relevant to the topic? True or False.", type="boolean"),
            ResponseSchema(name="topic", description="Is this document about the subject matter in the topic? True or False.", type="boolean"),
            ResponseSchema(name="explain", description="Summarize the information from the document that is relevant to the topic description and the criteria. Be specific and succint but mention all relevant entities.")
            ]

result_schema_dict = { "SnippetResponse":snippet_response_schema, "DocumentResponse":document_response_schema}

class LangChainTextClassifier_Snippet_default_true(BaseTextClassifier):
    """
    Represents the use of a LangChain-based LLM as a result classifier.
    Functions for both documents and snippets by setting an appropriate result-type.

    Prompts have four available variables to be used: the topic title ({topic_title}), the topic
    description ({topic_description}), the document (or snippet) title ({doc_title}), and 
    the document (or snippet) contents ({doc_content}).
    """
    def __init__(self, topic, user_context):
        """

        """
        super(LangChainTextClassifier_Snippet_default_true, self).__init__(topic, user_context)
        self.updating = False
       

    def is_relevant(self, document):
        """
        """
        return True
