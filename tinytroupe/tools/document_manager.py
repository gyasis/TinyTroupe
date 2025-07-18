"""
Document Management System for TinyTroupe Present Feature

This module provides document storage, indexing, sharing, and template management
capabilities for the Present Feature.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

from tinytroupe.tools import logger
from tinytroupe.utils import JsonSerializableRegistry
import tinytroupe.utils as utils


@dataclass
class DocumentMetadata:
    """Metadata for a shared document."""
    document_id: str
    title: str
    author: str
    created_at: str
    modified_at: str
    doc_type: str  # "report", "memo", "summary", etc.
    format: str    # "markdown", "docx", "pdf", etc.
    tags: List[str]
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    access_permissions: Optional[Dict[str, str]] = None
    references: Optional[List[str]] = None
    tool_generated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class DocumentIndex:
    """Index for fast document search and retrieval."""
    
    def __init__(self):
        self.documents: Dict[str, DocumentMetadata] = {}
        self.author_index: Dict[str, List[str]] = {}
        self.tag_index: Dict[str, List[str]] = {}
        self.type_index: Dict[str, List[str]] = {}
    
    def add_document(self, metadata: DocumentMetadata):
        """Add a document to the index."""
        doc_id = metadata.document_id
        self.documents[doc_id] = metadata
        
        # Update author index
        author = metadata.author
        if author not in self.author_index:
            self.author_index[author] = []
        self.author_index[author].append(doc_id)
        
        # Update tag index
        for tag in metadata.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(doc_id)
        
        # Update type index
        doc_type = metadata.doc_type
        if doc_type not in self.type_index:
            self.type_index[doc_type] = []
        self.type_index[doc_type].append(doc_id)
        
        logger.debug(f"Added document {doc_id} to index")
    
    def remove_document(self, doc_id: str):
        """Remove a document from the index."""
        if doc_id not in self.documents:
            return
        
        metadata = self.documents[doc_id]
        
        # Remove from author index
        if metadata.author in self.author_index:
            self.author_index[metadata.author].remove(doc_id)
            if not self.author_index[metadata.author]:
                del self.author_index[metadata.author]
        
        # Remove from tag index
        for tag in metadata.tags:
            if tag in self.tag_index:
                self.tag_index[tag].remove(doc_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        
        # Remove from type index
        if metadata.doc_type in self.type_index:
            self.type_index[metadata.doc_type].remove(doc_id)
            if not self.type_index[metadata.doc_type]:
                del self.type_index[metadata.doc_type]
        
        # Remove from main index
        del self.documents[doc_id]
        
        logger.debug(f"Removed document {doc_id} from index")
    
    def search_by_author(self, author: str) -> List[str]:
        """Find all documents by a specific author."""
        return self.author_index.get(author, [])
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Find all documents with a specific tag."""
        return self.tag_index.get(tag, [])
    
    def search_by_type(self, doc_type: str) -> List[str]:
        """Find all documents of a specific type."""
        return self.type_index.get(doc_type, [])
    
    def search_by_title(self, title_query: str) -> List[str]:
        """Find documents with titles containing the query."""
        results = []
        query_lower = title_query.lower()
        
        for doc_id, metadata in self.documents.items():
            if query_lower in metadata.title.lower():
                results.append(doc_id)
        
        return results
    
    def get_all_documents(self) -> List[str]:
        """Get all document IDs."""
        return list(self.documents.keys())
    
    def get_metadata(self, doc_id: str) -> Optional[DocumentMetadata]:
        """Get metadata for a specific document."""
        return self.documents.get(doc_id)


class TemplateManager:
    """Manages document templates for consistent formatting."""
    
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            # Default to a templates directory within the TinyTroupe package
            self.templates_dir = Path(__file__).parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)
        
        self.templates_dir.mkdir(exist_ok=True)
        self.templates: Dict[str, str] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default templates for common document types."""
        
        # Compliance Report Template
        compliance_template = """# Compliance Report: {title}

**Author**: {author}  
**Date**: {date}  
**Report Type**: {report_type}

## Executive Summary
{executive_summary}

## Compliance Areas Reviewed
{compliance_areas}

## Findings
{findings}

## Recommendations
{recommendations}

## Next Steps
{next_steps}

