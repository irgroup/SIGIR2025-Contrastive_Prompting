from simiir.user.loggers import Actions
from simiir.user.loggers.base import BaseLogger
import progressbar

class FixedCostLogger(BaseLogger):
    """
    A fixed cost logger - where interactions have a different - but constant - cost.
    Not the most realistic way of representing interaction costs, but as a start, it is pretty good.
    Costs can be defined in the constructor - and time_limit is the maximum amount of time a search session can be carried out for.
    A session ends when the accumulated costs reaches (or exceeds) the specified time limit. If a user initiates an activity which pushes them over the limit, they can complete that action - but nothing more.
    """
    def __init__(self,
                 output_controller,
                 user_context,
                 time_limit=300,
                 query_cost=10,
                 document_cost=20,
                 snippet_cost=3,
                 serp_results_cost=5,
                 mark_document_cost=3):
        """
        Instantiates the BaseLogger class and sets up additional instance variables for the FixedCostLogger.
        Note that this does not enforce the time limit...
        """
        super(FixedCostLogger, self).__init__(output_controller, user_context)
        
        #  Series of costs (in seconds) for each interaction that the user can perform; these are fixed.
        self._query_cost = query_cost
        self._document_cost = document_cost
        self._snippet_cost = snippet_cost
        self._serp_results_cost = serp_results_cost
        self._mark_document_cost = mark_document_cost
        
        self._total_time = 0  # An elapsed counter of the number of seconds a user has been interacting for.
        self._time_limit = time_limit  # The maximum time that a user can search for in a session.
        
        self._last_query_time = 0  # The last time a query was issued, from the start of the session, measured in seconds.
        self._last_marked_time = 0  # The last time a document was marked, from the start of the session, measured in seconds.
        self._last_relevant_snippet_time = 0  # The last time a snippet was considered relevant, from the start of the session (seconds).
        widgets = [' [',
         progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
         '] ',
           progressbar.Bar('*'),' (',
           progressbar.ETA(), ') ',
          ]
        
        self._bar = progressbar.ProgressBar(maxval=self._time_limit, widgets=widgets)
        self._bar.start()


    def get_last_query_time(self):
        return self._last_query_time
    
    def get_last_interaction_time(self):
        return self._total_time
    
    def get_last_marked_time(self):
        return self._last_marked_time
    
    def get_last_relevant_snippet_time(self):
        return self._last_relevant_snippet_time
    
    def get_progress(self):
        """
        Concrete implementation of the abstract get_progress() method.
        Returns a value between 0 and 1 representing how far through the current simulation the user is.
        """
        if self._total_time < self._time_limit:
            self._bar.update(self._total_time)
        
        return self._total_time / float(self._time_limit)
    
    def is_finished(self):
        """
        Concrete implementation of the is_finished() method from the BaseLogger.
        Returns True if the user has reached their search "allowance".
        """
        if self._total_time < self._time_limit:
            self._bar.update(self._total_time)
        # Include the super().is_finished() call to determine if there are any queries left to process.
        return (not (self._total_time < self._time_limit)) or super(FixedCostLogger, self).is_finished()
    
    def _report(self, action, **kwargs):
        """
        Re-implementation of the _report() method from BaseLogger.
        Includes additional details in the message such as the total elapsed time, and maximum time available to the user after the action has been processed.
        """
        log_entry_mapper = {
            Actions.START  : "START",
            Actions.STOP   : "STOP",
            Actions.UNKNOWN: "UNKNOWN",
            Actions.QUERY  : kwargs.get('query'),
            Actions.SERP   : kwargs.get('status'),
            Actions.SNIPPET: "{0} {1}".format(kwargs.get('status'), kwargs.get('doc_id')),
            Actions.DOC    : "{0} {1}".format(kwargs.get('status'), kwargs.get('doc_id')),
            Actions.MARK   : "{0} {1}".format(kwargs.get('status'), kwargs.get('doc_id')),
        }
        
        base = super(FixedCostLogger, self)._report(action, **kwargs)
        self._output_controller.log("{0}{1} {2} {3}".format(base, self._time_limit, self._total_time, log_entry_mapper[action]))
    
    def _log_query(self, **kwargs):
        """
        Concrete implementation of the _log_query() method from the BaseLogger.
        Increments the __total_time counter with the cost of issuing a query.
        """
        self._total_time = self._total_time + self._query_cost
        self._last_query_time = self._total_time
        self._last_marked_time = self._total_time  # Reset the marked time to zero at the start of the query
        self._report(Actions.QUERY, **kwargs)
    
    def _log_serp(self, **kwargs):
        """
        Concrete implementation of the _log_serp() method from the BaseLogger.
        Increments the __total_time counter with the cost of examining a SERP.
        """
        self._total_time = self._total_time + self._serp_results_cost
        self._report(Actions.SERP, **kwargs)
    
    def _log_snippet(self, **kwargs):
        """
        A concrete implementation of the log_snippet() method from the BaseLogger.
        Increments __total_time to reflect the cost of examining a snippet.
        """
        self._total_time = self._total_time + self._snippet_cost
        kwargs['doc_id'] = kwargs['snippet'].doc_id
        
        self._report(Actions.SNIPPET, **kwargs)
        
        if kwargs['snippet'].judgment > 0:
            self._last_relevant_snippet_time = self._total_time
    
    def _log_assess(self, **kwargs):
        """
        Concrete implementation for assessing a document at a fixed cost.
        """
        self._total_time = self._total_time + self._document_cost
        self._report(Actions.DOC, **kwargs)
    
    def _log_mark_document(self, **kwargs):
        """
        Concrete implementation for marking a document as relevant as a fixed cost.
        """
        self._total_time = self._total_time + self._mark_document_cost
        self._last_marked_time = self._total_time
        
        self._report(Actions.MARK, **kwargs)