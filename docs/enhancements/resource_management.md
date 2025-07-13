# Resource Management System

## Overview

The Resource Management System provides comprehensive tracking and allocation of business resources including budgets, equipment, software licenses, physical space, and personnel time. This feature enables realistic resource constraint simulation with conflict detection, approval workflows, and optimization recommendations.

## Core Features

### 1. Budget Management
- **Multi-Category Budgets**: Department, project, and cost center budgeting
- **Approval Workflows**: Configurable approval thresholds and processes
- **Real-time Tracking**: Live budget utilization and remaining amounts
- **Overrun Detection**: Automatic alerts for budget violations
- **Fiscal Period Support**: Quarterly and yearly budget cycles

### 2. Equipment and Asset Tracking
- **Inventory Management**: Complete asset lifecycle tracking
- **Allocation Scheduling**: Time-based equipment reservations
- **Maintenance Scheduling**: Planned maintenance and downtime
- **Utilization Analytics**: Equipment usage patterns and efficiency
- **Capacity Planning**: Optimal equipment allocation strategies

### 3. Space Management
- **Room Booking**: Conference room and workspace reservations
- **Occupancy Tracking**: Real-time space utilization
- **Conflict Resolution**: Automatic double-booking prevention
- **Space Analytics**: Usage patterns and optimization opportunities
- **Multi-location Support**: Distributed office management

### 4. Resource Optimization
- **Conflict Detection**: Real-time resource conflict identification
- **Allocation Recommendations**: AI-powered optimization suggestions
- **Cost Analysis**: Resource cost tracking and ROI calculation
- **Utilization Reports**: Detailed resource usage analytics
- **Capacity Forecasting**: Future resource need predictions

## Technical Implementation

### Key Components

#### ResourceManagementSystem Class
```python
class ResourceManagementSystem:
    async def create_resource(name: str, resource_type: ResourceType, total_capacity: float, unit: str) -> str
    async def allocate_resource(resource_id: str, allocated_to: str, allocated_amount: float, allocated_by: str) -> Optional[str]
    async def create_budget_category(name: str, department: str, total_budget: float, approval_threshold: float) -> str
    async def allocate_budget(category_id: str, amount: float, allocated_to: str, allocated_by: str) -> Optional[str]
    async def get_resource_utilization(resource_id: str = None, department: str = None) -> Dict[str, Any]
```

#### Resource Types and Management
```python
class ResourceType(Enum):
    BUDGET = "budget"
    TIME = "time"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    PERSONNEL = "personnel"
    SPACE = "space"

@dataclass
class Resource:
    resource_id: str
    name: str
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    unit: str
    unit_cost: float
    department: Optional[str] = None
    
    def get_utilization_percentage(self) -> float
    def is_available(self, required_amount: float) -> bool
```

#### Allocation and Tracking
```python
@dataclass
class ResourceAllocation:
    allocation_id: str
    resource_id: str
    allocated_to: str
    allocated_by: str
    allocated_amount: float
    start_date: datetime
    end_date: Optional[datetime] = None
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    status: AllocationStatus = AllocationStatus.PLANNED
```

## Usage Examples

### Creating and Managing Resources
```python
from tinytroupe.resource_management import ResourceManagementSystem, ResourceType

# Initialize resource management
resource_system = ResourceManagementSystem(task_manager, hiring_database)

# Create equipment resource
laptop_id = await resource_system.create_resource(
    name="MacBook Pro M3",
    resource_type=ResourceType.EQUIPMENT,
    total_capacity=5.0,  # 5 units available
    unit="units",
    unit_cost=3000.0,
    department="Engineering",
    description="High-performance development laptops"
)

print(f"Created laptop resource: {laptop_id}")

# Create software resource
software_id = await resource_system.create_resource(
    name="GitHub Enterprise",
    resource_type=ResourceType.SOFTWARE,
    total_capacity=100.0,  # 100 licenses
    unit="licenses",
    unit_cost=50.0,
    department="Engineering",
    description="Source code management licenses"
)

print(f"Created software resource: {software_id}")
```

### Budget Category Management
```python
# Create department budget
eng_budget_id = await resource_system.create_budget_category(
    name="Engineering",
    department="Engineering",
    total_budget=500000.0,
    approval_threshold=5000.0  # Amounts over $5k need approval
)

# Create project-specific budget
project_budget_id = await resource_system.create_budget_category(
    name="Project Alpha",
    department="Engineering",
    total_budget=75000.0,
    approval_threshold=10000.0
)

print(f"Created budgets: {eng_budget_id}, {project_budget_id}")
```