---
*Generated by {tool_name} on {timestamp}*
"""
        
        # Technical Memo Template
        technical_memo_template = """# Technical Memo: {title}

**From**: {author}  
**Date**: {date}  
**Subject**: {subject}

## Overview
{overview}

## Technical Details
{technical_details}

## Implementation Plan
{implementation_plan}

## Risks and Considerations
{risks}

## Conclusion
{conclusion}

---
*Generated by {tool_name} on {timestamp}*
"""
        
        # Meeting Summary Template
        meeting_summary_template = """# Meeting Summary: {title}

**Date**: {date}  
**Attendees**: {attendees}  
**Duration**: {duration}

## Key Discussion Points
{discussion_points}

## Decisions Made
{decisions}

## Action Items
{action_items}

## Next Meeting
{next_meeting}

---
*Generated by {tool_name} on {timestamp}*
"""
        
        self.templates["compliance_report"] = compliance_template
        self.templates["technical_memo"] = technical_memo_template
        self.templates["meeting_summary"] = meeting_summary_template
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get a template by name."""
        return self.templates.get(template_name)
    
    def add_template(self, name: str, template_content: str):
        """Add or update a template."""
        self.templates[name] = template_content
        logger.debug(f"Added template: {name}")
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template with provided parameters."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Add default values
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = datetime.now().isoformat()
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template parameter: {e}")


