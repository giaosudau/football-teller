from llama_index import SQLDatabase, GPTSQLStructStoreIndex, ServiceContext
from llama_index.indices.struct_store import SQLContextContainerBuilder

from config import get_sql_engine


class QA:
    def __init__(self, api):
        self.api = api
        sql_engine = get_sql_engine()
        sql_database = SQLDatabase(sql_engine)
        builder = SQLContextContainerBuilder(sql_database)
        context_builder = builder.build_context_container()
        service_context = ServiceContext.from_defaults(llm=api.llm)
        index = GPTSQLStructStoreIndex([],
                                       sql_database=sql_database,
                                       sql_context_container=context_builder,
                                       service_context=service_context)
        index.storage_context.persist()
        self.query_engine = index.as_query_engine()

    def ask(self, question):
        return self.query_engine.query(question)


