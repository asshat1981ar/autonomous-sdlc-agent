#!/usr/bin/env python3
"""
A2A Shared Knowledge Management System
Enables agents to share, discover, and collaborate on knowledge
"""
import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    """Types of knowledge that can be shared"""
    CODE_PATTERN = "code_pattern"
    BEST_PRACTICE = "best_practice"
    SOLUTION = "solution"
    EXPERIENCE = "experience"
    TECHNIQUE = "technique"
    RESOURCE = "resource"
    LESSON_LEARNED = "lesson_learned"
    WORKFLOW = "workflow"
    TEMPLATE = "template"

class KnowledgeStatus(Enum):
    """Status of knowledge items"""
    DRAFT = "draft"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    CONFLICTED = "conflicted"

@dataclass
class KnowledgeItem:
    """A piece of knowledge that can be shared between agents"""
    id: str
    title: str
    description: str
    knowledge_type: KnowledgeType
    content: Dict[str, Any]
    creator_id: str
    created_at: float
    updated_at: float
    tags: List[str]
    confidence: float
    validation_count: int
    usage_count: int
    related_items: List[str]
    status: KnowledgeStatus
    version: int
    metadata: Dict[str, Any]

@dataclass
class KnowledgeQuery:
    """Query for knowledge discovery"""
    keywords: List[str]
    knowledge_types: List[KnowledgeType]
    tags: List[str]
    min_confidence: float
    max_results: int
    exclude_creators: List[str]

@dataclass
class KnowledgeValidation:
    """Validation of a knowledge item by an agent"""
    validator_id: str
    knowledge_id: str
    is_valid: bool
    confidence_score: float
    feedback: str
    timestamp: float

