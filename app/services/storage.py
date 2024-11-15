from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select, func, or_
from sqlalchemy.types import String
import json
from app.models.core.storage import APIStorage
from app.models.enums import StorageType
from app.models.responses.storage import StorageEntryResponse, StorageListResponse, SimpleSessionListResponse, SessionListItemResponse
from app.core.exceptions import APIError
from app.core.warnings import WarningCollector, WarningCode, WarningSeverity
from flask import current_app
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
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get user sessions with their request/response pairs"""
        # Simply pass session_id to metadata_filters if provided
        if session_id:
            metadata_filters = metadata_filters or {}
            metadata_filters['session_id'] = session_id

        # Let _filter_storage_entries handle the warning logic
        filtered_entries = self._filter_storage_entries(
            user_id=user_id,
            endpoint=endpoint,
            start_date=start_date,
            end_date=end_date,
            storage_type=storage_type,
            metadata_filters=metadata_filters
        )

        # Group by session
        sessions = {}
        for entry in filtered_entries:
            session_id = entry.storage_metadata.get('session_id')
            if not session_id:
                continue

            if session_id not in sessions:
                sessions[session_id] = {
                    'session_id': session_id,
                    'created_at': entry.created_at,
                    'last_activity': entry.created_at,
                    'endpoints': {entry.endpoint},
                    'entries': []
                }

            sessions[session_id]['last_activity'] = max(
                sessions[session_id]['last_activity'],
                entry.created_at
            )
            sessions[session_id]['entries'].append(
                StorageEntryResponse.from_orm(entry)
            )

        # Convert to list and sort
        session_list = list(sessions.values())
        for session in session_list:
            session['endpoints'] = list(session['endpoints'])
            session['entries'].sort(key=lambda x: x.created_at, reverse=True)

        # Sort sessions by last_activity in reverse order
        session_list.sort(key=lambda x: x['last_activity'], reverse=True)

        return {
            'sessions': session_list[(page-1)*page_size:page*page_size],
            'total': len(session_list),
            'page': page,
            'page_size': page_size,
            'has_more': len(session_list) > page * page_size
        }

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
            filtered_entries = [
                e for e in filtered_entries if e.endpoint == endpoint]
            if not filtered_entries and before_count > 0:
                filter_results['endpoint'] = endpoint

        if start_date or end_date:
            before_count = len(filtered_entries)
            if start_date:
                filtered_entries = [
                    e for e in filtered_entries
                    if e.created_at.replace(tzinfo=timezone.utc) >= start_date
                ]
            if end_date:
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
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List user's storage sessions (simplified version)"""
        metadata_filters = {'session_id': session_id} if session_id else None
        filtered_entries = self._filter_storage_entries(
            user_id=user_id,
            endpoint=endpoint,
            start_date=start_date,
            end_date=end_date,
            metadata_filters=metadata_filters
        )

        # Group by session
        sessions = {}
        for entry in filtered_entries:
            session_id = entry.storage_metadata.get('session_id')
            if not session_id:
                continue

            if session_id not in sessions:
                sessions[session_id] = {
                    'session_id': session_id,
                    'user_id': user_id,
                    'created_at': entry.created_at,
                    'last_activity': entry.created_at,
                    'endpoints': set()  # Initialize as set for efficient unique additions
                }

            sessions[session_id]['last_activity'] = max(
                sessions[session_id]['last_activity'],
                entry.created_at
            )
            sessions[session_id]['endpoints'].add(entry.endpoint)

        # Convert to list and sort by last_activity
        session_list = []
        for session in sessions.values():
            # Convert set to list here before adding to response
            session['endpoints'] = list(session['endpoints'])
            session_list.append(session)

        session_list.sort(key=lambda x: x['last_activity'], reverse=True)

        # Add warning if no sessions found
        if not session_list:
            warning_msg = "No sessions found"
            if start_date or end_date:
                warning_msg += " in specified date range"
            WarningCollector.add_warning(
                message=warning_msg,
                code=WarningCode.NO_RESULTS_FOUND,
                severity=WarningSeverity.MEDIUM,
                priority=4
            )

        # Paginate
        total = len(session_list)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_sessions = session_list[start_idx:end_idx]

        return {
            'sessions': paginated_sessions,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': total > page * page_size
        }
