# Internal Communication System

## Overview

The Internal Communication System provides comprehensive real-time messaging and collaboration capabilities for Virtual Business Simulation. This feature enables realistic workplace communication with direct messaging, team channels, announcements, notifications, message threading, search functionality, and communication analytics.

## Core Features

### 1. Multi-Channel Communication
- **Direct Messages**: Private 1-to-1 conversations between employees
- **Team Channels**: Department and project-based group communication
- **Public Channels**: Company-wide discussion and collaboration spaces
- **Announcement Channels**: Official company communications and updates
- **Thread Management**: Organized conversation threading and reply tracking

### 2. Real-time Messaging
- **Instant Delivery**: Real-time message transmission and notifications
- **Read Receipts**: Message delivery and read status tracking
- **Typing Indicators**: Live typing status for active conversations
- **Presence Status**: Online/offline/away status management
- **Message Reactions**: Emoji reactions and engagement indicators

### 3. Advanced Search and Discovery
- **Full-text Search**: Comprehensive message content search across all accessible channels
- **Filter Options**: Search by sender, date range, channel, and message type
- **Keyword Indexing**: Intelligent keyword extraction and search optimization
- **Message History**: Complete conversation history and archival
- **Content Categories**: Organized search by content type and context

### 4. Notification Management
- **Smart Notifications**: Context-aware notification delivery and prioritization
- **Mention Alerts**: @username mentions with automatic notification
- **Channel Subscriptions**: Customizable notification preferences per channel
- **Mobile Integration**: Cross-platform notification support
- **Do Not Disturb**: Focus time and notification suppression controls

### 5. Communication Analytics
- **Usage Patterns**: Individual and team communication behavior analysis
- **Response Times**: Average response time tracking and optimization
- **Channel Activity**: Message volume and engagement metrics per channel
- **Collaboration Insights**: Cross-team communication and collaboration patterns
- **Peak Hours**: Optimal communication timing and availability analysis

## Technical Implementation

### Key Components

#### InternalCommunicationSystem Class
```python
class InternalCommunicationSystem:
    async def send_message(sender_id: str, content: str, recipient_ids: List[str] = None, channel_id: str = None) -> Optional[str]
    async def create_channel(name: str, channel_type: ChannelType, description: str = "", created_by: str = "system") -> str
    async def reply_to_message(sender_id: str, original_message_id: str, content: str) -> Optional[str]
    async def send_announcement(sender_id: str, title: str, content: str, target_audience: str = "all") -> Optional[str]
    async def search_messages(query: str, user_id: str, channel_id: str = None, date_range: Tuple[datetime, datetime] = None) -> List[Message]
```

#### Message Management
```python
@dataclass
class Message:
    message_id: str
    sender_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    recipient_ids: List[str] = field(default_factory=list)
    channel_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    
    def mark_as_read(self, user_id: str)
    def add_reaction(self, user_id: str, emoji: str)
    def get_engagement_score(self) -> float
```

#### Channel Architecture
```python
@dataclass
class CommunicationChannel:
    channel_id: str
    name: str
    channel_type: ChannelType
    description: str
    members: Set[str] = field(default_factory=set)
    admins: Set[str] = field(default_factory=set)
    message_ids: List[str] = field(default_factory=list)
    
    def add_member(self, user_id: str)
    def is_member(self, user_id: str) -> bool
    def is_admin(self, user_id: str) -> bool
```

#### Notification System
```python
@dataclass
class Notification:
    notification_id: str
    user_id: str
    notification_type: NotificationType
    title: str
    content: str
    timestamp: datetime
    is_read: bool = False
    
    def mark_as_read(self)
```

## Usage Examples