class SharedKnowledgeBase:
    """Shared knowledge base for A2A collaboration"""
    
    def __init__(self):
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.validations: Dict[str, List[KnowledgeValidation]] = {}
        self.access_log: List[Dict[str, Any]] = []
        self.knowledge_graph: Dict[str, Set[str]] = {}  # relationships
        
    def add_knowledge(self, creator_id: str, title: str, description: str,
                     knowledge_type: KnowledgeType, content: Dict[str, Any],
                     tags: List[str] = None, confidence: float = 0.8) -> str:
        """Add new knowledge item"""
        
        knowledge_id = str(uuid.uuid4())
        current_time = time.time()
        
        knowledge_item = KnowledgeItem(
            id=knowledge_id,
            title=title,
            description=description,
            knowledge_type=knowledge_type,
            content=content,
            creator_id=creator_id,
            created_at=current_time,
            updated_at=current_time,
            tags=tags or [],
            confidence=confidence,
            validation_count=0,
            usage_count=0,
            related_items=[],
            status=KnowledgeStatus.DRAFT,
            version=1,
            metadata={}
        )
        
        self.knowledge_items[knowledge_id] = knowledge_item
        self.validations[knowledge_id] = []
        
        # Initialize in knowledge graph
        self.knowledge_graph[knowledge_id] = set()
        
        # Auto-detect relationships
        self._detect_relationships(knowledge_id)
        
        logger.info(f"Added knowledge item: {title} by {creator_id}")
        return knowledge_id
    
    def query_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeItem]:
        """Query knowledge base"""
        
        results = []
        
        for item in self.knowledge_items.values():
            # Check knowledge type filter
            if query.knowledge_types and item.knowledge_type not in query.knowledge_types:
                continue
            
            # Check confidence threshold
            if item.confidence < query.min_confidence:
                continue
            
            # Check creator exclusion
            if item.creator_id in query.exclude_creators:
                continue
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance(item, query)
            
            if relevance_score > 0:
                results.append((item, relevance_score))
        
        # Sort by relevance and apply limit
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in results[:query.max_results]]
    
    def validate_knowledge(self, validator_id: str, knowledge_id: str,
                          is_valid: bool, confidence_score: float,
                          feedback: str = "") -> bool:
        """Validate a knowledge item"""
        
        if knowledge_id not in self.knowledge_items:
            return False
        
        validation = KnowledgeValidation(
            validator_id=validator_id,
            knowledge_id=knowledge_id,
            is_valid=is_valid,
            confidence_score=confidence_score,
            feedback=feedback,
            timestamp=time.time()
        )
        
        self.validations[knowledge_id].append(validation)
        
        # Update knowledge item
        item = self.knowledge_items[knowledge_id]
        item.validation_count += 1
        
        # Recalculate confidence based on validations
        validations = self.validations[knowledge_id]
        if validations:
            valid_validations = [v for v in validations if v.is_valid]
            item.confidence = len(valid_validations) / len(validations)
            
            # Update status based on validation consensus
            if len(validations) >= 3:  # Minimum validations for consensus
                if item.confidence >= 0.8:
                    item.status = KnowledgeStatus.VALIDATED
                elif item.confidence <= 0.3:
                    item.status = KnowledgeStatus.DEPRECATED
                else:
                    item.status = KnowledgeStatus.CONFLICTED
        
        item.updated_at = time.time()
        
        logger.info(f"Knowledge {knowledge_id} validated by {validator_id}: {is_valid}")
        return True
    
    def use_knowledge(self, user_id: str, knowledge_id: str) -> Optional[KnowledgeItem]:
        """Record usage of knowledge item"""
        
        if knowledge_id not in self.knowledge_items:
            return None
        
        item = self.knowledge_items[knowledge_id]
        item.usage_count += 1
        
        # Log access
        self.access_log.append({
            'user_id': user_id,
            'knowledge_id': knowledge_id,
            'action': 'use',
            'timestamp': time.time()
        })
        
        return item
    
    def get_related_knowledge(self, knowledge_id: str) -> List[KnowledgeItem]:
        """Get knowledge items related to the given item"""
        
        if knowledge_id not in self.knowledge_graph:
            return []
        
        related_ids = self.knowledge_graph[knowledge_id]
        return [self.knowledge_items[rid] for rid in related_ids if rid in self.knowledge_items]
    
    def add_relationship(self, knowledge_id1: str, knowledge_id2: str):
        """Add relationship between two knowledge items"""
        
        if knowledge_id1 in self.knowledge_graph and knowledge_id2 in self.knowledge_graph:
            self.knowledge_graph[knowledge_id1].add(knowledge_id2)
            self.knowledge_graph[knowledge_id2].add(knowledge_id1)
            
            # Update related_items in knowledge items
            if knowledge_id2 not in self.knowledge_items[knowledge_id1].related_items:
                self.knowledge_items[knowledge_id1].related_items.append(knowledge_id2)
            if knowledge_id1 not in self.knowledge_items[knowledge_id2].related_items:
                self.knowledge_items[knowledge_id2].related_items.append(knowledge_id1)
    
    def _calculate_relevance(self, item: KnowledgeItem, query: KnowledgeQuery) -> float:
        """Calculate relevance score for query"""
        
        score = 0.0
        
        # Keyword matching in title and description
        text_content = f"{item.title} {item.description}".lower()
        for keyword in query.keywords:
            if keyword.lower() in text_content:
                score += 1.0
        
        # Tag matching
        matching_tags = set(item.tags) & set(query.tags)
        score += len(matching_tags) * 0.5
        
        # Confidence factor
        score *= item.confidence
        
        # Usage popularity factor
        if item.usage_count > 0:
            score *= (1 + 0.1 * min(item.usage_count, 10))
        
        return score
    
    def _detect_relationships(self, new_knowledge_id: str):
        """Auto-detect relationships with existing knowledge"""
        
        new_item = self.knowledge_items[new_knowledge_id]
        
        for existing_id, existing_item in self.knowledge_items.items():
            if existing_id == new_knowledge_id:
                continue
            
            # Check for tag similarity
            common_tags = set(new_item.tags) & set(existing_item.tags)
            if len(common_tags) >= 2:
                self.add_relationship(new_knowledge_id, existing_id)
                continue
            
            # Check for content similarity (simplified)
            if new_item.knowledge_type == existing_item.knowledge_type:
                # Check for keyword overlap
                new_text = f"{new_item.title} {new_item.description}".lower()
                existing_text = f"{existing_item.title} {existing_item.description}".lower()
                
                new_words = set(new_text.split())
                existing_words = set(existing_text.split())
                
                overlap = len(new_words & existing_words)
                if overlap >= 3:
                    self.add_relationship(new_knowledge_id, existing_id)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        
        total_items = len(self.knowledge_items)
        
        # Count by type
        type_counts = {}
        for item in self.knowledge_items.values():
            type_name = item.knowledge_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Count by status
        status_counts = {}
        for item in self.knowledge_items.values():
            status_name = item.status.value
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(item.confidence for item in self.knowledge_items.values()) / max(total_items, 1)
        
        # Total validations
        total_validations = sum(len(validations) for validations in self.validations.values())
        
        return {
            'total_items': total_items,
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'average_confidence': avg_confidence,
            'total_validations': total_validations,
            'total_relationships': sum(len(rels) for rels in self.knowledge_graph.values()) // 2,
            'total_usage': sum(item.usage_count for item in self.knowledge_items.values())
        }

