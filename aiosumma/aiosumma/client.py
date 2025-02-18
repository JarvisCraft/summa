import json
import os
import os.path
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

from aiogrpcclient import (
    BaseGrpcClient,
    expose,
)
from summa.proto import consumer_service_pb2 as consumer_service_pb
from summa.proto import index_service_pb2 as index_service_pb
from summa.proto import reflection_service_pb2 as reflection_service_pb
from summa.proto import search_service_pb2 as search_service_pb
from summa.proto.consumer_service_pb2_grpc import ConsumerApiStub
from summa.proto.index_service_pb2 import (  # noqa
    Asc,
    Desc,
)
from summa.proto.index_service_pb2_grpc import IndexApiStub
from summa.proto.reflection_service_pb2_grpc import ReflectionApiStub
from summa.proto.search_service_pb2_grpc import SearchApiStub


class SummaClient(BaseGrpcClient):
    stub_clses = {
        'consumer_api': ConsumerApiStub,
        'index_api': IndexApiStub,
        'reflection_api': ReflectionApiStub,
        'search_api': SearchApiStub,
    }

    @expose
    async def commit_index(
        self,
        index_name: str,
        request_id: str = None,
        session_id: str = None,
    ) -> index_service_pb.CommitIndexResponse:
        """
        Commit index asynchronously. A commit will be scheduled and be done eventually.
        Executing commit means stopping all consumption before commit and starting it again
        after.

        Args:
            index_name: index name
            request_id: request id
            session_id: session id
        Returns:
            Commit scheduling result
        """
        return await self.stubs['index_api'].commit_index(
            index_service_pb.CommitIndexRequest(
                index_name=index_name,
            ),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def create_consumer(
        self,
        index_name: str,
        consumer_name: str,
        bootstrap_servers: List[str],
        group_id: str,
        topics: List[str],
        threads: int = None,
        request_id: str = None,
        session_id: str = None,
    ) -> consumer_service_pb.CreateConsumerResponse:
        """
        Create consumer and corresponding topics in Kafka.
        The newly created consumer starts immediately after creation

        Args:
            index_name: index name
            consumer_name: consumer name that will be used for topic creation in Kafka too
            bootstrap_servers: list of bootstrap servers
            group_id: group_id for Kafka topic consumption
            topics: list of topics
            threads: number of threads to read topics and number of partitions in Kafka topic
            request_id: request id
            session_id: session id
        """
        return await self.stubs['consumer_api'].create_consumer(
            consumer_service_pb.CreateConsumerRequest(
                consumer_name=consumer_name,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                index_name=index_name,
                topics=topics,
                threads=threads,
            ),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def create_index(
        self,
        index_name: str,
        schema: str,
        primary_key: Optional[str] = None,
        default_fields: Optional[List[str]] = None,
        multi_fields: Optional[List[str]] = None,
        stop_words: Optional[List[str]] = None,
        compression: Optional[str] = None,
        writer_heap_size_bytes: Optional[int] = None,
        writer_threads: Optional[int] = None,
        autocommit_interval_ms: Optional[int] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        sort_by_field: Optional[Tuple] = None
    ) -> index_service_pb.CreateIndexResponse:
        """
        Create index

        Args:
            index_name: index name
            schema: Tantivy index schema
            primary_key: primary key is used during insertion to check duplicates
            default_fields: fields that are used to search by default
            stop_words: list of words that won't be parsed
            compression: Tantivy index compression
            writer_heap_size_bytes: Tantivy writer heap size in bytes, shared between all threads
            writer_threads: Tantivy writer threads
            autocommit_interval_ms: if true then there will be a separate thread committing index every nth milliseconds
                set by this parameter
            request_id: request id
            session_id: session id
            sort_by_field: (field_name, order)
        """
        if os.path.exists(schema):
            with open(schema, 'r') as f:
                schema = f.read()
        return await self.stubs['index_api'].create_index(
            index_service_pb.CreateIndexRequest(
                index_name=index_name,
                schema=schema,
                primary_key=primary_key,
                default_fields=default_fields,
                multi_fields=multi_fields,
                stop_words=stop_words,
                compression=compression,
                writer_heap_size_bytes=writer_heap_size_bytes,
                writer_threads=writer_threads,
                autocommit_interval_ms=autocommit_interval_ms,
                sort_by_field=index_service_pb.SortByField(
                    field=sort_by_field[0],
                    order=sort_by_field[1],
                ) if sort_by_field else None
            ),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def delete_consumer(
        self,
        index_name: str,
        consumer_name: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> consumer_service_pb.DeleteConsumerResponse:
        """
        Delete consumer by consumer name

        Args:
            index_name: index nam
            consumer_name: consumer name
            request_id: request id
            session_id: session id
        """
        return await self.stubs['consumer_api'].delete_consumer(
            consumer_service_pb.DeleteConsumerRequest(index_name=index_name, consumer_name=consumer_name),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def delete_index(
        self,
        index_name: str,
        cascade: bool = False,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.DeleteIndexResponse:
        """
        Delete index by index name

        Args:
            index_name: index name
            cascade: if set then delete both consumers and aliases too
            request_id: request id
            session_id: session id
        """
        return await self.stubs['index_api'].delete_index(
            index_service_pb.DeleteIndexRequest(index_name=index_name, cascade=cascade),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def get_consumer(
        self,
        consumer_name: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> consumer_service_pb.GetConsumerResponse:
        """
        Get consumer by name

        Args:
            consumer_name: consumer name
            request_id: request id
            session_id: session id
        Return:
            Consumer description
        """
        return await self.stubs['consumer_api'].get_consumer(
            consumer_service_pb.GetConsumerRequest(consumer_name=consumer_name),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def get_consumers(
        self,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> consumer_service_pb.GetConsumersResponse:
        """
        Get all consumers

        Args:
            request_id: request id
            session_id: session id
        Returns:
            Consumers list
        """
        return await self.stubs['consumer_api'].get_consumers(
            consumer_service_pb.GetConsumersRequest(),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def get_index(
        self,
        index_name: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.GetIndexResponse:
        """
        Index metadata by name

        Args:
            index_name: index name
            request_id: request id
            session_id: session id
        Returns:
            Index description
        """
        return await self.stubs['index_api'].get_index(
            index_service_pb.GetIndexRequest(index_name=index_name),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def get_indices(
        self,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.GetIndicesResponse:
        """
        All indices metadata

        Args:
            request_id: request id
            session_id: session id
        Returns:
            Indices list
        """
        return await self.stubs['index_api'].get_indices(
            index_service_pb.GetIndicesRequest(),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def get_indices_aliases(
        self,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.GetIndicesAliasesResponse:
        """
        Get all aliases for all indices

        Args:
            request_id: request id
            session_id: session id
        Returns:
            Aliases list
        """
        return await self.stubs['index_api'].get_indices_aliases(
            index_service_pb.GetIndexAliasesRequest(),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def index_document(
        self,
        index_name: str,
        document: Union[dict, bytes],
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.IndexDocumentResponse:
        """
        Index document

        Args:
            index_name: index name
            document: bytes
            request_id: request id
            session_id: session id
        """
        if isinstance(document, dict):
            document = json.dumps(document).encode()
        return await self.stubs['index_api'].index_document(
            index_service_pb.IndexDocumentRequest(
                index_name=index_name,
                document=document,
            ),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def search(
        self,
        index_alias: str,
        query: search_service_pb.Query,
        collectors: Union[search_service_pb.Collector, List[search_service_pb.Collector]],
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> search_service_pb.SearchResponse:
        """
        Search request

        Args:
            index_alias: index alias
            query: structured `Query`
            collectors:
            request_id: request id
            session_id: session id
        """
        if not isinstance(collectors, List):
            collectors = [collectors]
        return await self.stubs['search_api'].search(
            search_service_pb.SearchRequest(
                index_alias=index_alias,
                query=query,
                collectors=collectors
            ),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def merge_segments(
        self,
        index_name: str,
        segment_ids: List[str],
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.MergeSegmentsResponse:
        """
        Merge a list of segments into a single one

        Args:
            index_name: index name
            segment_ids: segment ids
            request_id: request id
            session_id: session id
        """
        return await self.stubs['index_api'].merge_segments(
            index_service_pb.MergeSegmentsRequest(index_name=index_name, segment_ids=segment_ids),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def set_index_alias(
        self,
        index_alias: str,
        index_name: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.SetIndexAliasResponse:
        """
        Set or reassign the alias for an index

        Args:
            index_alias: index alias
            index_name: index name
            request_id: request id
            session_id: session id
        """
        return await self.stubs['index_api'].set_index_alias(
            index_service_pb.SetIndexAliasRequest(index_alias=index_alias, index_name=index_name),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def vacuum_index(
        self,
        index_name: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.VacuumIndexResponse:
        """
        Vacuuming index

        Args:
            index_name: index name
            request_id: request id
            session_id: session id
        """
        return await self.stubs['index_api'].vacuum_index(
            index_service_pb.VacuumIndexRequest(index_name=index_name),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )

    @expose
    async def get_top_terms(
        self,
        index_name: str,
        field_name: str,
        top_k: int,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> index_service_pb.VacuumIndexResponse:
        """
        Vacuuming index

        Args:
            index_name: index name
            field_name: field name
            top_k: extract top-K terms
        """
        return await self.stubs['reflection_api'].get_top_terms(
            reflection_service_pb.GetTopTermsRequest(
                index_name=index_name,
                field_name=field_name,
                top_k=top_k,
            ),
            metadata=(('request-id', request_id), ('session-id', session_id)),
        )
