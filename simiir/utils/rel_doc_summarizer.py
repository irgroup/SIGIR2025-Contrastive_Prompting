from simiir.user.query_generators.base import BaseQueryGenerator
from simiir.user.utils.langchain_wrapper import LangChainWrapper

from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

import logging

log = logging.getLogger('query_generators.basic_llm_generator')

class LangChainDocumentSummarizer(BaseQueryGenerator):
    """
    Takes the BasicQueryGenerator and generates a list of queries based upon a topic description
    using an LLM to create the list of queries.

    Does not use any information outside of the topic. 
    """
    def __init__(self,user_context=None,stopword_file=None, provider='ollama',model='llama3.3',temperature=1.0,verbose=False):
        super(LangChainDocumentSummarizer, self).__init__(stopword_file, user_context, allow_similar=True)
 
        prompt_template = """
        Below you get the content of all the relevant documents that were found separated by newlines. Please create a brief summary of the knowledge that you gained from the content.

        {summarized_documents}
        """
        self._template = prompt_template + """\n\n{format_instructions}\n"""
        log.debug(self._template)
        
        self._result_schema = [ResponseSchema(
            name="summary",
            description=f"Generate a summary of the relevant documents, that were found yet",
            type="string"
            )]
        
        self._output_parser = StructuredOutputParser.from_response_schemas(self._result_schema)

        format_instructions = self._output_parser.get_format_instructions()
        log.debug(f'init(): {format_instructions}')
        self._prompt = PromptTemplate(
            template=self._template,
            input_variables=["summarized_documents"],
            partial_variables={"format_instructions": format_instructions})
        log.debug(f"init(): {self._prompt}")
        
        self._llm = LangChainWrapper(self._prompt, provider, model, temperature, verbose)
    
    def generate_summary_string(self, text_to_summarize):
        """
        Given a user context object, produces a list of query terms that could be issued by the simulated agent
        using only the topic.
        """

        log.debug("text_to_summarize: " + text_to_summarize)
        log.debug('generate_query_list(before): Langchain Sum ' + self._prompt.format(summarized_documents=text_to_summarize))    
        out = self._llm.generate_response(self._output_parser,{ 'summarized_documents': text_to_summarize},self._result_schema)
       
        return out["summary"]