### Direct Messaging
```python
from tinytroupe.internal_communication import InternalCommunicationSystem, MessageType, MessagePriority

# Initialize communication system
comm_system = InternalCommunicationSystem(task_manager, hiring_database)

# Send direct message
message_id = await comm_system.send_message(
    sender_id="alice_001",
    content="Hi Bob, I've completed the authentication module. Ready for code review.",
    recipient_ids=["bob_002"],
    message_type=MessageType.DIRECT_MESSAGE,
    priority=MessagePriority.NORMAL
)

if message_id:
    print(f"Message sent: {message_id}")

# Reply to message
reply_id = await comm_system.reply_to_message(
    sender_id="bob_002",
    original_message_id=message_id,
    content="Great work! I'll review it this afternoon. Please ensure all tests are passing."
)

if reply_id:
    print(f"Reply sent: {reply_id}")
```

### Team Channel Communication
```python
# Create project channel
project_channel_id = await comm_system.create_channel(
    name="Authentication Project",
    channel_type=ChannelType.PROJECT,
    description="Discussion for authentication system implementation",
    created_by="bob_002",
    initial_members=["alice_001", "eve_005"]
)

print(f"Created project channel: {project_channel_id}")

# Post to channel with user mention
channel_msg_id = await comm_system.send_message(
    sender_id="alice_001",
    content="I've pushed the latest changes to the auth-feature branch. @EvenChen could you run the security tests?",
    channel_id=project_channel_id,
    message_type=MessageType.CHANNEL_MESSAGE
)

if channel_msg_id:
    print(f"Channel message posted: {channel_msg_id}")
    
    # Check if user was mentioned
    message = comm_system.messages[channel_msg_id]
    if "eve_005" in message.mentioned_users:
        print("Eve was mentioned and will receive notification")
```

### Company Announcements
```python
# Send company-wide announcement
announcement_id = await comm_system.send_announcement(
    sender_id="ceo_001",
    title="Q4 Company Update", 
    content="Team, I'm excited to share that we've exceeded our Q3 targets by 20%. Let's keep up the momentum!",
    priority=MessagePriority.HIGH,
    target_audience="all"
)

if announcement_id:
    print(f"Company announcement sent: {announcement_id}")

# Send department-specific announcement
dept_announcement_id = await comm_system.send_announcement(
    sender_id="bob_002",
    title="Engineering Team Meeting",
    content="All engineering team members, please attend the architecture review meeting on Friday at 2 PM.",
    priority=MessagePriority.NORMAL,
    target_audience="department:Engineering"
)

if dept_announcement_id:
    print(f"Department announcement sent: {dept_announcement_id}")
```

### Message Search and Discovery
```python
# Search for authentication-related messages
search_results = await comm_system.search_messages(
    query="authentication",
    user_id="alice_001"
)

print(f"Found {len(search_results)} messages about authentication")
for msg in search_results[:3]:
    sender_name = comm_system.hiring_database.employees[msg.sender_id].name
    print(f"  - From {sender_name}: {msg.content[:50]}...")

# Search in specific channel
channel_search = await comm_system.search_messages(
    query="code review",
    user_id="bob_002",
    channel_id=project_channel_id
)

print(f"Found {len(channel_search)} messages about code review in project channel")

# Search with date range
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()

recent_messages = await comm_system.search_messages(
    query="",  # Empty query returns all accessible messages
    user_id="bob_002",
    date_range=(yesterday, today)
)

print(f"Messages from last 24 hours: {len(recent_messages)}")
```

### Notification Management
```python
# Get unread notifications
alice_notifications = await comm_system.get_user_notifications("alice_001", unread_only=True)

print(f"Alice has {len(alice_notifications)} unread notifications:")
for notif in alice_notifications[:5]:  # Show first 5
    print(f"  - {notif.title}")
    print(f"    Type: {notif.notification_type.value}")
    print(f"    From: {notif.sender_id}")
    print(f"    Time: {notif.timestamp.strftime('%H:%M')}")

# Mark messages as read
unread_messages = await comm_system.get_unread_messages("alice_001")
print(f"Alice has {len(unread_messages)} unread messages")

for msg in unread_messages[:3]:  # Mark first 3 as read
    await comm_system.mark_message_as_read("alice_001", msg.message_id)
    print(f"Marked message as read: {msg.message_id}")
```

