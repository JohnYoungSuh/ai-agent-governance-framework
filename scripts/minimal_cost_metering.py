#!/usr/bin/env python3
"""
Minimal Cost Metering

Purpose: Track resource usage and attribute costs to achieve 100% attribution

Logic:
  1. Collect usage metrics hourly
  2. Calculate costs (usage × rate)
  3. Attribute to cost-center and agent-id
  4. Generate monthly invoice
"""

import json
from datetime import datetime
from collections import defaultdict

# Rate card (example rates in USD)
RATES = {
    "cpu_per_second": 0.00005,
    "memory_per_gb_second": 0.00001,
    "storage_per_gb_hour": 0.0001
}


def get_resource_usage(resource):
    """
    Get usage metrics for a resource
    
    Args:
        resource: dict with metadata and usage
    
    Returns:
        dict: usage metrics
    """
    # In real implementation, query metrics API
    # This is a placeholder
    return {
        "cpu_seconds": resource.get("cpu_seconds", 0),
        "memory_gb_seconds": resource.get("memory_gb_seconds", 0),
        "storage_gb_hours": resource.get("storage_gb_hours", 0)
    }


def calculate_cost(usage):
    """
    Calculate cost from usage metrics
    
    Args:
        usage: dict with cpu_seconds, memory_gb_seconds, storage_gb_hours
    
    Returns:
        float: total cost in USD
    """
    cost = (
        usage["cpu_seconds"] * RATES["cpu_per_second"] +
        usage["memory_gb_seconds"] * RATES["memory_per_gb_second"] +
        usage["storage_gb_hours"] * RATES["storage_per_gb_hour"]
    )
    return cost


def meter_costs(resources):
    """
    Meter costs for all resources
    
    Args:
        resources: list of dicts with labels and usage
    
    Returns:
        dict: costs by cost-center and agent-id
    """
    costs = defaultdict(lambda: defaultdict(float))
    
    for resource in resources:
        # Get required tags
        cost_center = resource.get("labels", {}).get("cost-center")
        agent_id = resource.get("labels", {}).get("agent-id")
        
        # Skip resources without required tags (should be blocked by admission control)
        if not cost_center or not agent_id:
            print(f"WARNING: Resource {resource.get('name')} missing required tags")
            continue
        
        # Get usage
        usage = get_resource_usage(resource)
        
        # Calculate cost
        cost = calculate_cost(usage)
        
        # Attribute cost
        costs[cost_center][agent_id] += cost
    
    return costs


def generate_invoice(costs, month):
    """
    Generate monthly invoice
    
    Args:
        costs: dict of costs by cost-center and agent-id
        month: str (YYYY-MM)
    
    Returns:
        str: invoice in CSV format
    """
    lines = ["cost_center,agent_id,total_cost"]
    
    for cost_center, agents in costs.items():
        for agent_id, total_cost in agents.items():
            lines.append(f"{cost_center},{agent_id},{total_cost:.2f}")
    
    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    print("Minimal Cost Metering - Test\n")
    
    # Example resources
    resources = [
        {
            "name": "security-agent-pod-1",
            "labels": {
                "cost-center": "CC-1234",
                "agent-id": "security-agent"
            },
            "cpu_seconds": 3600,  # 1 hour
            "memory_gb_seconds": 7200,  # 2 GB for 1 hour
            "storage_gb_hours": 10  # 10 GB for 1 hour
        },
        {
            "name": "it-ops-agent-pod-1",
            "labels": {
                "cost-center": "CC-1234",
                "agent-id": "it-ops-agent"
            },
            "cpu_seconds": 7200,  # 2 hours
            "memory_gb_seconds": 14400,  # 4 GB for 1 hour
            "storage_gb_hours": 20  # 20 GB for 1 hour
        },
        {
            "name": "ai-agent-pod-1",
            "labels": {
                "cost-center": "CC-5678",
                "agent-id": "ai-agent"
            },
            "cpu_seconds": 1800,  # 30 minutes
            "memory_gb_seconds": 3600,  # 2 GB for 30 minutes
            "storage_gb_hours": 5  # 5 GB for 1 hour
        }
    ]
    
    # Meter costs
    costs = meter_costs(resources)
    
    # Display costs
    print("Cost Attribution:\n")
    for cost_center, agents in costs.items():
        print(f"Cost Center: {cost_center}")
        for agent_id, total_cost in agents.items():
            print(f"  {agent_id}: ${total_cost:.4f}")
        print()
    
    # Generate invoice
    month = datetime.now().strftime("%Y-%m")
    invoice = generate_invoice(costs, month)
    
    print(f"Invoice for {month}:\n")
    print(invoice)
    print()
    
    # Calculate attribution completeness
    total_resources = len(resources)
    attributed_resources = sum(1 for r in resources if r.get("labels", {}).get("cost-center"))
    attribution_pct = (attributed_resources / total_resources) * 100
    
    print(f"Attribution Completeness: {attribution_pct:.1f}%")
    print(f"  Total resources: {total_resources}")
    print(f"  Attributed: {attributed_resources}")
    print(f"  Missing tags: {total_resources - attributed_resources}")
