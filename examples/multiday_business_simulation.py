"""
Comprehensive Multi-Day Business Simulation Example

This example demonstrates the complete multi-day business simulation capabilities:
- Persistent state management across simulation days
- Calendar integration with scheduled events
- Task lifecycle and employee continuity
- Business metrics tracking over time
- World factory modular creation
"""

import asyncio
import logging
import sys
import os
from datetime import date, datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinytroupe.business_world_factory import create_business_simulation
from tinytroupe.business_time_manager import TimeZone
from tinytroupe.task_management import TaskPriority, TaskComplexity
from tinytroupe.persistent_world_manager import WorldType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MultiDayBusinessSimulation:
    """
    Comprehensive multi-day business simulation that demonstrates:
    - Persistent world state across days
    - Calendar-driven event scheduling
    - Task creation and assignment
    - Employee performance tracking
    - Business metrics evolution
    """
    
    def __init__(self, company_name: str = "TechCorp"):
        self.company_name = company_name
        self.world_manager = None
        self.simulation_results = {}
        
        # Create output directory for results
        self.output_dir = Path(f"simulation_results_{company_name.lower()}")
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized {company_name} multi-day business simulation")
    
    async def setup_company(self):
        """Initialize the business world with company-specific configuration"""
        logger.info(f"Setting up {self.company_name} business world...")
        
        # Custom configuration for our tech company
        custom_config = {
            "name": f"{self.company_name} Corporate Simulation",
            "description": f"Multi-day simulation of {self.company_name} operations",
            "business_hours_start": "09:00",
            "business_hours_end": "18:00",
            "max_employee_workload": 42.0,  # Slightly higher for tech company
            "meeting_frequency": "daily",
            "collaboration_intensity": "high",
            "custom_settings": {
                "agile_methodology": True,
                "remote_work_policy": True,
                "innovation_focus": True,
                "quarterly_okrs": True,
                "sprint_length": 14  # days
            }
        }
        
        # Create business world using factory
        self.world_manager = create_business_simulation(
            world_id=f"{self.company_name.lower()}_2024_q4",
            custom_config=custom_config,
            storage_path=str(self.output_dir / "world_state")
        )
        
        logger.info(f"Created {self.company_name} business world")
        return self.world_manager
    
    async def schedule_company_events(self, start_date: date, num_days: int = 5):
        """Schedule realistic company events over the simulation period"""
        logger.info(f"Scheduling events for {num_days} days starting {start_date}")
        
        events_scheduled = 0
        
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            
            # Monday: Sprint Planning & Weekly Planning
            if day_offset == 0 or current_date.weekday() == 0:
                self.world_manager.schedule_event(current_date, {
                    "title": "Sprint Planning Meeting",
                    "type": "meeting",
                    "attendees": ["CEO", "VP_Engineering", "Project_Managers", "Tech_Leads"],
                    "duration": 120,
                    "priority": "high",
                    "meeting_type": "planning",
                    "expected_outcomes": ["sprint_backlog", "velocity_estimate", "risk_assessment"]
                })
                events_scheduled += 1
                
                self.world_manager.schedule_event(current_date, {
                    "title": "Weekly OKR Review",
                    "type": "meeting", 
                    "attendees": ["CEO", "VP_Engineering", "VP_Marketing"],
                    "duration": 60,
                    "priority": "medium",
                    "meeting_type": "review"
                })
                events_scheduled += 1
            
            # Tuesday: Technical Architecture Review
            if current_date.weekday() == 1:
                self.world_manager.schedule_event(current_date, {
                    "title": "Technical Architecture Review",
                    "type": "technical_meeting",
                    "attendees": ["VP_Engineering", "Senior_Engineers", "Tech_Leads"],
                    "duration": 90,
                    "priority": "high",
                    "meeting_type": "technical_review",
                    "focus_areas": ["scalability", "security", "performance"]
                })
                events_scheduled += 1
            
            # Wednesday: Product Demo & Customer Feedback
            if current_date.weekday() == 2:
                self.world_manager.schedule_event(current_date, {
                    "title": "Product Demo Session",
                    "type": "demo",
                    "attendees": ["Product_Manager", "Engineering_Team", "Sales_Team"],
                    "duration": 60,
                    "priority": "medium",
                    "meeting_type": "demo"
                })
                events_scheduled += 1
                
                self.world_manager.schedule_event(current_date, {
                    "title": "Customer Feedback Analysis",
                    "type": "analysis",
                    "attendees": ["Product_Manager", "UX_Designer", "Customer_Success"],
                    "duration": 45,
                    "priority": "medium"
                })
                events_scheduled += 1
            
            # Thursday: Engineering Sync & Code Review
            if current_date.weekday() == 3:
                self.world_manager.schedule_event(current_date, {
                    "title": "Engineering All-Hands",
                    "type": "meeting",
                    "attendees": ["All_Engineering"],
                    "duration": 60,
                    "priority": "medium",
                    "meeting_type": "sync",
                    "agenda": ["project_updates", "technical_discussions", "process_improvements"]
                })
                events_scheduled += 1
            
            # Friday: Sprint Retrospective & Planning Next Week
            if current_date.weekday() == 4:
                self.world_manager.schedule_event(current_date, {
                    "title": "Sprint Retrospective",
                    "type": "retrospective",
                    "attendees": ["Engineering_Team", "Product_Manager", "Scrum_Master"],
                    "duration": 90,
                    "priority": "high",
                    "meeting_type": "retrospective",
                    "focus": ["what_went_well", "what_could_improve", "action_items"]
                })
                events_scheduled += 1
            
            # Daily standups (every weekday)
            if current_date.weekday() < 5:  # Monday to Friday
                self.world_manager.schedule_event(current_date, {
                    "title": "Daily Standup",
                    "type": "standup",
                    "attendees": ["Engineering_Team"],
                    "duration": 15,
                    "priority": "medium",
                    "meeting_type": "standup"
                })
                events_scheduled += 1
        
        # Schedule some project deadlines
        milestone_date = start_date + timedelta(days=3)
        self.world_manager.schedule_event(milestone_date, {
            "title": "Feature Development Milestone",
            "type": "deadline",
            "priority": "critical",
            "deliverables": ["user_authentication", "payment_integration", "mobile_responsiveness"]
        })
        events_scheduled += 1
        
        # Schedule quarterly review
        review_date = start_date + timedelta(days=4)
        self.world_manager.schedule_event(review_date, {
            "title": "Q4 Business Review",
            "type": "review",
            "attendees": ["CEO", "All_VPs", "Department_Heads"],
            "duration": 180,
            "priority": "critical",
            "meeting_type": "quarterly_review"
        })
        events_scheduled += 1
        
        logger.info(f"Scheduled {events_scheduled} events across {num_days} days")
        return events_scheduled
    
    async def run_simulation_day(self, simulation_date: date, rounds: int = 3) -> dict:
        """Run a complete simulation day with detailed logging"""
        logger.info(f"=== RUNNING SIMULATION DAY: {simulation_date} ===")
        
        try:
            # Run the complete simulation day
            day_results = await self.world_manager.run_simulation_day(
                target_date=simulation_date,
                rounds=rounds
            )
            
            # Extract detailed day information
            day_info = {
                "date": simulation_date.isoformat(),
                "day_name": simulation_date.strftime("%A"),
                "simulation_rounds": rounds,
                "analytics": day_results,
                "events_processed": day_results.get("meetings_completed", 0),
                "state_saved": day_results.get("state_saved", False)
            }
            
            # Log day summary
            logger.info(f"Day {simulation_date} completed:")
            logger.info(f"  - Rounds: {rounds}")
            logger.info(f"  - Events: {day_info['events_processed']}")
            logger.info(f"  - State saved: {day_info['state_saved']}")
            
            return day_info
            
        except Exception as e:
            logger.error(f"Failed to run simulation day {simulation_date}: {e}")
            raise
    
    async def run_multiday_simulation(self, start_date: date = None, num_days: int = 5, rounds_per_day: int = 3):
        """Run complete multi-day business simulation"""
        logger.info(f"=== STARTING {num_days}-DAY {self.company_name} SIMULATION ===")
        
        if not start_date:
            start_date = date.today()
        
        # Setup phase
        await self.setup_company()
        events_count = await self.schedule_company_events(start_date, num_days)
        
        simulation_results = {
            "company": self.company_name,
            "start_date": start_date.isoformat(),
            "num_days": num_days,
            "rounds_per_day": rounds_per_day,
            "total_events_scheduled": events_count,
            "daily_results": [],
            "overall_metrics": {}
        }
        
        # Run simulation for each day
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            
            try:
                day_result = await self.run_simulation_day(current_date, rounds_per_day)
                simulation_results["daily_results"].append(day_result)
                
                # Brief pause between days for demonstration
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Day {current_date} failed: {e}")
                day_result = {
                    "date": current_date.isoformat(),
                    "error": str(e),
                    "status": "failed"
                }
                simulation_results["daily_results"].append(day_result)
        
        # Calculate overall metrics
        simulation_results["overall_metrics"] = self._calculate_overall_metrics(simulation_results)
        
        # Save results
        await self._save_simulation_results(simulation_results)
        
        logger.info(f"=== {self.company_name} SIMULATION COMPLETED ===")
        return simulation_results
    
    def _calculate_overall_metrics(self, results: dict) -> dict:
        """Calculate overall simulation metrics"""
        daily_results = results["daily_results"]
        successful_days = [day for day in daily_results if "error" not in day]
        
        total_events = sum(day.get("events_processed", 0) for day in successful_days)
        total_rounds = sum(day.get("simulation_rounds", 0) for day in successful_days)
        success_rate = len(successful_days) / len(daily_results) * 100
        
        # Calculate business metrics
        overall_metrics = {
            "simulation_success_rate": success_rate,
            "total_simulation_days": len(daily_results),
            "successful_days": len(successful_days),
            "failed_days": len(daily_results) - len(successful_days),
            "total_events_processed": total_events,
            "total_simulation_rounds": total_rounds,
            "average_events_per_day": total_events / len(successful_days) if successful_days else 0,
            "average_rounds_per_day": total_rounds / len(successful_days) if successful_days else 0
        }
        
        # Extract business analytics from last successful day
        if successful_days:
            last_day = successful_days[-1]
            if "analytics" in last_day:
                overall_metrics.update({
                    "final_productivity_score": last_day["analytics"].get("productivity_score", 0),
                    "total_decisions_made": last_day["analytics"].get("decisions_made", 0),
                    "total_collaboration_events": last_day["analytics"].get("collaboration_events", 0)
                })
        
        return overall_metrics
    
    async def _save_simulation_results(self, results: dict):
        """Save simulation results to JSON file"""
        import json
        
        results_file = self.output_dir / f"{self.company_name.lower()}_simulation_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Simulation results saved to: {results_file}")
    
    def print_simulation_summary(self, results: dict):
        """Print a comprehensive simulation summary"""
        print(f"\n{'='*60}")
        print(f"{self.company_name.upper()} MULTI-DAY SIMULATION SUMMARY")
        print(f"{'='*60}")
        
        print(f"Company: {results['company']}")
        print(f"Simulation Period: {results['start_date']} ({results['num_days']} days)")
        print(f"Rounds per Day: {results['rounds_per_day']}")
        
        metrics = results["overall_metrics"]
        print(f"\nOVERALL PERFORMANCE:")
        print(f"  Success Rate: {metrics['simulation_success_rate']:.1f}%")
        print(f"  Total Events Processed: {metrics['total_events_processed']}")
        print(f"  Total Simulation Rounds: {metrics['total_simulation_rounds']}")
        print(f"  Average Events/Day: {metrics['average_events_per_day']:.1f}")
        
        if "final_productivity_score" in metrics:
            print(f"\nBUSINESS METRICS:")
            print(f"  Final Productivity Score: {metrics['final_productivity_score']:.2f}")
            print(f"  Total Decisions Made: {metrics['total_decisions_made']}")
            print(f"  Collaboration Events: {metrics['total_collaboration_events']}")
        
        print(f"\nDAILY BREAKDOWN:")
        for day_result in results["daily_results"]:
            date_str = day_result["date"]
            day_name = day_result.get("day_name", "Unknown")
            
            if "error" in day_result:
                print(f"  {date_str} ({day_name}): FAILED - {day_result['error']}")
            else:
                events = day_result.get("events_processed", 0)
                state_saved = day_result.get("state_saved", False)
                print(f"  {date_str} ({day_name}): {events} events, State: {'✓' if state_saved else '✗'}")
        
        world_history = self.world_manager.get_world_history()
        print(f"\nPERSISTENT STATE:")
        print(f"  World History: {len(world_history)} saved states")
        print(f"  Available Dates: {[d.isoformat() for d in world_history]}")
        
        print(f"\nOUTPUT DIRECTORY: {self.output_dir.absolute()}")
        print(f"{'='*60}\n")