### Resource Allocation
```python
from datetime import datetime, timedelta

# Allocate laptops to a project
laptop_allocation = await resource_system.allocate_resource(
    resource_id=laptop_id,
    allocated_to="auth_project_task",
    allocated_amount=2.0,  # 2 laptops
    allocated_by="bob_002",
    start_date=datetime.now(),
    duration_days=14,
    purpose="Development work for authentication system"
)

if laptop_allocation:
    print(f"Allocated 2 laptops for 14 days: {laptop_allocation}")

# Allocate budget with approval workflow
budget_allocation = await resource_system.allocate_budget(
    category_id=project_budget_id,
    amount=15000.0,  # Above approval threshold
    allocated_to="marketing_campaign",
    allocated_by="carol_003",
    purpose="Q4 product launch campaign"
)

if budget_allocation:
    print(f"Budget allocation created: {budget_allocation}")
    
    # Approve the allocation
    approval_success = await resource_system.approve_allocation(
        allocation_id=budget_allocation,
        approved_by="ceo_001"
    )
    print(f"Allocation approved: {approval_success}")
```

### Resource Utilization Tracking
```python
# Get overall utilization
utilization = await resource_system.get_resource_utilization()

print(f"Resource Utilization Overview:")
print(f"  Total resources: {utilization['total_resources']}")
print(f"  Average utilization: {utilization['average_utilization']:.1f}%")

# High utilization resources (>80%)
if utilization['high_utilization']:
    print("High utilization resources:")
    for resource in utilization['high_utilization']:
        print(f"  - {resource['name']}: {resource['utilization']:.1f}%")

# By resource type
print("Utilization by type:")
for resource_type, data in utilization['by_type'].items():
    avg_util = data.get('average_utilization', 0)
    print(f"  {resource_type}: {data['count']} resources, {avg_util:.1f}% avg")

# Department-specific utilization
eng_utilization = await resource_system.get_resource_utilization(
    department="Engineering"
)
print(f"Engineering utilization: {eng_utilization['average_utilization']:.1f}%")
```

### Budget Status and Monitoring
```python
# Get comprehensive budget status
budget_status = await resource_system.get_budget_status()

print(f"Budget Status Overview:")
print(f"  Total budget: ${budget_status['total_budget']:,.2f}")
print(f"  Allocated: ${budget_status['allocated_budget']:,.2f}")
print(f"  Remaining: ${budget_status['remaining_budget']:,.2f}")

print("Budget categories:")
for category in budget_status['categories']:
    print(f"  - {category['name']} ({category['department']})")
    print(f"    Budget: ${category['total_budget']:,.2f}")
    print(f"    Utilization: {category['utilization_percentage']:.1f}%")

# Check for over-budget categories
if budget_status['over_budget_categories']:
    print("⚠️ Over-budget categories:")
    for category in budget_status['over_budget_categories']:
        print(f"  - {category['name']}: {category['utilization_percentage']:.1f}%")
```

### Conflict Detection and Resolution
```python
# Get current resource conflicts
conflicts = await resource_system.get_resource_conflicts(resolved=False)

print(f"Active resource conflicts: {len(conflicts)}")
for conflict in conflicts:
    print(f"  - {conflict.description}")
    print(f"    Type: {conflict.conflict_type.value}")
    print(f"    Severity: {conflict.severity}")
    print(f"    Resolution: {conflict.suggested_resolution}")

# Resolve a conflict
if conflicts:
    first_conflict = conflicts[0]
    resolution_success = await resource_system.resolve_conflict(
        conflict_id=first_conflict.conflict_id,
        resolved_by="bob_002",
        resolution_notes="Rescheduled conflicting allocation to next week"
    )
    print(f"Conflict resolved: {resolution_success}")
```

### Resource Lifecycle Management
```python
# Start using allocated resource
usage_started = await resource_system.start_resource_usage(laptop_allocation)
if usage_started:
    print("Resource usage started")

# Complete usage with actual cost tracking
actual_cost = 6500.0  # 30% cost overrun
usage_completed = await resource_system.complete_resource_usage(
    laptop_allocation,
    actual_cost=actual_cost
)

if usage_completed:
    allocation = resource_system.allocations[laptop_allocation]
    print(f"Resource usage completed:")
    print(f"  Estimated cost: ${allocation.estimated_cost:,.2f}")
    print(f"  Actual cost: ${allocation.actual_cost:,.2f}")
    
    if allocation.is_overrun():
        overrun = allocation.actual_cost - allocation.estimated_cost
        overrun_pct = (overrun / allocation.estimated_cost) * 100
        print(f"  ⚠️ Cost overrun: ${overrun:,.2f} ({overrun_pct:.1f}%)")
```

