"""
Unit tests for Business Simulation components

Tests the core business simulation functionality including:
- AsyncBusinessEmployee creation and behavior
- HiringDatabase employee management
- BusinessSimulationWorld operations
"""

import pytest
import asyncio
import json
import tempfile
from datetime import datetime, time
from pathlib import Path

from tinytroupe.business_employee import AsyncBusinessEmployee, create_business_employee
from tinytroupe.business_simulation import HiringDatabase, BusinessEmployee
from tinytroupe.business_world import BusinessSimulationWorld


class TestAsyncBusinessEmployee:
    """Test AsyncBusinessEmployee functionality"""
    
    def test_business_employee_creation(self):
        """Test basic business employee creation"""
        employee = AsyncBusinessEmployee(
            name="Test Employee",
            employee_id="TEST001",
            role="Software Engineer",
            department="Engineering"
        )
        
        assert employee.name == "Test Employee"
        assert employee.employee_id == "TEST001"
        assert employee.role == "Software Engineer"
        assert employee.department == "Engineering"
        assert employee.manager_id is None
        assert employee.direct_reports == []
    
    def test_business_employee_with_manager(self):
        """Test business employee with manager relationship"""
        employee = AsyncBusinessEmployee(
            name="Junior Dev",
            employee_id="TEST002", 
            role="Junior Software Engineer",
            department="Engineering",
            manager_id="TEST001"
        )
        
        assert employee.manager_id == "TEST001"
    
    def test_direct_reports_management(self):
        """Test adding and removing direct reports"""
        manager = AsyncBusinessEmployee(
            name="Manager",
            employee_id="MGR001",
            role="Engineering Manager", 
            department="Engineering"
        )
        
        # Add direct reports
        manager.add_direct_report("EMP001")
        manager.add_direct_report("EMP002")
        
        assert len(manager.direct_reports) == 2
        assert "EMP001" in manager.direct_reports
        assert "EMP002" in manager.direct_reports
        
        # Remove direct report
        manager.remove_direct_report("EMP001")
        assert len(manager.direct_reports) == 1
        assert "EMP001" not in manager.direct_reports
    
    def test_business_skills_management(self):
        """Test business skill tracking"""
        employee = AsyncBusinessEmployee(
            name="Developer",
            employee_id="DEV001",
            role="Software Engineer",
            department="Engineering"
        )
        
        # Update skills
        employee.update_business_skill("coding", 8)
        employee.update_business_skill("leadership", 5)
        
        assert employee.business_skills["coding"] == 8
        assert employee.business_skills["leadership"] == 5
        
        # Test skill bounds
        employee.update_business_skill("coding", 15)  # Should cap at 10
        employee.update_business_skill("leadership", -5)  # Should floor at 1
        
        assert employee.business_skills["coding"] == 10
        assert employee.business_skills["leadership"] == 1
    
    def test_factory_function(self):
        """Test the create_business_employee factory function"""
        employee = create_business_employee(
            name="Factory Employee",
            employee_id="FAC001",
            role="Data Scientist",
            department="Analytics",
            occupation="You analyze data and build models.",
            personality_traits=["Analytical", "Detail-oriented"],
            professional_interests=["Machine Learning", "Statistics"],
            skills=["Python", "SQL", "Statistics"]
        )
        
        assert isinstance(employee, AsyncBusinessEmployee)
        assert employee.name == "Factory Employee"
        assert employee.role == "Data Scientist"
        assert employee.department == "Analytics"