class KnowledgeAgent:
    """Agent mixin for knowledge management capabilities"""
    
    def __init__(self, agent_id: str, knowledge_base: SharedKnowledgeBase):
        self.agent_id = agent_id
        self.knowledge_base = knowledge_base
        self.personal_knowledge: Dict[str, Any] = {}
        self.knowledge_subscriptions: Set[KnowledgeType] = set()
    
    async def contribute_knowledge(self, title: str, description: str,
                                 knowledge_type: KnowledgeType,
                                 content: Dict[str, Any],
                                 tags: List[str] = None) -> str:
        """Contribute knowledge to shared knowledge base"""
        
        knowledge_id = self.knowledge_base.add_knowledge(
            creator_id=self.agent_id,
            title=title,
            description=description,
            knowledge_type=knowledge_type,
            content=content,
            tags=tags or []
        )
        
        logger.info(f"Agent {self.agent_id} contributed knowledge: {title}")
        return knowledge_id
    
    async def discover_knowledge(self, keywords: List[str],
                               knowledge_types: List[KnowledgeType] = None,
                               tags: List[str] = None) -> List[KnowledgeItem]:
        """Discover relevant knowledge"""
        
        query = KnowledgeQuery(
            keywords=keywords,
            knowledge_types=knowledge_types or list(KnowledgeType),
            tags=tags or [],
            min_confidence=0.5,
            max_results=10,
            exclude_creators=[self.agent_id]  # Exclude own contributions
        )
        
        results = self.knowledge_base.query_knowledge(query)
        
        # Record usage
        for item in results:
            self.knowledge_base.use_knowledge(self.agent_id, item.id)
        
        logger.info(f"Agent {self.agent_id} discovered {len(results)} knowledge items")
        return results
    
    async def validate_knowledge(self, knowledge_id: str, is_valid: bool,
                               confidence: float, feedback: str = "") -> bool:
        """Validate a knowledge item"""
        
        success = self.knowledge_base.validate_knowledge(
            validator_id=self.agent_id,
            knowledge_id=knowledge_id,
            is_valid=is_valid,
            confidence_score=confidence,
            feedback=feedback
        )
        
        if success:
            logger.info(f"Agent {self.agent_id} validated knowledge {knowledge_id}: {is_valid}")
        
        return success
    
    async def learn_from_experience(self, experience_title: str,
                                  situation: str, action: str, result: str,
                                  lesson: str, tags: List[str] = None) -> str:
        """Learn from experience and add to knowledge base"""
        
        experience_content = {
            'situation': situation,
            'action': action,
            'result': result,
            'lesson': lesson,
            'timestamp': time.time()
        }
        
        return await self.contribute_knowledge(
            title=experience_title,
            description=f"Experience learned: {lesson}",
            knowledge_type=KnowledgeType.EXPERIENCE,
            content=experience_content,
            tags=tags or ['experience', 'learning']
        )
    
    async def share_best_practice(self, practice_title: str,
                                description: str, implementation: Dict[str, Any],
                                benefits: List[str], tags: List[str] = None) -> str:
        """Share a best practice"""
        
        practice_content = {
            'implementation': implementation,
            'benefits': benefits,
            'applicability': 'general',
            'difficulty': 'medium'
        }
        
        return await self.contribute_knowledge(
            title=practice_title,
            description=description,
            knowledge_type=KnowledgeType.BEST_PRACTICE,
            content=practice_content,
            tags=tags or ['best_practice']
        )
    
    async def subscribe_to_knowledge_type(self, knowledge_type: KnowledgeType):
        """Subscribe to notifications for new knowledge of specific type"""
        self.knowledge_subscriptions.add(knowledge_type)
        logger.info(f"Agent {self.agent_id} subscribed to {knowledge_type.value}")
    
    def get_knowledge_contributions(self) -> List[KnowledgeItem]:
        """Get knowledge items contributed by this agent"""
        return [item for item in self.knowledge_base.knowledge_items.values()
                if item.creator_id == self.agent_id]