### Message Threading and Conversations
```python
# Start discussion thread
discussion_id = await comm_system.send_message(
    sender_id="david_004",
    content="Team, we need to finalize the product roadmap for next quarter.",
    recipient_ids=["alice_001", "bob_002", "carol_003"],
    message_type=MessageType.DIRECT_MESSAGE
)

if discussion_id:
    print(f"Started discussion: {discussion_id}")
    
    # Multiple replies create thread
    alice_reply = await comm_system.reply_to_message(
        sender_id="alice_001",
        original_message_id=discussion_id,
        content="From engineering perspective, we should prioritize API improvements."
    )
    
    carol_reply = await comm_system.reply_to_message(
        sender_id="carol_003", 
        original_message_id=discussion_id,
        content="Marketing suggests focusing on user engagement features."
    )
    
    # Check thread structure
    thread_id = comm_system.messages[discussion_id].thread_id or discussion_id
    if thread_id in comm_system.threads:
        thread_messages = comm_system.threads[thread_id]
        print(f"Thread has {len(thread_messages)} messages")
```

### Communication Analytics
```python
# Get comprehensive communication analytics
analytics = await comm_system.get_communication_analytics(
    date_range=(date.today() - timedelta(days=30), date.today())
)

print(f"Communication Analytics (Last 30 days):")
print(f"  Total messages: {analytics['total_messages']}")
print(f"  Average read rate: {analytics['engagement_metrics']['average_read_rate']:.1f}%")

print("Message types:")
for msg_type, count in analytics['message_types'].items():
    print(f"  - {msg_type}: {count}")

print("Most active channels:")
sorted_channels = sorted(analytics['channel_activity'].items(), key=lambda x: x[1], reverse=True)
for channel, count in sorted_channels[:3]:
    print(f"  - {channel}: {count} messages")

print("Most active users:")
sorted_users = sorted(analytics['user_activity'].items(), key=lambda x: x[1], reverse=True)
for user, count in sorted_users[:3]:
    print(f"  - {user}: {count} messages")

# Department-specific analytics
eng_analytics = await comm_system.get_communication_analytics(
    department="Engineering",
    date_range=(date.today() - timedelta(days=7), date.today())
)

print(f"Engineering Communication (Last 7 days):")
print(f"  Messages: {eng_analytics['total_messages']}")
print(f"  Top collaborators: {len(eng_analytics['top_collaborators'])}")
```

### Message Reactions and Engagement
```python
# Create message with reactions
good_news_id = await comm_system.send_message(
    sender_id="ceo_001",
    content="Great news! We've just closed our Series B funding round!",
    recipient_ids=[emp_id for emp_id in comm_system.hiring_database.employees.keys()],
    message_type=MessageType.ANNOUNCEMENT,
    priority=MessagePriority.HIGH
)

if good_news_id:
    # Add reactions from team members
    message = comm_system.messages[good_news_id]
    message.add_reaction("alice_001", "🎉")
    message.add_reaction("bob_002", "🎉") 
    message.add_reaction("carol_003", "👏")
    message.add_reaction("david_004", "🚀")
    
    print("Message reactions:")
    for emoji, users in message.reactions.items():
        print(f"  {emoji}: {len(users)} reactions")
    
    # Calculate engagement
    engagement_score = message.get_engagement_score()
    print(f"Engagement score: {engagement_score:.2%}")
```

## Business Use Cases

### 1. Team Collaboration
- **Project Coordination**: Real-time project status updates and coordination
- **Knowledge Sharing**: Technical discussions and information exchange
- **Problem Solving**: Collaborative troubleshooting and solution development
- **Decision Making**: Group discussions and consensus building

### 2. Organizational Communication
- **Company Updates**: Leadership communication and strategic announcements
- **Policy Distribution**: HR policies and procedure dissemination
- **Event Coordination**: Company events and meeting organization
- **Culture Building**: Social interaction and team building activities

