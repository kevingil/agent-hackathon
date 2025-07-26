"""
Database connection utilities for the MCP server.
This module provides standalone database connections without requiring the main app context.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlmodel import Session, create_engine, select, text
from sqlalchemy import func
import logging
import numpy as np

from ..mcp_config import mcp_settings

logger = logging.getLogger(__name__)

# Create engine for the MCP server (only if database config is available)
mcp_engine = None
if mcp_settings.DATABASE_URI:
    mcp_engine = create_engine(str(mcp_settings.DATABASE_URI))


def get_mcp_session():
    """Get a database session for the MCP server."""
    if not mcp_engine:
        raise RuntimeError(
            "Database not configured. Please set POSTGRES_USER, POSTGRES_PASSWORD, "
            "and POSTGRES_DB environment variables to use vector search tools."
        )
    return Session(mcp_engine)


class StoreService:
    """Service for performing database operations."""

    def __init__(self):
        if not mcp_engine:
            raise RuntimeError(
                "Database not configured. Please set POSTGRES_USER, POSTGRES_PASSWORD, "
                "and POSTGRES_DB environment variables to use vector search tools."
            )
        self.engine = mcp_engine

    async def search_keyword(
        self,
        query_embedding: List[float],
        session_id: Optional[uuid.UUID] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar code chunks using vector similarity.

        Args:
            query_embedding: The embedding vector to search for
            session_id: Optional session ID to filter results
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar code chunks with metadata
        """
        try:
            with get_mcp_session() as session:
                # Build the similarity search query dynamically to avoid parameter type issues
                if session_id:
                    query = text("""
                        SELECT 
                            cse.id,
                            cse.session_id,
                            cse.file_path,
                            cse.file_content,
                            cse.chunk_index,
                            cse.chunk_size,
                            cse.file_metadata,
                            cse.created_at,
                            css.name as session_name,
                            css.github_url,
                            1 - (cse.embedding_vector <=> :query_embedding) as similarity
                        FROM codesearchembedding cse
                        JOIN codesearchsession css ON cse.session_id = css.id
                        WHERE 
                            cse.session_id = :session_id_filter
                            AND cse.embedding_vector IS NOT NULL
                            AND (1 - (cse.embedding_vector <=> :query_embedding)) >= :similarity_threshold
                        ORDER BY cse.embedding_vector <=> :query_embedding
                        LIMIT :limit_val
                    """)

                    result = session.execute(
                        query,
                        {
                            "query_embedding": query_embedding,
                            "session_id_filter": str(session_id),
                            "similarity_threshold": similarity_threshold,
                            "limit_val": limit,
                        },
                    )
                else:
                    query = text("""
                        SELECT 
                            cse.id,
                            cse.session_id,
                            cse.file_path,
                            cse.file_content,
                            cse.chunk_index,
                            cse.chunk_size,
                            cse.file_metadata,
                            cse.created_at,
                            css.name as session_name,
                            css.github_url,
                            1 - (cse.embedding_vector <=> :query_embedding) as similarity
                        FROM codesearchembedding cse
                        JOIN codesearchsession css ON cse.session_id = css.id
                        WHERE 
                            cse.embedding_vector IS NOT NULL
                            AND (1 - (cse.embedding_vector <=> :query_embedding)) >= :similarity_threshold
                        ORDER BY cse.embedding_vector <=> :query_embedding
                        LIMIT :limit_val
                    """)

                    result = session.execute(
                        query,
                        {
                            "query_embedding": query_embedding,
                            "similarity_threshold": similarity_threshold,
                            "limit_val": limit,
                        },
                    )

                results = []
                for row in result:
                    results.append(
                        {
                            "id": str(row.id),
                            "session_id": str(row.session_id),
                            "session_name": row.session_name,
                            "github_url": row.github_url,
                            "file_path": row.file_path,
                            "file_content": row.file_content,
                            "chunk_index": row.chunk_index,
                            "chunk_size": row.chunk_size,
                            "file_metadata": row.file_metadata,
                            "similarity": float(row.similarity),
                            "created_at": row.created_at.isoformat(),
                        }
                    )

                return results

        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            raise

    async def add_to_cart(self) -> List[Dict[str, Any]]:
        """
        Get all sessions that have vector embeddings processed.

        Returns:
            List of sessions with embedding counts
        """
        try:
            with get_mcp_session() as session:
                query = text("""
                    SELECT 
                        css.id,
                        css.name,
                        css.github_url,
                        css.agent_type,
                        css.vector_embeddings_processed,
                        css.created_at,
                        css.updated_at,
                        css.last_used,
                        COUNT(cse.id) as embedding_count
                    FROM codesearchsession css
                    LEFT JOIN codesearchembedding cse ON css.id = cse.session_id
                    WHERE css.vector_embeddings_processed = true
                    GROUP BY css.id, css.name, css.github_url, css.agent_type, 
                             css.vector_embeddings_processed, css.created_at, 
                             css.updated_at, css.last_used
                    ORDER BY css.updated_at DESC
                """)

                result = session.execute(query)

                sessions = []
                for row in result:
                    sessions.append(
                        {
                            "id": str(row.id),
                            "name": row.name,
                            "github_url": row.github_url,
                            "agent_type": row.agent_type,
                            "vector_embeddings_processed": row.vector_embeddings_processed,
                            "embedding_count": row.embedding_count,
                            "created_at": row.created_at.isoformat(),
                            "updated_at": row.updated_at.isoformat(),
                            "last_used": row.last_used.isoformat(),
                        }
                    )

                return sessions

        except Exception as e:
            logger.error(f"Error getting sessions with embeddings: {e}")
            raise

    async def remove_from_cart(self) -> List[Dict[str, Any]]:
        """
        Get all sessions that have vector embeddings processed.

        Returns:
            List of sessions with embedding counts
        """
        try:
            with get_mcp_session() as session:
                query = text("""
                    SELECT 
                        css.id,
                        css.name,
                        css.github_url,
                        css.agent_type,
                        css.vector_embeddings_processed,
                        css.created_at,
                        css.updated_at,
                        css.last_used,
                        COUNT(cse.id) as embedding_count
                    FROM codesearchsession css
                    LEFT JOIN codesearchembedding cse ON css.id = cse.session_id
                    WHERE css.vector_embeddings_processed = true
                    GROUP BY css.id, css.name, css.github_url, css.agent_type, 
                             css.vector_embeddings_processed, css.created_at, 
                             css.updated_at, css.last_used
                    ORDER BY css.updated_at DESC
                """)

                result = session.execute(query)

                sessions = []
                for row in result:
                    sessions.append(
                        {
                            "id": str(row.id),
                            "name": row.name,
                            "github_url": row.github_url,
                            "agent_type": row.agent_type,
                            "vector_embeddings_processed": row.vector_embeddings_processed,
                            "embedding_count": row.embedding_count,
                            "created_at": row.created_at.isoformat(),
                            "updated_at": row.updated_at.isoformat(),
                            "last_used": row.last_used.isoformat(),
                        }
                    )

                return sessions

        except Exception as e:
            logger.error(f"Error getting sessions with embeddings: {e}")
            raise

    async def checkout_cart(self, session_id: uuid.UUID) -> List[Dict[str, Any]]:
        """ """
        pass

    async def get_session_cart(self, session_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get all files and their chunk information for a specific session.

        Args:
            session_id: The session ID to get files for

        Returns:
            List of files with chunk information
        """
        try:
            with get_mcp_session() as session:
                query = text("""
                    SELECT 
                        cse.file_path,
                        COUNT(*) as chunk_count,
                        SUM(cse.chunk_size) as total_content_size,
                        MAX(cse.created_at) as last_processed,
                        cse.file_metadata
                    FROM codesearchembedding cse
                    WHERE cse.session_id = :session_id
                    GROUP BY cse.file_path, cse.file_metadata
                    ORDER BY cse.file_path
                """)

                result = session.exec(query, {"session_id": str(session_id)})

                items = []
                for row in result:
                    items.append(
                        {
                            "part": row.part_name,
                            "part_description": row.part_description,
                            "part_id": row.part_id,
                            "date_added": row.date_added,
                        }
                    )

                return items

        except Exception as e:
            logger.error(f"Error getting session files: {e}")
            raise