class TestHiringDatabase:
    """Test HiringDatabase functionality"""
    
    @pytest.fixture
    def temp_employee_dir(self):
        """Create temporary directory with test employee files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test employee file
            employee_data = {
                "type": "BusinessEmployee",
                "persona": {
                    "name": "Test Employee",
                    "personality": {"traits": ["Collaborative", "Analytical"]},
                    "skills": ["Python", "Leadership"]
                },
                "business_properties": {
                    "employee_id": "TEST001",
                    "role": "Software Engineer",
                    "department": "Engineering",
                    "hire_date": "2023-01-15",
                    "manager_id": "MGR001",
                    "direct_reports": ["SUB001"],
                    "business_skills": {"coding": 8, "leadership": 6}
                }
            }
            
            employee_file = temp_path / "test_employee.employee.json"
            with open(employee_file, 'w') as f:
                json.dump(employee_data, f)
            
            yield str(temp_path)
    
    def test_hiring_database_creation(self, temp_employee_dir):
        """Test HiringDatabase creation and employee loading"""
        db = HiringDatabase(temp_employee_dir)
        
        assert len(db.employees) == 1
        assert "TEST001" in db.employees
        
        employee = db.employees["TEST001"]
        assert employee.name == "Test Employee"
        assert employee.role == "Software Engineer"
        assert employee.department == "Engineering"
        assert employee.manager_id == "MGR001"
    
    def test_organizational_chart_building(self, temp_employee_dir):
        """Test organizational chart construction"""
        db = HiringDatabase(temp_employee_dir)
        
        # Should have built org chart from employee data
        assert "MGR001" in db.organizational_chart
        assert "TEST001" in db.organizational_chart["MGR001"]
    
    @pytest.mark.asyncio
    async def test_agent_creation(self, temp_employee_dir):
        """Test creating agents from employee data"""
        db = HiringDatabase(temp_employee_dir)
        
        agent = await db.create_agent("TEST001")
        
        assert isinstance(agent, AsyncBusinessEmployee)
        assert agent.name == "Test Employee"
        assert agent.employee_id == "TEST001"
        assert agent.role == "Software Engineer"
        assert agent.department == "Engineering"
        assert agent.manager_id == "MGR001"
        assert agent.direct_reports == ["SUB001"]
        assert agent.business_skills == {"coding": 8, "leadership": 6}
    
    def test_employee_queries(self, temp_employee_dir):
        """Test various employee query methods"""
        db = HiringDatabase(temp_employee_dir)
        
        # Test get employee
        employee = db.get_employee("TEST001")
        assert employee is not None
        assert employee.name == "Test Employee"
        
        # Test get by department
        eng_employees = db.get_employees_by_department("Engineering")
        assert len(eng_employees) == 1
        assert eng_employees[0].employee_id == "TEST001"
        
        # Test get by role
        engineers = db.get_employees_by_role("Software Engineer")
        assert len(engineers) == 1
        assert engineers[0].employee_id == "TEST001"
        
        # Test get direct reports
        reports = db.get_direct_reports("MGR001")
        assert len(reports) == 1
        assert reports[0].employee_id == "TEST001"
    
    def test_department_analytics(self, temp_employee_dir):
        """Test department analytics calculation"""
        db = HiringDatabase(temp_employee_dir)
        
        analytics = db.get_department_analytics("Engineering")
        
        assert analytics["department"] == "Engineering"
        assert analytics["total_employees"] == 1
        assert "average_salary" in analytics
        assert "performance_distribution" in analytics
        assert "employees" in analytics
    
    def test_company_analytics(self, temp_employee_dir):
        """Test company-wide analytics"""
        db = HiringDatabase(temp_employee_dir)
        
        analytics = db.get_company_analytics()
        
        assert analytics["total_employees"] == 1
        assert "Engineering" in analytics["departments"]
        assert analytics["departments"]["Engineering"] == 1
        assert "total_salary_cost" in analytics
        assert "average_salary" in analytics


class TestBusinessSimulationWorld:
    """Test BusinessSimulationWorld functionality"""
    
    @pytest.fixture
    def sample_hiring_db(self, temp_employee_dir):
        """Create a sample hiring database for testing"""
        return HiringDatabase(temp_employee_dir)
    
    def test_business_world_creation(self, sample_hiring_db):
        """Test BusinessSimulationWorld creation"""
        world = BusinessSimulationWorld(
            name="Test Business World",
            hiring_database=sample_hiring_db,
            business_hours_start=time(9, 0),
            business_hours_end=time(17, 0)
        )
        
        assert world.name == "Test Business World"
        assert world.hiring_database == sample_hiring_db
        assert world.business_hours_start == time(9, 0)
        assert world.business_hours_end == time(17, 0)
        assert world.is_meeting is True  # Should enable meeting mode
    
    @pytest.mark.asyncio
    async def test_add_employee_to_world(self, sample_hiring_db):
        """Test adding employees to the business world"""
        world = BusinessSimulationWorld(hiring_database=sample_hiring_db)
        
        # Add employee by ID
        agent = await world.add_employee("TEST001")
        
        assert agent is not None
        assert isinstance(agent, AsyncBusinessEmployee)
        assert agent.employee_id == "TEST001"
        assert len(world.agents) == 1
    
    @pytest.mark.asyncio
    async def test_add_department_to_world(self, sample_hiring_db):
        """Test adding entire departments to the world"""
        world = BusinessSimulationWorld(hiring_database=sample_hiring_db)
        
        # Add Engineering department
        agents = await world.add_department("Engineering")
        
        assert len(agents) == 1
        assert agents[0].department == "Engineering"
        assert len(world.agents) == 1
    
    def test_business_analytics(self, sample_hiring_db):
        """Test business analytics generation"""
        world = BusinessSimulationWorld(hiring_database=sample_hiring_db)
        
        analytics = world.get_business_analytics()
        
        assert analytics["world_name"] == "Business Simulation"
        assert analytics["total_employees"] == 0  # No agents added yet
        assert "departments" in analytics
        assert "business_metrics" in analytics
        assert "business_hours" in analytics


# Integration test
@pytest.mark.asyncio
async def test_business_simulation_integration():
    """Integration test for complete business simulation workflow"""
    
    # Create temporary employee directory with test data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test employee
        employee_data = {
            "type": "BusinessEmployee",
            "persona": {
                "name": "Integration Test Employee",
                "occupation": {"description": "Software development and testing"},
                "personality": {"traits": ["Collaborative"]},
                "skills": ["Python", "Testing"]
            },
            "business_properties": {
                "employee_id": "INT001",
                "role": "Software Engineer", 
                "department": "Engineering",
                "hire_date": "2023-06-01",
                "business_skills": {"coding": 7}
            }
        }
        
        employee_file = temp_path / "integration_employee.employee.json"
        with open(employee_file, 'w') as f:
            json.dump(employee_data, f)
        
        # Create business simulation
        hiring_db = HiringDatabase(str(temp_path))
        world = BusinessSimulationWorld(
            name="Integration Test World",
            hiring_database=hiring_db
        )
        
        # Add employee to world
        agent = await world.add_employee("INT001")
        
        # Verify integration
        assert agent is not None
        assert agent.name == "Integration Test Employee"
        assert len(world.agents) == 1
        
        # Test business analytics
        analytics = world.get_business_analytics()
        assert analytics["total_employees"] == 1
        assert "Engineering" in analytics["departments"]


if __name__ == "__main__":
    pytest.main([__file__])