### Optimization Recommendations
```python
# Get AI-powered optimization recommendations
recommendations = await resource_system.generate_resource_recommendations()

print(f"Resource Optimization Recommendations: {len(recommendations)}")

for rec in recommendations:
    priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    emoji = priority_emoji.get(rec['priority'], "⚪")
    
    print(f"{emoji} {rec['recommendation']}")
    print(f"   Type: {rec['type']}")
    print(f"   Priority: {rec['priority']}")
    print(f"   Impact: {rec['impact']}")
```

## Business Use Cases

### 1. Project Resource Planning
- **Budget Allocation**: Assign budgets to projects with tracking and controls
- **Equipment Planning**: Reserve necessary equipment for project phases
- **Team Scheduling**: Allocate personnel time across multiple projects
- **Space Requirements**: Book meeting rooms and workspaces for project activities

### 2. Department Management
- **Budget Control**: Monitor department spending against allocated budgets
- **Asset Utilization**: Track equipment usage and identify optimization opportunities
- **Space Optimization**: Analyze office space usage and optimize layouts
- **Cost Center Analysis**: Understand true cost of department operations

### 3. Capacity Planning
- **Resource Forecasting**: Predict future resource needs based on project pipeline
- **Bottleneck Identification**: Identify resource constraints limiting productivity
- **Investment Planning**: Data-driven decisions for equipment and software purchases
- **Growth Planning**: Resource scaling strategies for business expansion

### 4. Compliance and Governance
- **Approval Workflows**: Ensure proper authorization for resource expenditures
- **Audit Trails**: Complete tracking of resource allocation and usage
- **Policy Enforcement**: Automatic enforcement of budget and allocation policies
- **Risk Management**: Early warning systems for resource overruns and conflicts

## Integration with Other Systems

### Task Management
- Automatic resource allocation based on task requirements
- Resource availability constraints affect task scheduling
- Task completion triggers resource release
- Resource conflicts impact task timeline feasibility

### Daily Scheduling
- Resource booking integrated with employee schedules
- Meeting room reservations coordinate with calendar systems
- Equipment allocation aligns with work schedules
- Resource conflicts automatically adjust scheduling

### Performance Tracking
- Resource utilization metrics feed into performance evaluations
- Cost efficiency becomes part of employee assessments
- Resource optimization contributes to team performance scores
- ROI tracking for resource investments

### Internal Communication
- Automatic notifications for resource allocation changes
- Approval workflow communications
- Resource conflict alerts and resolution discussions
- Resource usage reports and recommendations sharing

## Advanced Features

### 1. Dynamic Resource Allocation
```python
# Smart allocation based on priority and availability
optimal_allocation = await resource_system.optimize_resource_allocation(
    resource_type=ResourceType.EQUIPMENT,
    requests=[
        {"task_id": "task_1", "priority": "high", "duration": 5},
        {"task_id": "task_2", "priority": "medium", "duration": 3},
        {"task_id": "task_3", "priority": "low", "duration": 2}
    ]
)
```

### 2. Predictive Analytics
```python
# Forecast future resource needs
forecast = await resource_system.forecast_resource_demand(
    resource_type=ResourceType.SOFTWARE,
    forecast_period_days=90,
    confidence_level=0.95
)

print(f"Predicted demand: {forecast['predicted_demand']}")
print(f"Confidence: {forecast['confidence_level']:.1%}")
print(f"Recommended action: {forecast['recommendation']}")
```

### 3. Cost Optimization
```python
# Analyze cost efficiency and optimization opportunities
cost_analysis = await resource_system.analyze_resource_costs(
    time_period_days=30,
    include_recommendations=True
)

print(f"Total resource costs: ${cost_analysis['total_cost']:,.2f}")
print(f"Cost per productive hour: ${cost_analysis['cost_per_hour']:.2f}")
print(f"Optimization potential: ${cost_analysis['savings_opportunity']:,.2f}")
```

## Configuration Options

### Resource Types
```python
# Configure available resource types
RESOURCE_TYPES = {
    ResourceType.EQUIPMENT: {
        "requires_physical_allocation": True,
        "supports_maintenance_windows": True,
        "default_allocation_duration": 7  # days
    },
    ResourceType.SOFTWARE: {
        "supports_concurrent_use": True,
        "license_tracking": True,
        "auto_renewal_alerts": True
    },
    ResourceType.SPACE: {
        "booking_granularity": "hourly",
        "advance_booking_limit": 30,  # days
        "cancellation_policy": "24_hours"
    }
}
```