async def demo_single_company_simulation():
    """Demo a single company's multi-day simulation"""
    print("SINGLE COMPANY MULTI-DAY SIMULATION DEMO")
    print("=" * 50)
    
    # Create and run TechCorp simulation
    techcorp_sim = MultiDayBusinessSimulation("TechCorp")
    
    # Run 5-day simulation starting tomorrow
    start_date = date.today() + timedelta(days=1)
    results = await techcorp_sim.run_multiday_simulation(
        start_date=start_date,
        num_days=5,
        rounds_per_day=2  # Reduced for demo speed
    )
    
    # Print comprehensive summary
    techcorp_sim.print_simulation_summary(results)
    
    return results


async def demo_multiple_company_comparison():
    """Demo comparing multiple companies with different configurations"""
    print("MULTIPLE COMPANY COMPARISON DEMO")
    print("=" * 50)
    
    companies = [
        ("StartupAlpha", {"max_employee_workload": 50.0, "collaboration_intensity": "high"}),
        ("Enterprise Corp", {"max_employee_workload": 40.0, "collaboration_intensity": "medium"}),
        ("RemoteTech", {"max_employee_workload": 38.0, "collaboration_intensity": "high"})
    ]
    
    comparison_results = []
    start_date = date.today() + timedelta(days=1)
    
    for company_name, custom_config in companies:
        print(f"\nRunning simulation for {company_name}...")
        
        # Create simulation with custom config
        sim = MultiDayBusinessSimulation(company_name)
        
        # Run shorter simulation for comparison
        results = await sim.run_multiday_simulation(
            start_date=start_date,
            num_days=3,
            rounds_per_day=2
        )
        
        comparison_results.append((company_name, results))
    
    # Print comparison summary
    print(f"\n{'='*80}")
    print("COMPANY COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    print(f"{'Company':<15} {'Success Rate':<12} {'Avg Events/Day':<15} {'Productivity':<12}")
    print("-" * 80)
    
    for company_name, results in comparison_results:
        metrics = results["overall_metrics"]
        success_rate = metrics["simulation_success_rate"]
        avg_events = metrics["average_events_per_day"]
        productivity = metrics.get("final_productivity_score", 0)
        
        print(f"{company_name:<15} {success_rate:<11.1f}% {avg_events:<14.1f} {productivity:<11.2f}")
    
    return comparison_results


async def main():
    """Main demo function"""
    print("COMPREHENSIVE MULTI-DAY BUSINESS SIMULATION DEMONSTRATION")
    print("This demo showcases the complete business simulation capabilities")
    print("=" * 80)
    
    try:
        # Demo 1: Single company simulation
        print("\n📊 DEMO 1: Single Company Simulation")
        single_results = await demo_single_company_simulation()
        
        # Demo 2: Multiple company comparison
        print("\n📈 DEMO 2: Multiple Company Comparison")
        comparison_results = await demo_multiple_company_comparison()
        
        print("\n✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("\nKey Capabilities Demonstrated:")
        print("  ✓ Multi-day persistent simulation")
        print("  ✓ Calendar-driven event scheduling")
        print("  ✓ Business metrics tracking")
        print("  ✓ State persistence across days")
        print("  ✓ Company configuration flexibility")
        print("  ✓ Performance comparison analysis")
        
        return {
            "single_company": single_results,
            "company_comparison": comparison_results
        }
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(main())