# Example usage and testing
async def demo_knowledge_system():
    """Demonstrate the knowledge management system"""
    print("🧠 A2A Knowledge Management System Demo")
    print("=" * 50)
    
    # Create shared knowledge base
    knowledge_base = SharedKnowledgeBase()
    
    # Create knowledge agents
    agent1 = KnowledgeAgent("dev_agent_001", knowledge_base)
    agent2 = KnowledgeAgent("test_agent_001", knowledge_base)
    agent3 = KnowledgeAgent("arch_agent_001", knowledge_base)
    
    print("✅ Created knowledge base and 3 agents")
    
    # Demo 1: Contribute knowledge
    print("\n📚 Demo 1: Contributing Knowledge")
    
    knowledge_id1 = await agent1.contribute_knowledge(
        title="Singleton Pattern in Python",
        description="Implementation of singleton pattern using metaclass",
        knowledge_type=KnowledgeType.CODE_PATTERN,
        content={
            'language': 'python',
            'code': 'class SingletonMeta(type): ...',
            'use_cases': ['database_connection', 'logging']
        },
        tags=['python', 'design_pattern', 'singleton']
    )
    
    knowledge_id2 = await agent2.share_best_practice(
        practice_title="Test-Driven Development",
        description="Best practices for implementing TDD",
        implementation={
            'steps': ['write_test', 'run_test', 'write_code', 'refactor'],
            'tools': ['pytest', 'unittest']
        },
        benefits=['better_code_quality', 'faster_debugging'],
        tags=['testing', 'tdd', 'methodology']
    )
    
    knowledge_id3 = await agent3.learn_from_experience(
        experience_title="Microservices Communication Failure",
        situation="Service A couldn't communicate with Service B",
        action="Implemented circuit breaker pattern",
        result="Improved system resilience",
        lesson="Always implement fallback mechanisms for service communication",
        tags=['microservices', 'resilience', 'circuit_breaker']
    )
    
    print(f"Added {len(knowledge_base.knowledge_items)} knowledge items")
    
    # Demo 2: Knowledge discovery
    print("\n🔍 Demo 2: Knowledge Discovery")
    
    discovered = await agent2.discover_knowledge(
        keywords=['pattern', 'python'],
        knowledge_types=[KnowledgeType.CODE_PATTERN, KnowledgeType.BEST_PRACTICE],
        tags=['python']
    )
    
    print(f"Agent 2 discovered {len(discovered)} relevant knowledge items:")
    for item in discovered:
        print(f"  - {item.title} (confidence: {item.confidence:.2f})")
    
    # Demo 3: Knowledge validation
    print("\n✅ Demo 3: Knowledge Validation")
    
    await agent2.validate_knowledge(knowledge_id1, True, 0.9, "Great implementation example")
    await agent3.validate_knowledge(knowledge_id1, True, 0.8, "Useful pattern")
    await agent1.validate_knowledge(knowledge_id2, True, 0.9, "Excellent TDD guide")
    
    # Demo 4: Knowledge relationships
    print("\n🔗 Demo 4: Knowledge Relationships")
    related = knowledge_base.get_related_knowledge(knowledge_id1)
    print(f"Found {len(related)} related knowledge items")
    
    # Demo 5: Knowledge statistics
    print("\n📊 Demo 5: Knowledge Statistics")
    stats = knowledge_base.get_knowledge_stats()
    print(f"Knowledge Base Stats:")
    print(f"  Total items: {stats['total_items']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")
    print(f"  Status distribution: {stats['status_distribution']}")
    print(f"  Total validations: {stats['total_validations']}")
    
    print("\n✅ Knowledge Management Demo Complete")

if __name__ == "__main__":
    asyncio.run(demo_knowledge_system())