### Approval Workflows
```python
# Configure approval hierarchies
APPROVAL_WORKFLOWS = {
    "budget_allocations": {
        "0-1000": "auto_approve",
        "1001-5000": "manager_approval",
        "5001-25000": "director_approval",
        "25000+": "executive_approval"
    },
    "equipment_allocation": {
        "standard": "auto_approve",
        "high_value": "manager_approval",
        "external_location": "director_approval"
    }
}
```

### Conflict Resolution Policies
```python
# Define conflict resolution strategies
CONFLICT_RESOLUTION = {
    "priority_override": True,  # High priority can override lower priority
    "first_come_first_served": False,
    "auto_suggest_alternatives": True,
    "escalation_timeout_hours": 24
}
```

## Metrics and KPIs

### Resource Efficiency
- **Utilization Rate**: Percentage of resource capacity actually used
- **Allocation Accuracy**: Planned vs. actual resource usage
- **Conflict Resolution Time**: Average time to resolve resource conflicts
- **Cost Variance**: Difference between estimated and actual resource costs

### Budget Performance
- **Budget Adherence**: Percentage of budgets staying within limits
- **Approval Efficiency**: Time from request to approval for budget allocations
- **Cost Per Project**: Average resource cost for completed projects
- **ROI Tracking**: Return on investment for resource expenditures

### Operational Metrics
- **Resource Availability**: Average availability of critical resources
- **Booking Efficiency**: Ratio of used to booked resource time
- **Maintenance Overhead**: Time lost to maintenance vs. productive use
- **Demand Forecasting Accuracy**: Precision of resource demand predictions

## Testing

Comprehensive test coverage in `test_resource_management.py`:

```bash
# Run resource management tests
python test_resource_management.py
```

### Test Scenarios
- ✅ Resource creation and configuration
- ✅ Budget category management
- ✅ Resource allocation with approval workflows
- ✅ Conflict detection and resolution
- ✅ Utilization analytics and reporting
- ✅ Cost tracking and overrun detection
- ✅ Optimization recommendations
- ✅ Integration with task management

## Best Practices

### 1. Resource Planning
- **Accurate Estimation**: Use historical data for resource requirement estimates
- **Buffer Management**: Include contingency resources for unexpected needs
- **Regular Reviews**: Periodically review and adjust resource allocations
- **Demand Forecasting**: Plan resource needs based on project pipeline

### 2. Budget Control
- **Clear Hierarchies**: Establish clear approval hierarchies and limits
- **Regular Monitoring**: Track budget utilization in real-time
- **Variance Analysis**: Investigate significant budget variances
- **Predictive Alerts**: Set up early warning systems for budget overruns

### 3. Conflict Management
- **Proactive Detection**: Implement early conflict detection systems
- **Quick Resolution**: Establish rapid conflict resolution processes
- **Alternative Planning**: Always have backup resource plans
- **Stakeholder Communication**: Keep affected parties informed of conflicts

## Troubleshooting

### Common Issues

#### Resource Allocation Failures
- Check resource availability and capacity
- Verify allocation permissions and approval requirements
- Ensure no conflicting allocations exist
- Validate resource type compatibility with request

#### Budget Overruns
- Review approval thresholds and workflow configuration
- Check for unauthorized allocations or approvals
- Verify cost calculation accuracy
- Investigate variance between estimated and actual costs

#### Conflict Resolution Delays
- Ensure conflict detection algorithms are running
- Check notification systems for approval workflows
- Verify escalation procedures and timeouts
- Review alternative resource availability

## API Reference

### Core Methods

#### `create_resource(name, resource_type, total_capacity, unit, unit_cost, department)`
Creates a new manageable resource with specified capacity and cost.

#### `allocate_resource(resource_id, allocated_to, allocated_amount, allocated_by, start_date, duration_days)`
Allocates a specified amount of resource for a defined period.

#### `create_budget_category(name, department, total_budget, approval_threshold)`
Establishes a budget category with spending controls and approval requirements.

#### `allocate_budget(category_id, amount, allocated_to, allocated_by, purpose)`
Allocates budget from a category with automatic approval workflow routing.

#### `get_resource_utilization(resource_id, department)`
Returns detailed utilization analytics for specified resources or departments.

This enhancement brings enterprise-level resource management to the Virtual Business Simulation, enabling realistic resource constraints, approval workflows, and optimization strategies that mirror real business operations.