from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select, func, or_
from sqlalchemy.types import String
import json
from flask import current_app

from app.core.models.domain.storage import APIStorage
from app.core.enums import StorageType
from app.core.models.responses.storage import (
    StorageEntryResponse, StorageListResponse,
    SimpleSessionListResponse, SessionListItemResponse,
    DetailedSessionListResponse, SessionWithEntriesResponse
)
from app.core.exceptions import APIError
from app.core.warnings import WarningCollector
from app.core.enums import WarningCode, WarningSeverity
from app.core.session import get_or_create_session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import cast
from datetime import timezone


class StorageService:
    """Service for handling data storage operations"""

    def __init__(self, db: Session):
        self.db = db

    def store_request(
        self,
        user_id: int,
        endpoint: str,
        request_data: Dict[str, Any],
        ttl_days: Optional[int] = None,
        compress: bool = False,
        metadata: Optional[Dict] = None
    ) -> APIStorage:
        """Store request data"""
        metadata = metadata or {}
        if 'session_id' not in metadata:
            metadata['session_id'] = get_or_create_session(user_id)

        storage = APIStorage(
            user_id=user_id,
            endpoint=endpoint,
            storage_type=StorageType.REQUEST,
            ttl=datetime.utcnow() + timedelta(days=ttl_days) if ttl_days else None,
            compressed=compress,
            storage_metadata=metadata
        )

        storage.request_data = storage.compress_data(request_data) if compress \
            else json.dumps(request_data).encode()

        self.db.add(storage)
        self.db.commit()

        current_app.logger.debug(
            f"Stored request for user {user_id} at endpoint '{endpoint}' "
            f"(compressed: {compress}, ttl: {storage.ttl}, "
            f"metadata: {storage.storage_metadata})"
        )
        return storage

    def store_response(
        self,
        user_id: int,
        endpoint: str,
        response_data: Dict[str, Any],
        ttl_days: Optional[int] = None,
        compress: bool = False,
        metadata: Optional[Dict] = None
    ) -> APIStorage:
        """Store response data"""
        metadata = metadata or {}
        if 'session_id' not in metadata:
            metadata['session_id'] = get_or_create_session(user_id)

        storage = APIStorage(
            user_id=user_id,
            endpoint=endpoint,
            storage_type=StorageType.RESPONSE,
            ttl=datetime.utcnow() + timedelta(days=ttl_days) if ttl_days else None,
            compressed=compress,
            storage_metadata=metadata
        )

        storage.response_data = storage.compress_data(response_data) if compress \
            else json.dumps(response_data).encode()

        self.db.add(storage)
        self.db.commit()

        current_app.logger.debug(
            f"Stored response for user {user_id} at endpoint '{endpoint}' "
            f"(compressed: {compress}, ttl: {storage.ttl}, "
            f"metadata: {storage.storage_metadata})"
        )
        return storage

    def query_storage(
        self,
        user_id: int,
        storage_type: Optional[StorageType] = None,
        endpoint: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,  # Add this parameter
        page: int = 1,
        page_size: int = 20
    ) -> StorageListResponse:
        """Query stored data with filters"""
        # Handle session_id by adding it to metadata_filters
        if session_id:
            metadata_filters = metadata_filters or {}
            if 'session_id' in metadata_filters and metadata_filters['session_id'] != session_id:
                WarningCollector.add_warning(
                    message="Both session_id parameter and metadata_filters['session_id'] provided. Using session_id parameter.",
                    code=WarningCode.PARAMETER_PRECEDENCE,
                    severity=WarningSeverity.LOW
                )
            metadata_filters['session_id'] = session_id

        filtered_entries = self._filter_storage_entries(
            user_id=user_id,
            endpoint=endpoint,
            start_date=start_date,
            end_date=end_date,
            storage_type=storage_type,
            metadata_filters=metadata_filters
        )

        # Calculate pagination
        total = len(filtered_entries)
        paginated_entries = filtered_entries[(page-1)*page_size:page*page_size]

        # Convert to response model
        items = [StorageEntryResponse.from_orm(
            entry) for entry in paginated_entries]

        return StorageListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=total > page * page_size
        )

    def delete_storage(
        self,
        user_id: int,
        storage_ids: List[int],
        force: bool = False
    ) -> int:
        """Delete storage entries"""
        query = select(APIStorage).where(
            APIStorage.user_id == user_id,
            APIStorage.id.in_(storage_ids)
        )

        if not force:
            # Only delete entries where TTL has expired
            query = query.where(
                or_(
                    APIStorage.ttl.is_(None),
                    APIStorage.ttl <= datetime.utcnow()
                )
            )

        entries = self.db.execute(query).scalars().all()
        for entry in entries:
            self.db.delete(entry)

        self.db.commit()
        return len(entries)

    def get_user_sessions(
        self,
        user_id: int,
        endpoint: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None,
        storage_type: Optional[StorageType] = None,
        metadata_filters: Dict[str, Any] = None,
        page: int = 1,
        page_size: int = 20,
        entries_per_session: Optional[int] = 20
    ) -> Dict[str, Any]:
        """
        Get user sessions with their request/response pairs.

        Args:
            user_id: ID of the user
            endpoint: Filter by endpoint
            start_date: Filter entries after this date
            end_date: Filter entries before this date
            session_id: Filter by specific session ID
            storage_type: Filter by request/response type
            metadata_filters: Additional metadata filters
            page: Page number for session pagination
            page_size: Number of sessions per page
            entries_per_session: Maximum number of entries to return per session
        """
        filtered_entries = self._filter_storage_entries(
            user_id=user_id,
            endpoint=endpoint,
            start_date=start_date,
            end_date=end_date,
            storage_type=storage_type,
            metadata_filters=metadata_filters
        )

        # Group entries by session_id and remove duplicates
        session_groups = {}
        for entry in filtered_entries:
            session_id = entry.storage_metadata.get('session_id')
            if not session_id:
                continue
            if session_id not in session_groups:
                # Use dict to prevent duplicates
                session_groups[session_id] = {}
            # Use ID as key to prevent duplicates
            session_groups[session_id][entry.id] = entry

        sessions = []
        for session_id, entries_dict in session_groups.items():
            entries = list(entries_dict.values())  # Convert back to list
            entries.sort(key=lambda x: x.created_at,
                         reverse=True)  # Sort by created_at

            total_entries = len(entries)
            shown_entries = entries[:entries_per_session] if entries_per_session else entries

            session = SessionWithEntriesResponse(
                session_id=session_id,
                user_id=user_id,
                created_at=min(e.created_at for e in entries),
                last_activity=max(e.created_at for e in entries),
                endpoints=list({e.endpoint for e in entries}),
                total_entries=total_entries,
                entries_shown=len(shown_entries),
                has_more_entries=entries_per_session and total_entries > entries_per_session,
                entries=[StorageEntryResponse.from_orm(
                    e) for e in shown_entries]
            )
            sessions.append(session)

        # Sort sessions by last activity
        sessions.sort(key=lambda x: x.last_activity, reverse=True)

        # Paginate sessions
        total_sessions = len(sessions)
        paginated_sessions = sessions[(page-1)*page_size:page*page_size]

        response = DetailedSessionListResponse(
            sessions=paginated_sessions,
            total=total_sessions,
            page=page,
            page_size=page_size,
            has_more=total_sessions > page * page_size
        )

        return response.model_dump()

    def _filter_storage_entries(
        self,
        user_id: int,
        endpoint: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        storage_type: Optional[StorageType] = None,
        session_id: Optional[str] = None,
        metadata_filters: Dict[str, Any] = None,
    ) -> List[APIStorage]:
        """Base function for filtering storage entries with detailed warnings"""
        # Handle session_id precedence
        if session_id and metadata_filters and 'session_id' in metadata_filters:
            WarningCollector.add_warning(
                message="Both session_id parameter and metadata_filters['session_id'] provided. Using session_id parameter.",
                code=WarningCode.PARAMETER_PRECEDENCE,
                severity=WarningSeverity.LOW
            )
            metadata_filters = {
                k: v for k, v in metadata_filters.items() if k != 'session_id'}

        # If session_id parameter is provided, add it to metadata filters
        if session_id:
            metadata_filters = metadata_filters or {}
            metadata_filters['session_id'] = session_id

        # Build base query with only basic filters
        query = select(APIStorage).where(APIStorage.user_id == user_id)
        base_entries = self.db.execute(query).scalars().all()

        if not base_entries:
            WarningCollector.add_warning(
                message="No storage entries found for this user",
                code=WarningCode.NO_RESULTS_FOUND,
                severity=WarningSeverity.MEDIUM
            )
            return []

        filtered_entries = base_entries
        initial_count = len(filtered_entries)

        # Track filter results
        filter_results = {}

        if storage_type:
            before_count = len(filtered_entries)
            filtered_entries = [
                e for e in filtered_entries if e.storage_type == storage_type]
            if not filtered_entries and before_count > 0:
                filter_results['storage_type'] = storage_type.value

        if endpoint:
            before_count = len(filtered_entries)
            endpoint_variations = self._normalize_endpoint(endpoint)

            # Try each endpoint variation
            matched_entries = []
            matched_variation = None

            for variation in endpoint_variations:
                current_matches = [
                    e for e in filtered_entries
                    if e.endpoint.strip('/ ').lower() == variation.strip('/ ')
                ]
                if current_matches:
                    matched_entries.extend(current_matches)
                    if not matched_variation:  # Keep track of first matching variation
                        matched_variation = variation

            if matched_entries:
                filtered_entries = matched_entries
                if matched_variation != endpoint:
                    WarningCollector.add_warning(
                        message="Found entries using normalized endpoint: '{}' (original: '{}')".format(
                            matched_variation, endpoint),
                        code=WarningCode.ENDPOINT_NORMALIZED,
                        severity=WarningSeverity.LOW
                    )
            elif before_count > 0:
                filter_results['endpoint'] = endpoint
                # Add more specific warning about tried variations
                WarningCollector.add_warning(
                    message="No entries found for endpoint '{}'. Tried variations: {}".format(
                        endpoint, ', '.join(endpoint_variations)),
                    code=WarningCode.NO_RESULTS_FOUND,
                    severity=WarningSeverity.LOW
                )

        if start_date or end_date:
            before_count = len(filtered_entries)
            if start_date:
                filtered_entries = [
                    e for e in filtered_entries
                    if e.created_at.replace(tzinfo=timezone.utc) >= start_date
                ]
            if end_date:
                # Only adjust to end of day if time wasn't specified (hour, minute, second all 0)
                if end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0:
                    end_date = end_date.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )
                filtered_entries = [
                    e for e in filtered_entries
                    if e.created_at.replace(tzinfo=timezone.utc) <= end_date
                ]
            if not filtered_entries and before_count > 0:
                if start_date and end_date:
                    date_range = "{} to {}".format(start_date, end_date)
                elif start_date:
                    date_range = "after {}".format(start_date)
                else:
                    date_range = "before {}".format(end_date)
                filter_results['date_range'] = date_range

        if metadata_filters:
            before_count = len(filtered_entries)
            filtered_entries = [
                entry for entry in filtered_entries
                if all(
                    entry.storage_metadata.get(key) == value
                    for key, value in metadata_filters.items()
                )
            ]
            if not filtered_entries and before_count > 0:
                filter_results['metadata'] = metadata_filters

        # Generate appropriate warning based on what filtered out results
        if not filtered_entries and filter_results:
            messages = []
            if 'storage_type' in filter_results:
                messages.append("storage type '{}'".format(
                    filter_results['storage_type']))
            if 'endpoint' in filter_results:
                messages.append("endpoint '{}'".format(
                    filter_results['endpoint']))
            if 'date_range' in filter_results:
                messages.append("date range {}".format(
                    filter_results['date_range']))
            if 'metadata' in filter_results:
                metadata_str = ', '.join("{}='{}'".format(k, v)
                                         for k, v in filter_results['metadata'].items())
                messages.append("metadata filters {}".format(metadata_str))

            warning_msg = "No entries found matching " + " and ".join(messages)

            WarningCollector.add_warning(
                message=warning_msg,
                code=WarningCode.NO_RESULTS_FOUND,
                severity=WarningSeverity.MEDIUM
            )

        return filtered_entries

    def list_user_sessions(
        self,
        user_id: int,
        endpoint: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None,
        storage_type: Optional[StorageType] = None,
        page: int = 1,
        page_size: int = 20,
        entries_per_session: Optional[int] = None
    ) -> Dict[str, Any]:
        """List user's storage sessions without entries."""
        metadata_filters = {'session_id': session_id} if session_id else None
        filtered_entries = self._filter_storage_entries(
            user_id=user_id,
            endpoint=endpoint,
            start_date=start_date,
            end_date=end_date,
            metadata_filters=metadata_filters
        )

        # Group entries by session_id
        session_groups = {}
        for entry in filtered_entries:
            session_id = entry.storage_metadata.get('session_id')
            if not session_id:
                continue
            if session_id not in session_groups:
                session_groups[session_id] = []
            session_groups[session_id].append(entry)

        # Create session responses
        sessions = []
        for session_id, entries in session_groups.items():
            session = SessionListItemResponse(
                session_id=session_id,
                user_id=user_id,
                created_at=min(e.created_at for e in entries),
                last_activity=max(e.created_at for e in entries),
                endpoints=list({e.endpoint for e in entries}),
                total_entries=len(entries),
                entries_shown=0,  # No entries in simple list
                has_more_entries=True if entries else False
            )
            sessions.append(session)

        # Sort and paginate
        sessions.sort(key=lambda x: x.last_activity, reverse=True)
        total = len(sessions)
        paginated_sessions = sessions[(page-1)*page_size:page*page_size]

        response = SimpleSessionListResponse(
            sessions=paginated_sessions,
            total=total,
            page=page,
            page_size=page_size,
            has_more=total > page * page_size
        )

        return response.model_dump()

    def _normalize_endpoint(self, endpoint: str) -> List[str]:
        """Normalize endpoint to try different variations"""
        from app.core.config import settings  # Import here to avoid circular imports

        if not endpoint:
            return []

        # Strip leading/trailing slashes and whitespace
        clean_endpoint = endpoint.strip('/ ').lower()

        # Get API version prefix from settings
        version_prefix = settings.API_VERSION_PREFIX

        # Generate variations
        variations = {
            f"/{clean_endpoint}",         # /health
            clean_endpoint,               # health
            f"/{version_prefix}/{clean_endpoint}",  # /v1/health
            f"{version_prefix}/{clean_endpoint}"    # v1/health
        }

        # If endpoint already starts with vX/, also add without version
        if any(clean_endpoint.startswith(f"{v}/") for v in [version_prefix, "v1", "v2"]):
            # Extract base endpoint after any version prefix
            base_endpoint = clean_endpoint.split(
                '/', 1)[1] if '/' in clean_endpoint else clean_endpoint
            variations.add(f"/{base_endpoint}")
            variations.add(base_endpoint)

        # Add debug log
        current_app.logger.debug(
            "Normalized endpoint '{}' to variations: {}".format(
                endpoint, variations)
        )

        return list(variations)
