from simiir.user.query_generators.base import BaseQueryGenerator
from simiir.user.utils.langchain_wrapper import LangChainWrapper

from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

import logging



log = logging.getLogger('query_generators.langchain_based_on_context')

class LangChainQueryGenerator_based_on_TREC_Title(BaseQueryGenerator):
    """
    Takes the BasicQueryGenerator and generates a list of queries based upon a topic description
    using an LLM to create the list of queries.

    Does not use any information outside of the topic. 
    """
    def __init__(self, stopword_file, prompt_file, n=3,provider='ollama',model='mistral',temperature=1.0,verbose=False, background_file=[]):
        super(LangChainQueryGenerator_with_minimal_Context, self).__init__(stopword_file, background_file=background_file, allow_similar=False)
        prompt_template = ""
        with open(prompt_file,'r') as prompt:
            prompt_template = prompt.read()
        
        self._template = prompt_template + """\n\n{format_instructions}\n"""
        log.debug(self._template)
        
        self._result_schema = [ResponseSchema(
            name="queries",
            description=f"Generate an array of 30 possible queries for the topic of less than or equal to {n} search terms ordered by likelihood of success.",
            type="list"
            )]
        
        self._output_parser = StructuredOutputParser.from_response_schemas(self._result_schema)

        format_instructions = self._output_parser.get_format_instructions()
        self._prompt = PromptTemplate(
            template=self._template,
            input_variables=["topic_title"],
            partial_variables={"format_instructions": format_instructions})
                
        self._llm = LangChainWrapper(self._prompt, provider, model, temperature, verbose)
    
    def generate_query_list(self, user_context):
        """
        Given a user context object, produces a list of query terms that could be issued by the simulated agent
        using only the topic.
        """

        topic_title = user_context.topic.title

        out = self._llm.generate_response(self._output_parser,{ 'topic_title': topic_title},self._result_schema)
        queries = out.get('queries',[])
        return [(str(query), len(queries) - idx) for idx, query in enumerate(queries)]