### 3. Customer and Stakeholder Engagement
- **Client Communication**: External stakeholder communication channels
- **Vendor Coordination**: Supplier and partner communication management
- **Support Channels**: Customer service and technical support conversations
- **Feedback Collection**: Customer and employee feedback gathering

### 4. Knowledge Management
- **Documentation**: Living documentation through conversation history
- **Training**: Onboarding and skills development discussions
- **Best Practices**: Sharing expertise and lessons learned
- **Innovation**: Idea sharing and collaborative innovation

## Integration with Other Systems

### Task Management
- Automatic task-related message threading
- Task status updates through communication channels
- Assignment notifications and deadline reminders
- Progress reports and milestone celebrations

### Daily Scheduling
- Meeting coordination and scheduling discussions
- Calendar integration with communication channels
- Schedule change notifications and coordination
- Availability sharing and coordination

### Resource Management
- Resource request and approval discussions
- Equipment booking and coordination
- Budget discussion and approval workflows
- Resource conflict resolution communication

### Performance Tracking
- Performance feedback delivery and discussion
- Goal progress sharing and celebration
- 360 feedback coordination and reminders
- Coaching and development conversations

## Advanced Features

### 1. Intelligent Message Routing
```python
# Smart message prioritization and routing
smart_routing = await comm_system.analyze_message_importance(
    message_content="URGENT: Production server is down",
    sender_id="alice_001",
    context="system_alert"
)

if smart_routing['priority'] == 'urgent':
    # Route to emergency response channel
    await comm_system.escalate_message(
        message_id=message_id,
        escalation_level="emergency",
        notify_roles=["cto", "engineering_manager", "devops_lead"]
    )
```

### 2. Communication Sentiment Analysis
```python
# Analyze team communication sentiment
sentiment_analysis = await comm_system.analyze_communication_sentiment(
    channel_id=project_channel_id,
    time_period_days=7
)

print(f"Channel sentiment analysis:")
print(f"  Overall sentiment: {sentiment_analysis['overall_sentiment']}")
print(f"  Positive indicators: {sentiment_analysis['positive_count']}")
print(f"  Negative indicators: {sentiment_analysis['negative_count']}")
print(f"  Team morale trend: {sentiment_analysis['morale_trend']}")
```

### 3. Automated Response Suggestions
```python
# Generate intelligent response suggestions
response_suggestions = await comm_system.generate_response_suggestions(
    message_id=discussion_id,
    user_id="bob_002",
    context="manager_response"
)

print("Suggested responses:")
for suggestion in response_suggestions['suggestions']:
    print(f"  - {suggestion['response']}")
    print(f"    Tone: {suggestion['tone']}")
    print(f"    Confidence: {suggestion['confidence']:.1f}%")
```

## Configuration Options

### Message Types and Priorities
```python
class MessageType(Enum):
    DIRECT_MESSAGE = "direct_message"
    CHANNEL_MESSAGE = "channel_message" 
    ANNOUNCEMENT = "announcement"
    TASK_UPDATE = "task_update"
    MEETING_NOTES = "meeting_notes"
    DOCUMENT_SHARE = "document_share"
    SYSTEM_ALERT = "system_alert"
    FEEDBACK = "feedback"

class MessagePriority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
```

### Channel Configuration
```python
# Configure channel types and permissions
CHANNEL_CONFIGURATION = {
    ChannelType.PUBLIC: {
        "auto_join": True,
        "message_retention_days": 365,
        "file_upload_limit_mb": 100
    },
    ChannelType.PRIVATE: {
        "invite_only": True,
        "message_retention_days": 180,
        "admin_approval_required": True
    },
    ChannelType.ANNOUNCEMENT: {
        "read_only_members": True,
        "pin_important_messages": True,
        "executive_only_posting": True
    }
}
```