class SharedDocumentRepository(JsonSerializableRegistry):
    """
    Central repository for storing and managing shared documents.
    
    Provides document storage, indexing, search, and access control
    for the Present Feature.
    """
    
    def __init__(self, storage_dir: str = None, templates_dir: str = None):
        if storage_dir is None:
            # Default to a documents directory in the current working directory
            self.storage_dir = Path.cwd() / "shared_documents"
        else:
            self.storage_dir = Path(storage_dir)
        
        self.storage_dir.mkdir(exist_ok=True)
        
        self.index = DocumentIndex()
        self.template_manager = TemplateManager(templates_dir)
        
        # Load existing documents from storage
        self._load_existing_documents()
    
    def _generate_document_id(self, title: str, author: str) -> str:
        """Generate a unique document ID."""
        timestamp = str(int(time.time()))
        content = f"{title}_{author}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate checksum for document content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _load_existing_documents(self):
        """Load metadata for existing documents in the storage directory."""
        metadata_file = self.storage_dir / "index.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    index_data = json.load(f)
                
                for doc_data in index_data.get('documents', []):
                    metadata = DocumentMetadata(**doc_data)
                    self.index.add_document(metadata)
                
                logger.info(f"Loaded {len(self.index.documents)} existing documents")
            except Exception as e:
                logger.error(f"Error loading existing documents: {e}")
    
    def _save_index(self):
        """Save the document index to disk."""
        metadata_file = self.storage_dir / "index.json"
        index_data = {
            "documents": [metadata.to_dict() for metadata in self.index.documents.values()],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def store_document(self, 
                      title: str, 
                      content: str, 
                      author: str,
                      doc_type: str = "document",
                      format: str = "markdown",
                      tags: List[str] = None,
                      template_name: str = None,
                      template_params: Dict[str, Any] = None,
                      tool_generated: str = None) -> str:
        """
        Store a document in the repository.
        
        Returns:
            str: The document ID
        """
        if tags is None:
            tags = []
        
        # Generate unique ID
        doc_id = self._generate_document_id(title, author)
        
        # Process content through template if specified
        if template_name and template_params:
            try:
                content = self.template_manager.render_template(template_name, **template_params)
            except Exception as e:
                logger.warning(f"Template rendering failed: {e}. Using raw content.")
        
        # Create file path
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{doc_id}_{safe_title}.{format}"
        file_path = self.storage_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create metadata
        now = datetime.now().isoformat()
        metadata = DocumentMetadata(
            document_id=doc_id,
            title=title,
            author=author,
            created_at=now,
            modified_at=now,
            doc_type=doc_type,
            format=format,
            tags=tags,
            file_path=str(file_path),
            size_bytes=len(content.encode('utf-8')),
            checksum=self._calculate_checksum(content),
            tool_generated=tool_generated
        )
        
        # Add to index
        self.index.add_document(metadata)
        self._save_index()
        
        logger.info(f"Stored document '{title}' with ID {doc_id}")
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID."""
        metadata = self.index.get_metadata(doc_id)
        if not metadata:
            return None
        
        if not metadata.file_path or not Path(metadata.file_path).exists():
            logger.error(f"Document file not found for ID {doc_id}")
            return None
        
        try:
            with open(metadata.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "metadata": metadata.to_dict(),
                "content": content
            }
        except Exception as e:
            logger.error(f"Error reading document {doc_id}: {e}")
            return None
    
    def search_documents(self, 
                        query: str = None,
                        author: str = None,
                        doc_type: str = None,
                        tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for documents based on various criteria.
        
        Returns list of document metadata dictionaries.
        """
        result_ids = set()
        
        # If no criteria specified, return all documents
        if not any([query, author, doc_type, tags]):
            result_ids = set(self.index.get_all_documents())
        else:
            # Search by different criteria and intersect results
            if author:
                result_ids.update(self.index.search_by_author(author))
            
            if doc_type:
                type_results = set(self.index.search_by_type(doc_type))
                if result_ids:
                    result_ids.intersection_update(type_results)
                else:
                    result_ids.update(type_results)
            
            if tags:
                for tag in tags:
                    tag_results = set(self.index.search_by_tag(tag))
                    if result_ids:
                        result_ids.intersection_update(tag_results)
                    else:
                        result_ids.update(tag_results)
            
            if query:
                title_results = set(self.index.search_by_title(query))
                if result_ids:
                    result_ids.intersection_update(title_results)
                else:
                    result_ids.update(title_results)
        
        # Return metadata for found documents
        results = []
        for doc_id in result_ids:
            metadata = self.index.get_metadata(doc_id)
            if metadata:
                results.append(metadata.to_dict())
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x['created_at'], reverse=True)
        
        return results
    
    def share_document(self, doc_id: str, recipient_agents: List[str], message: str = None) -> bool:
        """
        Share a document with specified agents.
        
        This creates a sharing record and could notify the agents in a full implementation.
        """
        metadata = self.index.get_metadata(doc_id)
        if not metadata:
            logger.error(f"Cannot share document {doc_id}: not found")
            return False
        
        # Create sharing record
        sharing_record = {
            "document_id": doc_id,
            "document_title": metadata.title,
            "shared_by": metadata.author,
            "shared_with": recipient_agents,
            "shared_at": datetime.now().isoformat(),
            "message": message
        }
        
        # Store sharing record
        sharing_file = self.storage_dir / "sharing_log.jsonl"
        with open(sharing_file, 'a') as f:
            f.write(json.dumps(sharing_record) + '\n')
        
        logger.info(f"Shared document {doc_id} with {recipient_agents}")
        return True
    
    def get_shared_documents(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all documents shared with a specific agent."""
        sharing_file = self.storage_dir / "sharing_log.jsonl"
        if not sharing_file.exists():
            return []
        
        shared_docs = []
        try:
            with open(sharing_file, 'r') as f:
                for line in f:
                    record = json.loads(line.strip())
                    if agent_name in record.get('shared_with', []):
                        shared_docs.append(record)
        except Exception as e:
            logger.error(f"Error reading sharing log: {e}")
        
        return shared_docs
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the repository."""
        metadata = self.index.get_metadata(doc_id)
        if not metadata:
            return False
        
        # Remove file
        if metadata.file_path and Path(metadata.file_path).exists():
            try:
                os.remove(metadata.file_path)
            except Exception as e:
                logger.error(f"Error deleting file {metadata.file_path}: {e}")
        
        # Remove from index
        self.index.remove_document(doc_id)
        self._save_index()
        
        logger.info(f"Deleted document {doc_id}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        total_docs = len(self.index.documents)
        
        # Count by type
        type_counts = {}
        for doc_type, doc_list in self.index.type_index.items():
            type_counts[doc_type] = len(doc_list)
        
        # Count by author
        author_counts = {}
        for author, doc_list in self.index.author_index.items():
            author_counts[author] = len(doc_list)
        
        return {
            "total_documents": total_docs,
            "by_type": type_counts,
            "by_author": author_counts,
            "available_templates": self.template_manager.list_templates()
        }


# Global repository instance
global_document_repository = SharedDocumentRepository()