### Notification Settings
```python
# Configure notification preferences
NOTIFICATION_SETTINGS = {
    "default_preferences": {
        "direct_messages": "immediate",
        "mentions": "immediate", 
        "channel_messages": "batched",
        "announcements": "immediate"
    },
    "quiet_hours": {
        "enabled": True,
        "start_time": "18:00",
        "end_time": "08:00"
    },
    "digest_settings": {
        "daily_digest": True,
        "weekly_summary": True
    }
}
```

## Metrics and KPIs

### Communication Efficiency
- **Response Time**: Average time between message and reply
- **Message Volume**: Daily/weekly message counts by channel and user
- **Read Rates**: Percentage of messages read within 24/48 hours
- **Engagement Score**: Reaction and interaction rates per message

### Collaboration Quality
- **Cross-team Communication**: Inter-departmental message frequency
- **Knowledge Sharing**: Documentation and expertise sharing rates
- **Problem Resolution**: Time from problem identification to solution
- **Decision Speed**: Time from discussion initiation to consensus

### System Performance
- **Message Delivery**: Real-time delivery success rates
- **Search Effectiveness**: Search result relevance and usage
- **Platform Adoption**: User engagement and feature utilization
- **Integration Success**: API usage and external system connectivity

## Testing

Comprehensive test coverage in `test_internal_communication.py`:

```bash
# Run internal communication tests
python test_internal_communication.py
```

### Test Scenarios
- ✅ Direct messaging between employees
- ✅ Channel creation and management
- ✅ Message threading and replies
- ✅ Announcement broadcasting
- ✅ Message search and filtering
- ✅ Notification delivery and management
- ✅ Communication analytics
- ✅ Message reactions and engagement

## Best Practices

### 1. Communication Etiquette
- **Clear Messages**: Write clear, concise, and actionable messages
- **Appropriate Channels**: Use correct channels for different types of communication
- **Response Timeliness**: Establish and maintain reasonable response time expectations
- **Professional Tone**: Maintain professional communication standards

### 2. Channel Management
- **Purpose-driven Channels**: Create channels with clear purposes and guidelines
- **Active Moderation**: Maintain channel relevance and prevent off-topic discussions
- **Archive Inactive Channels**: Regular cleanup of unused or outdated channels
- **Access Control**: Proper member management and permission settings

### 3. Information Security
- **Sensitive Information**: Avoid sharing confidential information in inappropriate channels
- **Access Reviews**: Regular review of channel membership and permissions
- **Data Retention**: Implement appropriate message retention and deletion policies
- **Compliance**: Ensure communication practices meet regulatory requirements

## Troubleshooting

### Common Issues

#### Message Delivery Problems
- Check user notification preferences and settings
- Verify channel membership and permissions
- Ensure network connectivity and system availability
- Review message size and attachment limitations

#### Search Functionality Issues
- Verify search index updates and synchronization
- Check search query syntax and filters
- Ensure proper user permissions for accessible content
- Review search performance and optimization

#### Notification Overload
- Adjust notification frequency and batching settings
- Implement smart notification filtering and prioritization
- Provide user controls for notification preferences
- Consider quiet hours and do-not-disturb features

## API Reference

### Core Methods

#### `send_message(sender_id, content, recipient_ids, channel_id, message_type, priority)`
Sends a message to specified recipients or channel with priority and type classification.

#### `create_channel(name, channel_type, description, created_by, initial_members)`
Creates a new communication channel with specified type and initial membership.

#### `reply_to_message(sender_id, original_message_id, content, attachments)`
Creates a threaded reply to an existing message with automatic thread management.

#### `send_announcement(sender_id, title, content, priority, target_audience)`
Broadcasts official announcements to specified audiences with high-priority delivery.

#### `search_messages(query, user_id, channel_id, date_range)`
Searches accessible messages with comprehensive filtering and ranking options.

This enhancement transforms the Virtual Business Simulation into a modern digital workplace with comprehensive communication capabilities that mirror contemporary collaboration platforms, enabling realistic workplace interaction patterns and communication dynamics.